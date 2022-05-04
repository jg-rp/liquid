"""Test cases for statically counting a template's variables."""
import asyncio

from typing import List, Optional, TextIO
from unittest import TestCase

from liquid import Environment
from liquid import DictLoader
from liquid import Template

from liquid.ast import ChildNode, Node
from liquid.context import Context
from liquid.exceptions import TemplateTraversalError
from liquid.expression import Expression
from liquid.mode import Mode
from liquid.stream import TokenStream
from liquid.tag import Tag
from liquid.template import BoundTemplate, Refs
from liquid.token import Token


class MockExpression(Expression):
    """Mock expression"""

    def evaluate(self, context: Context) -> object:
        return "mock expression"

    async def evaluate_async(self, context: Context) -> object:
        return "mock expression"


class MockNode(Node):
    """Mock AST node."""

    def __init__(self, token: Token) -> None:
        self.tok = token

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        buffer.write("mock node")

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        buffer.write("mock node")


class MockTag(Tag):
    """Mock tag."""

    block = False
    name = "mock"

    def parse(self, stream: TokenStream) -> Node:
        return MockNode(stream.current)


class MockChildNode(MockNode):
    """Mock AST node."""

    def children(self) -> List[ChildNode]:
        return [ChildNode(self.tok.linenum, expression=MockExpression())]


class MockChildTag(MockTag):
    """Mock tag"""

    def parse(self, stream: TokenStream) -> Node:
        return MockChildNode(stream.current)


