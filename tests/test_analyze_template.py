"""Test cases for statically counting a template using `BoundTemplate.analyze`."""
# pylint: disable=too-many-lines
import asyncio

from typing import List
from typing import Optional
from typing import TextIO

from unittest import TestCase

from liquid import Environment
from liquid import DictLoader
from liquid import Template

from liquid.ast import ChildNode
from liquid.ast import Node

from liquid.context import Context
from liquid.exceptions import TemplateInheritanceError
from liquid.exceptions import TemplateTraversalError
from liquid.expression import Expression

from liquid.extra import add_inheritance_tags
from liquid.extra import add_inline_expression_tags
from liquid.extra import WithTag

from liquid.mode import Mode
from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.template import BoundTemplate
from liquid.template import NameRefs
from liquid.template import Refs
from liquid.template import TemplateAnalysis

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
class AnalyzeTemplateTestCase(TestCase):
    """Test that we can count a template's variables, tags and filters."""

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
        template_filters: Optional[NameRefs] = None,
        template_tags: Optional[NameRefs] = None,
    ) -> None:
        """Template analysis test helper."""

        async def coro():
            return await template.analyze_async(raise_for_failures=raise_for_failures)

        def assert_refs(refs: TemplateAnalysis) -> None:
            self.assertEqual(refs.local_variables, template_locals)
            self.assertEqual(refs.global_variables, template_globals)
            self.assertEqual(refs.variables, template_refs)

            if failed_visits:
                self.assertEqual(refs.failed_visits, failed_visits)
            else:
                self.assertEqual(refs.failed_visits, {})

            if unloadable:
                self.assertEqual(refs.unloadable_partials, unloadable)
            else:
                self.assertEqual(refs.unloadable_partials, {})

            if template_filters:
                self.assertEqual(refs.filters, template_filters)
            else:
                self.assertEqual(refs.filters, {})

            if template_tags:
                self.assertEqual(refs.tags, template_tags)
            else:
                self.assertEqual(refs.tags, {})

        assert_refs(template.analyze(raise_for_failures=raise_for_failures))
        assert_refs(asyncio.run(coro()))

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

        expected_filters = {
            "default": [("<string>", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_filters=expected_filters,
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
            "x[y.z].title": [("<string>", 1)],
            "y.z": [("<string>", 1)],
        }
        expected_template_locals = {}
        expected_refs = {"x[y.z].title": [("<string>", 1)], "y.z": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

    def test_analyze_identifier_with_bracketed_string_literal_containing_dots(self):
        """Test that we can represent dotted properties."""
        template = Template("{{ some['foo.bar'] }}")

        expected_template_globals = {'some["foo.bar"]': [("<string>", 1)]}
        expected_template_locals = {}
        expected_refs = {'some["foo.bar"]': [("<string>", 1)]}

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
        expected_filters = {"append": [("<string>", 1)]}
        expected_tags = {"assign": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_filters=expected_filters,
            template_tags=expected_tags,
        )

    def test_analyze_capture_tag(self):
        """Test that we can count references in a capture tag."""
        template = Template("{% capture x %}{% if y %}z{% endif %}{% endcapture %}")

        expected_template_globals = {"y": [("<string>", 1)]}
        expected_template_locals = {"x": [("<string>", 1)]}
        expected_refs = {"y": [("<string>", 1)]}
        expected_tags = {
            "capture": [("<string>", 1)],
            "if": [("<string>", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
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
        expected_tags = {"case": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
        )

    def test_analyze_cycle_tag(self):
        """Test that we can count references in a cycle tag."""
        template = Template("{% cycle x: a, b %}")

        expected_template_globals = {
            "a": [("<string>", 1)],
            "b": [("<string>", 1)],
            "x": [("<string>", 1)],
        }
        expected_template_locals = {}
        expected_refs = {
            "a": [("<string>", 1)],
            "b": [("<string>", 1)],
            "x": [("<string>", 1)],
        }
        expected_tags = {"cycle": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
        )

    def test_analyze_decrement_tag(self):
        """Test that we can count references in a decrement tag."""
        template = Template("{% decrement x %}")

        expected_template_globals = {}
        expected_template_locals = {"x": [("<string>", 1)]}
        expected_refs = {}
        expected_tags = {"decrement": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
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
        expected_template_filters = {"default": [("<string>", 1)]}
        expected_tags = {"echo": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_filters=expected_template_filters,
            template_tags=expected_tags,
        )

    def test_analyze_for_tag(self):
        """Test that we can count references in a for tag."""
        template = Template(
            "\n".join(
                [
                    "{% for x in (1..y) %}",
                    "  {{ x }}",
                    "{% break %}",
                    "{% else %}",
                    "  {{ z }}",
                    "{% continue %}",
                    "{% endfor %}",
                ]
            )
        )

        expected_template_globals = {"y": [("<string>", 1)], "z": [("<string>", 5)]}
        expected_template_locals = {}
        expected_refs = {
            "x": [("<string>", 2)],
            "y": [("<string>", 1)],
            "z": [("<string>", 5)],
        }

        expected_tags = {
            "break": [("<string>", 3)],
            "continue": [("<string>", 6)],
            "for": [("<string>", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
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
        expected_tags = {"if": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
        )

    def test_analyze_ifchanged_tag(self):
        """Test that we can count references in an ifchanged tag."""
        template = Template(r"{% ifchanged %}{{ x }}{% endifchanged %}")

        expected_template_globals = {"x": [("<string>", 1)]}
        expected_template_locals = {}
        expected_refs = {"x": [("<string>", 1)]}
        expected_tags = {"ifchanged": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
        )

    def test_analyze_increment_tag(self):
        """Test that we can count references in an increment tag."""
        template = Template("{% increment x %}")

        expected_template_globals = {}
        expected_template_locals = {"x": [("<string>", 1)]}
        expected_refs = {}
        expected_tags = {"increment": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
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
        expected_template_filters = {
            "upcase": [("<string>", 3), ("<string>", 5)],
        }
        expected_tags = {
            "echo": [("<string>", 3), ("<string>", 5), ("<string>", 9)],
            "for": [("<string>", 8)],
            "if": [("<string>", 2)],
            "liquid": [("<string>", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_filters=expected_template_filters,
            template_tags=expected_tags,
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
        expected_template_filters = {"append": [("<string>", 1)]}
        expected_tags = {"tablerow": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_filters=expected_template_filters,
            template_tags=expected_tags,
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
        expected_tags = {"unless": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
        )

    def test_analyze_include_tag(self):
        """Test that we can count references in an include tag."""
        loader = DictLoader({"some_name": "{{ y }}"})
        env = Environment(loader=loader)
        template = env.from_string("{% include 'some_name' %}")

        expected_template_globals = {"y": [("some_name", 1)]}
        expected_template_locals = {}
        expected_refs = {"y": [("some_name", 1)]}
        expected_tags = {"include": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
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
        expected_tags = {"assign": [("some_name", 1)], "include": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
        )

    def test_analyze_include_tag_once(self):
        """Test that we analyze each partial template once."""
        loader = DictLoader({"some_name": "{{ y }}"})
        env = Environment(loader=loader)
        template = env.from_string("{% include 'some_name' %}{% include 'some_name' %}")

        expected_template_globals = {"y": [("some_name", 1)]}
        expected_template_locals = {}
        expected_refs = {"y": [("some_name", 1)]}
        expected_tags = {"include": [("<string>", 1), ("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
        )

    def test_analyze_recursive_include_tag(self):
        """Test that we can analyze recursive include tags."""
        loader = DictLoader({"some_name": "{{ y }}{% include 'some_name' %}"})
        env = Environment(loader=loader)
        template = env.from_string("{% include 'some_name' %}")

        expected_template_globals = {"y": [("some_name", 1)]}
        expected_template_locals = {}
        expected_refs = {"y": [("some_name", 1)]}
        expected_tags = {"include": [("<string>", 1), ("some_name", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
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
        expected_template_filters = {"append": [("some_name", 1)]}
        expected_tags = {"include": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_filters=expected_template_filters,
            template_tags=expected_tags,
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
        expected_template_filters = {"append": [("some_name", 1)]}
        expected_tags = {"include": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_filters=expected_template_filters,
            template_tags=expected_tags,
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
        expected_template_filters = {"append": [("some_name", 1)]}
        expected_tags = {"include": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_filters=expected_template_filters,
            template_tags=expected_tags,
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
        expected_tags = {"include": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            unloadable=expected_unloadable_partials,
            raise_for_failures=False,
            template_tags=expected_tags,
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
        expected_tags = {"include": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            unloadable=expected_unloadable_partials,
            raise_for_failures=False,
            template_tags=expected_tags,
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
        expected_tags = {
            "assign": [("<string>", 1), ("some_name", 1)],
            "render": [("<string>", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
        )

    def test_analyze_render_tag_once(self):
        """Test that analyze each partial rendered template once."""
        loader = DictLoader({"some_name": "{{ x }}"})
        env = Environment(loader=loader)
        template = env.from_string("{% render 'some_name' %}{% render 'some_name' %}")

        expected_template_globals = {"x": [("some_name", 1)]}
        expected_template_locals = {}
        expected_refs = {"x": [("some_name", 1)]}
        expected_tags = {"render": [("<string>", 1), ("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
        )

    def test_analyze_recursive_render_tag(self):
        """Test that we can analyze recursive render tags."""
        loader = DictLoader({"some_name": "{{ y }}{% render 'some_name' %}"})
        env = Environment(loader=loader)
        template = env.from_string("{% render 'some_name' %}")

        expected_template_globals = {"y": [("some_name", 1)]}
        expected_template_locals = {}
        expected_refs = {"y": [("some_name", 1)]}
        expected_tags = {"render": [("<string>", 1), ("some_name", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
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
        expected_template_filters = {"append": [("some_name", 1)]}
        expected_tags = {"render": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_filters=expected_template_filters,
            template_tags=expected_tags,
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
        expected_template_filters = {"append": [("some_name", 1)]}
        expected_tags = {"render": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_filters=expected_template_filters,
            template_tags=expected_tags,
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
        expected_template_filters = {"append": [("some_name", 1)]}
        expected_tags = {"render": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_filters=expected_template_filters,
            template_tags=expected_tags,
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
        expected_tags = {
            "assign": [("<string>", 1), ("some_name", 1)],
            "render": [("<string>", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
        )

    def test_render_template_not_found(self):
        """Test that we handle templates that can not be found."""
        env = Environment()
        template = env.from_string("{% render 'nosuchtemplate' %}{{ y }}")

        expected_template_globals = {"y": [("<string>", 1)]}
        expected_template_locals = {}
        expected_refs = {"y": [("<string>", 1)]}
        expected_unloadable_partials = {"nosuchtemplate": [("<string>", 1)]}
        expected_tags = {"render": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            unloadable=expected_unloadable_partials,
            raise_for_failures=False,
            template_tags=expected_tags,
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
        expected_tags = {"mock": [("<string>", 1), ("<string>", 2)]}

        self._test(
            template,
            {},
            {},
            {},
            failed_visits=expected_failed_visits,
            raise_for_failures=False,
            template_tags=expected_tags,
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
        expected_tags = {"mock": [("<string>", 1), ("<string>", 2)]}

        self._test(
            template,
            {},
            {},
            {},
            failed_visits=expected_failed_visits,
            raise_for_failures=False,
            template_tags=expected_tags,
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

    def test_analyze_conditional_expression(self) -> None:
        """Test that we can statically analyze non-standard conditional expressions."""
        env = Environment()
        add_inline_expression_tags(env)

        template = env.from_string(r"{{ foo | upcase if a.b else bar || append: baz }}")

        expected_template_globals = {
            "foo": [("<string>", 1)],
            "a.b": [("<string>", 1)],
            "bar": [("<string>", 1)],
            "baz": [("<string>", 1)],
        }
        expected_template_locals: Refs = {}
        expected_refs = {
            "foo": [("<string>", 1)],
            "a.b": [("<string>", 1)],
            "bar": [("<string>", 1)],
            "baz": [("<string>", 1)],
        }
        expected_template_filters = {
            "upcase": [("<string>", 1)],
            "append": [("<string>", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_filters=expected_template_filters,
        )

    def test_analyze_with_tag(self) -> None:
        """Test that we can statically analyze non-standard with tags."""
        env = Environment()
        env.add_tag(WithTag)

        template = env.from_string(
            r"{% with p: collection.products.first %}"
            r"{{ p.title }}"
            r"{% endwith %}"
            r"{{ p.title }}"
            r"{{ collection.products.first.title }}"
        )

        expected_template_globals = {
            "collection.products.first": [("<string>", 1)],
            "p.title": [("<string>", 1)],
            "collection.products.first.title": [("<string>", 1)],
        }
        expected_template_locals: Refs = {}
        expected_refs = {
            "collection.products.first": [("<string>", 1)],
            "collection.products.first.title": [("<string>", 1)],
            "p.title": [("<string>", 1), ("<string>", 1)],
        }
        expected_tags = {"with": [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_tags=expected_tags,
        )

    def test_variable_parts(self) -> None:
        """Test that we can retrieve a variable's parts as a tuple."""
        template = Template("{{ some['foo.bar'] }}")

        expected_template_globals = {'some["foo.bar"]': [("<string>", 1)]}
        expected_template_locals = {}
        expected_refs = {'some["foo.bar"]': [("<string>", 1)]}

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
        )

        refs = template.analyze(raise_for_failures=True)
        _ref = list(refs.variables.keys())[0]
        self.assertEqual(_ref.parts, ("some", "foo.bar"))

        global_ref = list(refs.global_variables.keys())[0]
        self.assertEqual(global_ref.parts, ("some", "foo.bar"))

        async def coro():
            return await template.analyze_async(raise_for_failures=True)

        refs = asyncio.run(coro())
        _ref = list(refs.variables.keys())[0]
        self.assertEqual(_ref.parts, ("some", "foo.bar"))

        global_ref = list(refs.global_variables.keys())[0]
        self.assertEqual(global_ref.parts, ("some", "foo.bar"))

    def test_analyze_inheritance_chain(self):
        """Test that we can count references in a chain of inherited templates."""
        loader = DictLoader(
            {
                "base": (
                    "Hello, "
                    "{% assign x = 'foo' %}"
                    "{% block content %}{{ x | upcase }}{% endblock %}!"
                    "{% block foo %}{% endblock %}!"
                ),
                "other": (
                    "{% extends 'base' %}"
                    "{% block content %}{{ x | downcase }}{% endblock %}"
                    "{% block foo %}{% assign z = 7 %}{% endblock %}"
                ),
                "some": "{% extends 'other' %}{{ y | append: x }}{% block foo %}{% endblock %}",
            }
        )
        env = Environment(loader=loader)
        add_inheritance_tags(env)
        template = env.get_template("some")

        expected_template_globals = {}
        expected_template_locals = {"x": [("base", 1)]}
        expected_refs = {
            "x": [("other", 1)],
        }
        expected_template_filters = {
            "downcase": [("other", 1)],
        }
        expected_tags = {
            "assign": [("base", 1)],
            "extends": [("some", 1), ("other", 1)],
            "block": [
                ("some", 1),
                ("other", 1),
                ("other", 1),
                ("base", 1),
                ("base", 1),
            ],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_filters=expected_template_filters,
            template_tags=expected_tags,
        )

    def test_analyze_recursive_extends(self):
        """Test that we handle recursive use of the 'extends' tag."""
        loader = DictLoader(
            {
                "some": "{% extends 'other' %}",
                "other": "{% extends 'some' %}",
            }
        )
        env = Environment(loader=loader)
        add_inheritance_tags(env)
        template = env.get_template("some")

        with self.assertRaises(TemplateInheritanceError):
            template.analyze()

    def test_analyze_super_block(self):
        """Test that we can count references when rendering super blocks."""
        loader = DictLoader(
            {
                "base": "Hello, {% block content %}{{ foo | upcase }}{% endblock %}!",
                "some": (
                    "{% extends 'base' %}"
                    "{% block content %}{{ block.super }}!{% endblock %}"
                ),
            }
        )
        env = Environment(loader=loader)
        add_inheritance_tags(env)
        template = env.get_template("some")

        expected_template_globals = {"foo": [("base", 1)]}
        expected_template_locals = {}
        expected_refs = {"foo": [("base", 1)], "block.super": [("some", 1)]}
        expected_template_filters = {"upcase": [("base", 1)]}
        expected_tags = {
            "extends": [("some", 1)],
            "block": [("some", 1), ("base", 1)],
        }

        self._test(
            template,
            expected_refs,
            expected_template_locals,
            expected_template_globals,
            template_filters=expected_template_filters,
            template_tags=expected_tags,
        )