# pylint: disable=too-many-public-methods
class CountTemplateVariablesTestCase(TestCase):
    """Test that we can count a template's variable references."""

    # pylint: disable=too-many-arguments
    def _test(
        self,
        template: BoundTemplate,
        template_refs: Refs,
        template_locals: Refs,
        template_globals: Refs,
        failed_visits: Optional[Refs] = None,
        unloadable: Optional[Refs] = None,
        raise_for_failures: bool = True,
    ) -> None:
        failed_visits = failed_visits if failed_visits is not None else {}
        unloadable = unloadable if unloadable is not None else {}

        refs = template.analyze(raise_for_failures=raise_for_failures)
        self.assertEqual(refs.local_variables, template_locals)
        self.assertEqual(refs.global_variables, template_globals)
        self.assertEqual(refs.variables, template_refs)
        self.assertEqual(refs.failed_visits, failed_visits)
        self.assertEqual(refs.unloadable_partials, unloadable)

        async def coro():
            return await template.analyze_async(raise_for_failures=raise_for_failures)

        refs = asyncio.run(coro())
        self.assertEqual(refs.local_variables, template_locals)
        self.assertEqual(refs.global_variables, template_globals)
        self.assertEqual(refs.variables, template_refs)
        self.assertEqual(refs.failed_visits, failed_visits)
        self.assertEqual(refs.unloadable_partials, unloadable)

    def test_analyze_output(self):
        """Test that we can count references in an output statement."""
        template = Template("{{ x | default: y, allow_false: z }}")

        expected_template_globals = {
            "x": [("<string>", 1)],
            "y": [("<string>", 1)],
            "z": [("<string>", 1)],
        }
        expected_template_locals = {}
        expected_refs = {
            "x": [("<string>", 1)],
            "y": [("<string>", 1)],
            "z": [("<string>", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_identifier_with_bracketed_string_literal(self):
        """Test that we can count references in bracketed identifiers."""
        template = Template("{{ x['y'].title }}")

        expected_template_globals = {"x.y.title": [("<string>", 1)]}
        expected_template_locals = {}
        expected_refs = {"x.y.title": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_identifier_with_nested_identifier(self):
        """Test that we can count references in nested identifiers."""
        template = Template("{{ x[y.z].title }}")

        expected_template_globals = {
            "x.[y.z].title": [("<string>", 1)],
            "y.z": [("<string>", 1)],
        }
        expected_template_locals = {}
        expected_refs = {"x.[y.z].title": [("<string>", 1)], "y.z": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_assign_tag(self):
        """Test that we can count references in an assign tag."""
        template = Template("{% assign x = y | append: z %}")

        expected_template_globals = {"y": [("<string>", 1)], "z": [("<string>", 1)]}
        expected_template_locals = {"x": [("<string>", 1)]}
        expected_refs = {"y": [("<string>", 1)], "z": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_capture_tag(self):
        """Test that we can count references in a capture tag."""
        template = Template("{% capture x %}{% if y %}z{% endif %}{% endcapture %}")

        expected_template_globals = {"y": [("<string>", 1)]}
        expected_template_locals = {"x": [("<string>", 1)]}
        expected_refs = {"y": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_case_tag(self):
        """Test that we can count references in a case tag."""
        # NOTE: `case` tags get rewritten to `if`/`elsif` tags, resulting in unintuitive
        # line numbers when analyzing `case` tags.
        template = Template(
            "\n".join(
                [
                    "{% case x %}",
                    "{% when y %}",
                    "  {{ a }}",
                    "{% when z %}",
                    "  {{ b }}",
                    "{% endcase %}",
                ]
            )
        )

        expected_template_globals = {
            "x": [("<string>", 2), ("<string>", 4)],
            "y": [("<string>", 2)],
            "a": [("<string>", 3)],
            "z": [("<string>", 4)],
            "b": [("<string>", 5)],
        }
        expected_template_locals = {}
        expected_refs = {
            "x": [("<string>", 2), ("<string>", 4)],
            "y": [("<string>", 2)],
            "a": [("<string>", 3)],
            "z": [("<string>", 4)],
            "b": [("<string>", 5)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_cycle_tag(self):
        """Test that we can count references in a cycle tag."""
        template = Template("{% cycle x: a, b %}")

        expected_template_globals = {
            "x": [("<string>", 1)],
            "a": [("<string>", 1)],
            "b": [("<string>", 1)],
        }
        expected_template_locals = {}
        expected_refs = {
            "x": [("<string>", 1)],
            "a": [("<string>", 1)],
            "b": [("<string>", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_decrement_tag(self):
        """Test that we can count references in a decrement tag."""
        template = Template("{% decrement x %}")

        expected_template_globals = {}
        expected_template_locals = {"x": [("<string>", 1)]}
        expected_refs = {}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_echo_tag(self):
        """Test that we can count references in an echo tag."""
        template = Template(r"{% echo x | default: y, allow_false: z %}")

        expected_template_globals = {
            "x": [("<string>", 1)],
            "y": [("<string>", 1)],
            "z": [("<string>", 1)],
        }
        expected_template_locals = {}
        expected_refs = {
            "x": [("<string>", 1)],
            "y": [("<string>", 1)],
            "z": [("<string>", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_for_tag(self):
        """Test that we can count references in a for tag."""
        template = Template(
            "\n".join(
                [
                    "{% for x in (1..y) %}",
                    "  {{ x }}",
                    "{% else %}",
                    "  {{ z }}",
                    "{% endfor %}",
                ]
            )
        )

        expected_template_globals = {"y": [("<string>", 1)], "z": [("<string>", 4)]}
        expected_template_locals = {}
        expected_refs = {
            "x": [("<string>", 2)],
            "y": [("<string>", 1)],
            "z": [("<string>", 4)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_if_tag(self):
        """Test that we can count references in an if tag."""
        template = Template(
            "\n".join(
                [
                    "{% if x %}",
                    "  {{ a }}",
                    "{% elsif y %}",
                    "  {{ b }}",
                    "{% endif %}",
                ]
            )
        )

        expected_template_globals = {
            "x": [("<string>", 1)],
            "a": [("<string>", 2)],
            "y": [("<string>", 3)],
            "b": [("<string>", 4)],
        }
        expected_template_locals = {}
        expected_refs = {
            "x": [("<string>", 1)],
            "a": [("<string>", 2)],
            "y": [("<string>", 3)],
            "b": [("<string>", 4)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_ifchanged_tag(self):
        """Test that we can count references in an ifchanged tag."""
        template = Template(r"{% ifchanged %}{{ x }}{% endifchanged %}")

        expected_template_globals = {"x": [("<string>", 1)]}
        expected_template_locals = {}
        expected_refs = {"x": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_increment_tag(self):
        """Test that we can count references in an increment tag."""
        template = Template("{% increment x %}")

        expected_template_globals = {}
        expected_template_locals = {"x": [("<string>", 1)]}
        expected_refs = {}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_liquid_tag(self):
        """Test that we can count references in a liquid tag."""
        template = Template(
            "\n".join(
                [
                    r"{% liquid",
                    r"if product.title",
                    r"   echo foo | upcase",
                    r"else",
                    r"   echo 'product-1' | upcase ",
                    r"endif",
                    r"",
                    r"for i in (0..5)",
                    r"   echo i",
                    r"endfor %}",
                ]
            )
        )

        expected_template_globals = {
            "product.title": [("<string>", 2)],
            "foo": [("<string>", 3)],
        }
        expected_template_locals = {}
        expected_refs = {
            "product.title": [("<string>", 2)],
            "foo": [("<string>", 3)],
            "i": [("<string>", 9)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_tablerow_tag(self):
        """Test that we can count references in a tablerow tag."""
        template = Template(
            r"{% tablerow x in y.z %}{{ x | append: a }}{% endtablerow %}",
        )

        expected_template_globals = {"y.z": [("<string>", 1)], "a": [("<string>", 1)]}
        expected_template_locals = {}
        expected_refs = {
            "y.z": [("<string>", 1)],
            "x": [("<string>", 1)],
            "a": [("<string>", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_unless_tag(self):
        """Test that we can count references in an unless tag."""
        template = Template(
            "\n".join(
                [
                    "{% unless x %}",
                    "  {{ a }}",
                    "{% elsif y %}",
                    "  {{ b }}",
                    "{% endunless %}",
                ]
            )
        )

        expected_template_globals = {
            "x": [("<string>", 1)],
            "a": [("<string>", 2)],
            "y": [("<string>", 3)],
            "b": [("<string>", 4)],
        }
        expected_template_locals = {}
        expected_refs = {
            "x": [("<string>", 1)],
            "a": [("<string>", 2)],
            "y": [("<string>", 3)],
            "b": [("<string>", 4)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_include_tag(self):
        """Test that we can count references in an include tag."""
        loader = DictLoader({"some_name": "{{ y }}"})
        env = Environment(loader=loader)
        template = env.from_string("{% include 'some_name' %}")

        expected_template_globals = {"y": [("some_name", 1)]}
        expected_template_locals = {}
        expected_refs = {"y": [("some_name", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_include_tag_with_assign(self):
        """Test that we can count references in an include tag and update template
        locals ."""
        loader = DictLoader({"some_name": "{{ y }}{% assign z = 4 %}"})
        env = Environment(loader=loader)
        template = env.from_string("{% include 'some_name' %}{{ z }}")

        expected_template_globals = {"y": [("some_name", 1)]}
        expected_template_locals = {"z": [("some_name", 1)]}
        expected_refs = {"y": [("some_name", 1)], "z": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_include_tag_once(self):
        """Test that we analyze each partial template once."""
        loader = DictLoader({"some_name": "{{ y }}"})
        env = Environment(loader=loader)
        template = env.from_string("{% include 'some_name' %}{% include 'some_name' %}")

        expected_template_globals = {"y": [("some_name", 1)]}
        expected_template_locals = {}
        expected_refs = {"y": [("some_name", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_recursive_include_tag(self):
        """Test that we can analyze recursive include tags."""
        loader = DictLoader({"some_name": "{{ y }}{% include 'some_name' %}"})
        env = Environment(loader=loader)
        template = env.from_string("{% include 'some_name' %}")

        expected_template_globals = {"y": [("some_name", 1)]}
        expected_template_locals = {}
        expected_refs = {"y": [("some_name", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_include_tag_with_bound_variable(self):
        """Test that we can count references in an include tag that uses a bound
        variable."""
        # Without an "as" alias, bound variables are given the name of the included
        # template, up to the first dot.
        loader = DictLoader({"some_name": "{{ y | append: x }}{{ some_name }}"})
        env = Environment(loader=loader)
        template = env.from_string("{% include 'some_name' with foo %}")

        expected_template_globals = {
            "foo": [("<string>", 1)],
            "y": [("some_name", 1)],
            "x": [("some_name", 1)],
        }
        expected_template_locals = {}
        expected_refs = {
            "y": [("some_name", 1)],
            "foo": [("<string>", 1)],
            "x": [("some_name", 1)],
            "some_name": [("some_name", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_include_tag_with_alias(self):
        """Test that we can count references in an include tag that uses an alias."""
        loader = DictLoader({"some_name": "{{ y | append: x }}"})
        env = Environment(loader=loader)
        template = env.from_string("{% include 'some_name' with foo as x %}")

        expected_template_globals = {"foo": [("<string>", 1)], "y": [("some_name", 1)]}
        expected_template_locals = {}
        expected_refs = {
            "y": [("some_name", 1)],
            "foo": [("<string>", 1)],
            "x": [("some_name", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_include_tag_with_arguments(self):
        """Test that we can count references in an include tag with arguments."""
        loader = DictLoader({"some_name": "{{ y | append: x }}"})
        env = Environment(loader=loader)
        template = env.from_string("{% include 'some_name', x:y, z:'4' %}\n{{ x }}")

        expected_template_globals = {
            "y": [("some_name", 1), ("<string>", 1)],
            "x": [("<string>", 2)],
        }
        expected_template_locals = {}
        expected_refs = {
            "x": [("some_name", 1), ("<string>", 2)],
            "y": [("some_name", 1), ("<string>", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_include_with_variable_name(self):
        """Test that we handle include tags with a variable template name."""
        env = Environment()
        template = env.from_string("{% include somevar %}{{ y }}")

        expected_template_globals = {
            "somevar": [("<string>", 1)],
            "y": [("<string>", 1)],
        }
        expected_template_locals = {}
        expected_refs = {"somevar": [("<string>", 1)], "y": [("<string>", 1)]}
        expected_unloadable_partials = {"somevar": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            unloadable=expected_unloadable_partials,
            raise_for_failures=False,
        )

        with self.assertRaises(TemplateTraversalError):
            self._test(
                template,
                expected_refs,
                expected_template_locals,
                expected_template_globals,
                unloadable=expected_unloadable_partials,
                raise_for_failures=True,
            )

    def test_include_template_not_found(self):
        """Test that we handle templates that can not be found."""
        env = Environment()
        template = env.from_string("{% include 'nosuchtemplate' %}{{ y }}")

        expected_template_globals = {"y": [("<string>", 1)]}
        expected_template_locals = {}
        expected_refs = {"y": [("<string>", 1)]}
        expected_unloadable_partials = {"nosuchtemplate": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            unloadable=expected_unloadable_partials,
            raise_for_failures=False,
        )

        with self.assertRaises(TemplateTraversalError):
            self._test(
                template,
                expected_refs,
                expected_template_locals,
                expected_template_globals,
                unloadable=expected_unloadable_partials,
                raise_for_failures=True,
            )

    def test_analyze_render_tag(self):
        """Test that we can count references in a render tag."""
        loader = DictLoader({"some_name": "{{ x }}{% assign y = z %}"})
        env = Environment(loader=loader)
        template = env.from_string("{% assign z = 1 %}{% render 'some_name' %}")

        expected_template_globals = {"x": [("some_name", 1)], "z": [("some_name", 1)]}
        expected_template_locals = {"z": [("<string>", 1)]}
        expected_refs = {"x": [("some_name", 1)], "z": [("some_name", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_render_tag_once(self):
        """Test that analyze each partial rendered template once."""
        loader = DictLoader({"some_name": "{{ x }}"})
        env = Environment(loader=loader)
        template = env.from_string("{% render 'some_name' %}{% render 'some_name' %}")

        expected_template_globals = {"x": [("some_name", 1)]}
        expected_template_locals = {}
        expected_refs = {"x": [("some_name", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_recursive_render_tag(self):
        """Test that we can analyze recursive render tags."""
        loader = DictLoader({"some_name": "{{ y }}{% render 'some_name' %}"})
        env = Environment(loader=loader)
        template = env.from_string("{% render 'some_name' %}")

        expected_template_globals = {"y": [("some_name", 1)]}
        expected_template_locals = {}
        expected_refs = {"y": [("some_name", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_render_tag_with_bound_variable(self):
        """Test that we can count references in a render tag that uses a bound
        variable."""
        loader = DictLoader({"some_name": "{{ y | append: x }}{{ some_name }}"})
        env = Environment(loader=loader)
        template = env.from_string("{% render 'some_name' with foo %}")

        expected_template_globals = {
            "foo": [("<string>", 1)],
            "y": [("some_name", 1)],
            "x": [("some_name", 1)],
        }
        expected_template_locals = {}
        expected_refs = {
            "y": [("some_name", 1)],
            "foo": [("<string>", 1)],
            "x": [("some_name", 1)],
            "some_name": [("some_name", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_render_tag_with_alias(self):
        """Test that we can count references in a render tag that uses an alias."""
        loader = DictLoader({"some_name": "{{ y | append: x }}"})
        env = Environment(loader=loader)
        template = env.from_string("{% render 'some_name' with foo as x %}")

        expected_template_globals = {"foo": [("<string>", 1)], "y": [("some_name", 1)]}
        expected_template_locals = {}
        expected_refs = {
            "y": [("some_name", 1)],
            "foo": [("<string>", 1)],
            "x": [("some_name", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_render_tag_with_arguments(self):
        """Test that we can count references in a render tag with arguments."""
        loader = DictLoader({"some_name": "{{ y | append: x }}"})
        env = Environment(loader=loader)
        template = env.from_string("{% render 'some_name', x:y, z:'4' %}\n{{ x }}")

        expected_template_globals = {
            "y": [("some_name", 1), ("<string>", 1)],
            "x": [("<string>", 2)],
        }
        expected_template_locals = {}
        expected_refs = {
            "x": [("some_name", 1), ("<string>", 2)],
            "y": [("some_name", 1), ("<string>", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_render_tag_scope(self):
        """Test that we local references in a render tag go out of scope."""
        loader = DictLoader({"some_name": "{{ x }}{% assign y = z %}"})
        env = Environment(loader=loader)
        template = env.from_string("{% assign z = 1 %}{% render 'some_name' %}{{ y }}")

        expected_template_globals = {
            "x": [("some_name", 1)],
            "z": [("some_name", 1)],
            "y": [("<string>", 1)],
        }
        expected_template_locals = {"z": [("<string>", 1)]}
        expected_refs = {
            "x": [("some_name", 1)],
            "z": [("some_name", 1)],
            "y": [("<string>", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_render_template_not_found(self):
        """Test that we handle templates that can not be found."""
        env = Environment()
        template = env.from_string("{% render 'nosuchtemplate' %}{{ y }}")

        expected_template_globals = {"y": [("<string>", 1)]}
        expected_template_locals = {}
        expected_refs = {"y": [("<string>", 1)]}
        expected_unloadable_partials = {"nosuchtemplate": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            unloadable=expected_unloadable_partials,
            raise_for_failures=False,
        )

        with self.assertRaises(TemplateTraversalError):
            self._test(
                template,
                expected_refs,
                expected_template_locals,
                expected_template_globals,
                unloadable=expected_unloadable_partials,
                raise_for_failures=True,
            )

    def test_node_missing_children(self):
        """Test that we handle AST nodes that don't implement a children method."""
        env = Environment(tolerance=Mode.STRICT)
        env.add_tag(MockTag)
        template = env.from_string("{% mock %}\n{% mock %}")

        expected_failed_visits = {"MockNode": [("<string>", 1), ("<string>", 2)]}

        self._test(
            template,
            {},
            {},
            {},
            failed_visits=expected_failed_visits,
            raise_for_failures=False,
        )

        with self.assertRaises(TemplateTraversalError):
            self._test(
                template,
                {},
                {},
                {},
                failed_visits=expected_failed_visits,
                raise_for_failures=True,
            )

    def test_expression_missing_children(self):
        """Test that we handle expressions that don't implement a children method."""
        env = Environment(tolerance=Mode.STRICT)
        env.add_tag(MockChildTag)
        template = env.from_string("{% mock %}\n{% mock %}")

        expected_failed_visits = {"MockExpression": [("<string>", 1), ("<string>", 2)]}

        self._test(
            template,
            {},
            {},
            {},
            failed_visits=expected_failed_visits,
            raise_for_failures=False,
        )

        with self.assertRaises(TemplateTraversalError):
            self._test(
                template,
                {},
                {},
                {},
                failed_visits=expected_failed_visits,
                raise_for_failures=True,
            )
