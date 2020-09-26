import unittest

from dataclasses import dataclass, field
from typing import Any, Mapping

from liquid import Environment
from liquid.context import Context
from liquid.compiler import Compiler
from liquid.vm import VM, Nop


@dataclass
class Case:
    description: str
    source: str
    expected: Any
    globals: Mapping = field(default_factory=dict)


class VMTestCase(unittest.TestCase):
    def _test_last_popped(self, test_cases):
        """Helper method for testing lists of Cases."""
        env = Environment()

        for case in test_cases:
            with self.subTest(msg=case.description):

                root = env.parse(case.source)

                compiler = Compiler()
                compiler.compile(root)

                vm = VM(
                    env,
                    bytecode=compiler.bytecode(),
                    context=Context(case.globals, filters=env.filters),
                )
                vm.run()
                elem = vm.last_popped_stack_elem()

                self.assertEqual(elem, case.expected)

    def _test(self, test_cases):
        """Helper method for testing lists of Cases."""
        env = Environment()

        for case in test_cases:
            with self.subTest(msg=case.description):
                root = env.parse(case.source)

                compiler = Compiler()
                compiler.compile(root)

                vm = VM(
                    env,
                    compiler.bytecode(),
                    context=Context(case.globals, filters=env.filters),
                )
                vm.run()
                out = vm.current_buffer().getvalue()

                self.assertEqual(out, case.expected)

    def test_literals(self):
        test_cases = [
            Case(description="integer literal", source=r"{{ 1 }}", expected=1),
            Case(description="float literal", source=r"{{ 1.5 }}", expected=1.5),
            Case(description="negative integer", source=r"{{ -1 }}", expected=-1),
            Case(description="negative float", source=r"{{ -1.2 }}", expected=-1.2),
            Case(
                description="string literal", source=r"{{ 'hello' }}", expected="hello"
            ),
            Case(description="template literal", source="hello", expected="hello"),
        ]

        self._test_last_popped(test_cases)

    def test_echo_literals(self):
        test_cases = [
            Case(description="integer literal", source="{% echo 1 %}", expected=1),
            Case(description="float literal", source="{% echo 1.5 %}", expected=1.5),
            Case(description="negative integer", source="{% echo  -1 %}", expected=-1),
            Case(description="negative float", source="{% echo -1.2 %}", expected=-1.2),
            Case(
                description="string literal",
                source="{% echo 'hello' %}",
                expected="hello",
            ),
        ]

        self._test_last_popped(test_cases)

    def test_raw(self):
        test_cases = [
            Case(
                description="literal output statement",
                source=r"{% raw %}{{ foo }}{% endraw %}",
                expected=r"{{ foo }}",
            ),
        ]

        self._test_last_popped(test_cases)

    def test_boolean_expression(self):
        test_cases = [
            Case(description="true", source=r"{{ true }}", expected=True),
            Case(description="false", source=r"{{ false }}", expected=False),
            Case(
                description="less than integers", source=r"{{ 1 < 2 }}", expected=True
            ),
            Case(
                description="greater than integers",
                source=r"{{ 1 > 2 }}",
                expected=False,
            ),
            Case(
                description="greater than integers that are equal",
                source=r"{{ 1 > 1 }}",
                expected=False,
            ),
            Case(
                description="less than integers that are equal",
                source=r"{{ 1 < 1 }}",
                expected=False,
            ),
            Case(
                description="less than or equal integers",
                source=r"{{ 1 <= 1 }}",
                expected=True,
            ),
            Case(
                description="greater than or equal integers",
                source=r"{{ 1 >= 1 }}",
                expected=True,
            ),
            Case(
                description="equals integers",
                source=r"{{ 1 == 1 }}",
                expected=True,
            ),
            Case(
                description="true equals false",
                source=r"{{ true == false }}",
                expected=False,
            ),
            Case(
                description="true equals true",
                source=r"{{ true == true }}",
                expected=True,
            ),
            Case(
                description="false equals false",
                source=r"{{ false == false }}",
                expected=True,
            ),
            Case(
                description="false not equals true",
                source=r"{{ false != true }}",
                expected=True,
            ),
            Case(
                description="false not equals true alt",
                source=r"{{ false <> true }}",
                expected=True,
            ),
            Case(
                description="true not equals false",
                source=r"{{ true != false }}",
                expected=True,
            ),
            Case(
                description="true not equals false alt",
                source=r"{{ true <> false }}",
                expected=True,
            ),
            Case(
                description="string contains string",
                source=r"{{ 'hello' contains 'ell' }}",
                expected=True,
            ),
            Case(
                description="string does not contain string",
                source=r"{{ 'hello' contains 'foo' }}",
                expected=False,
            ),
            Case(
                description="empty string",
                source=r"{{ 'hello' == empty }}",
                expected=False,
            ),
            Case(
                description="and with boolean literals",
                source=r"{{ true and false }}",
                expected=False,
            ),
            Case(
                description="or with boolean literals",
                source=r"{{ true or false }}",
                expected=True,
            ),
        ]

        self._test_last_popped(test_cases)

    def test_conditionals(self):
        """Test that we can execute "if" tags."""
        test_cases = [
            Case(
                description="literal true condition",
                source=r"{% if true %}10{% endif %}",
                expected="10",
            ),
            Case(
                description="literal true condition with alternative",
                source=r"{% if true %}10{% else %}20{% endif %}",
                expected="10",
            ),
            Case(
                description="literal false condition with alternative",
                source=r"{% if false %}10{% else %}20{% endif %}",
                expected="20",
            ),
            Case(
                description="truthy constant expression condition",
                source=r"{% if 1 < 2 %}10{% endif %}",
                expected="10",
            ),
            Case(
                description="truthy constant expression condition with alternative",
                source=r"{% if 1 < 2 %}10{% else %}20{% endif %}",
                expected="10",
            ),
            Case(
                description="falsey constant expression condition with alternative",
                source=r"{% if 1 > 2 %}10{% else %}20{% endif %}",
                expected="20",
            ),
            Case(
                description="falsey constant expression no alternative",
                source=r"{% if 1 > 2 %}10{% endif %}",
                expected=Nop,
            ),
            Case(
                description="conditional alternative with no default alternative",
                source=r"{% if false %}10{% elsif true %}20{% endif %}",
                expected="20",
            ),
            Case(
                description="truthy conditional alternative with default alternative",
                source=r"{% if false %}10{% elsif true %}20{% else %}30{% endif %}",
                expected="20",
            ),
            Case(
                description="falsey conditional alternative with default alternative",
                source=r"{% if false %}10{% elsif false %}20{% else %}30{% endif %}",
                expected="30",
            ),
            Case(
                description="unless literal false",
                source=r"{% unless false %}10{% endunless %}",
                expected="10",
            ),
        ]

        self._test_last_popped(test_cases)

    def test_assign(self):
        """Test that we can execute assign tags."""

        test_cases = [
            Case(
                description="assign and resolve",
                source=r"{% assign one = 1 %}{{ one }}",
                expected=1,
            ),
            Case(
                description="assign and resolve in condition",
                source=r"{% assign x = true %}{% if x %}foo{% endif %}",
                expected="foo",
            ),
        ]

        self._test_last_popped(test_cases)

    def test_capture(self):
        """Test that we can execute capture tags."""
        test_cases = [
            Case(
                description="capture and resolve",
                source=r"{% capture some %}foo{% endcapture %}{{ some }}",
                expected="foo",
            ),
        ]

        self._test_last_popped(test_cases)

    def test_case_when(self):
        """Test that we can execute case tags."""
        test_cases = [
            Case(
                description="simple case",
                source=r"{% case true %}{% when false %}foo{% when true %}bar{% endcase %}",
                expected="bar",
            ),
        ]

        self._test_last_popped(test_cases)

    def test_resolve(self):
        """Test that we can execute global identifiers."""
        context = {
            "collections": {"sports": "sportswear"},
            "product": {"collection_name": "sports", "title": "shorts"},
            "username": "brian",
        }

        test_cases = [
            Case(
                description="not a local identifier",
                source=r"{{ username }}",
                expected="brian",
                globals=context,
            ),
            Case(
                description="chained global identifier",
                source=r"{{ product.title }}",
                expected="shorts",
                globals=context,
            ),
            Case(
                description="get item from identifier",
                source=r"{{ collections[product.collection_name] }}",
                expected="sportswear",
                globals=context,
            ),
            Case(
                description="missing global",
                source=r"{{ nosuchthing }}",
                expected=None,
                globals=context,
            ),
            Case(
                description="missing global item access",
                source=r"{{ nosuchthing.foo }}",
                expected=None,
                globals=context,
            ),
            Case(
                description="local overrides global",
                source=r"{% assign username = 'dave' %}{{ username }}",
                expected="dave",
                globals=context,
            ),
        ]

        self._test_last_popped(test_cases)

    def test_counters(self):
        """Test that we can execute increment and decrement counters."""
        test_cases = [
            Case(description="new increment", source="{% increment foo %}", expected=0),
            Case(
                description="increment twice",
                source=r"{% increment foo %}{% increment foo %}",
                expected=1,
            ),
            Case(
                description="new decrement", source=r"{% decrement foo %}", expected=-1
            ),
            Case(
                description="decrement twice",
                source=r"{% decrement foo %}{% decrement foo %}",
                expected=-2,
            ),
            Case(
                description="increment then decrement",
                source=r"{% increment foo %}{% decrement foo %}",
                expected=-1,
            ),
            Case(
                description="counter scope",
                source=r"{% assign foo = 5 %}{% increment foo %}",
                expected=0,
            ),
        ]

        self._test_last_popped(test_cases)

    def test_cycle(self):
        """Test that we can execute "cycle" tags."""
        test_cases = [
            Case(
                description="default group",
                source=r"{% cycle 'a', 'b', 'c' %}",
                expected="a",
            ),
            Case(
                description="two calls to default group",
                source=r"{% cycle 'a', 'b', 'c' %}{% cycle 'a', 'b', 'c' %}",
                expected="b",
            ),
            Case(
                description="named group",
                source=r"{% cycle 'foo': 'a', 'b', 'c' %}",
                expected="a",
            ),
        ]

        self._test_last_popped(test_cases)

    def test_for_render(self):
        """Test that we can render "for" tags."""
        test_cases = [
            Case(
                description="simple range loop",
                source=r"{% for i in (0..3) %}{{ i }}{% endfor %}",
                expected="0123",
            ),
            Case(
                description="range loop with limit",
                source=r"{% for i in (0..3) limit:2 %}{{ i }}{% endfor %}",
                expected="01",
            ),
            Case(
                description="reversed range loop",
                source=r"{% for i in (0..3) reversed %}{{ i }}{% endfor %}",
                expected="3210",
            ),
            Case(
                description="for each loop",
                source=r"{% for c in collections %}{{ c }} {% endfor %}",
                expected="sport garden ",
                globals={"collections": ["sport", "garden"]},
            ),
            Case(
                description="for each loop over mapping",
                source=r"{% for c in collection %}{{ c[0] }} {{c[1]}} {% endfor %}",
                expected="title foo description bar ",
                globals={"collection": {"title": "foo", "description": "bar"}},
            ),
            Case(
                description="forloop index helper",
                source=r"{% for c in collections %}{{ forloop.index0 }}{% endfor %}",
                expected="01",
                globals={"collections": ["sport", "garden"]},
            ),
            Case(
                description="forloop last helper",
                source=r"{% for c in collections %}{{ forloop.last }} {% endfor %}",
                expected="false true ",
                globals={"collections": ["sport", "garden"]},
            ),
            Case(
                description="default on empty",
                source=r"{% for c in collections %}{{ c }}{% else %}empty{% endfor %}",
                expected="empty",
                globals={"collections": []},
            ),
            Case(
                description="nested loop",
                source=(
                    r"{% for i in nums %}"
                    r"{% for j in letters %}"
                    r"{{ i }}{{ j }} "
                    r"{% endfor %}"
                    r"{% endfor %}"
                    r"{{ 9999 }}"
                ),
                expected="1a 1b 1c 2a 2b 2c 3a 3b 3c 9999",
                globals={
                    "nums": [1, 2, 3],
                    "letters": ["a", "b", "c"],
                },
            ),
            Case(
                description="nested loop with continue",
                source=(
                    r"{% for i in nums %}"
                    r"{% for j in letters %}"
                    r"{% if j == 'b' %}{% continue %}{% endif %}"
                    r"{{ i }}{{ j }} "
                    r"{% endfor %}"
                    r"{% endfor %}"
                    r"{{ 9999 }}"
                ),
                expected="1a 1c 2a 2c 3a 3c 9999",
                globals={
                    "nums": [1, 2, 3],
                    "letters": ["a", "b", "c"],
                },
            ),
            Case(
                description="nested loop with continue",
                source=(
                    r"{% for i in nums %}"
                    r"{% for j in letters %}"
                    r"{% if j == 'b' %}{% continue %}{% endif %}"
                    r"{{ i }}{{ j }} "
                    r"{% endfor %}"
                    r"hello "
                    r"{% endfor %}"
                ),
                expected="1a 1c hello 2a 2c hello 3a 3c hello ",
                globals={
                    "nums": [1, 2, 3],
                    "letters": ["a", "b", "c"],
                },
            ),
            Case(
                description="nested loop with break",
                source=(
                    r"{% for i in nums %}"
                    r"{% for j in letters %}"
                    r"{% if j == 'c' %}{% break %}{% endif %}"
                    r"{{ i }}{{ j }} "
                    r"{% endfor %}"
                    r"hello "
                    r"{% endfor %}"
                ),
                expected="1a 1b hello 2a 2b hello 3a 3b hello ",
                globals={
                    "nums": [1, 2, 3],
                    "letters": ["a", "b", "c", "d"],
                },
            ),
            Case(
                description="loop variable goes out of scope",
                source=r"{% for i in nums %}{{ i }}{% endfor %}{{ i }}",
                expected="123",
                globals={
                    "nums": [1, 2, 3],
                },
            ),
        ]

        self._test(test_cases)

    def test_liquid_render(self):
        """Test that we can render "liquid" tags."""
        test_cases = [
            Case(
                description="multiple tags",
                source="\n".join(
                    [
                        r"{% liquid",
                        r"if product.title",
                        r"   echo product.title | upcase",
                        r"else",
                        r"   echo 'product-1' | upcase ",
                        r"endif",
                        r"",
                        r"for i in (0..5)",
                        r"   echo i",
                        r"endfor %}",
                    ]
                ),
                expected="FOO012345",
                globals={"product": {"title": "foo"}},
            ),
        ]

        self._test(test_cases)

    def test_render_filters(self):
        """Test that we can render filtered expressions."""
        test_cases = [
            Case(
                description="no arg filter",
                source=r"{{ product.title | upcase }}",
                expected="FOO",
                globals={"product": {"title": "foo"}},
            ),
            Case(
                description="one arg filter",
                source=r"{{ product.title | prepend: 'bar ' }}",
                expected="bar foo",
                globals={"product": {"title": "foo"}},
            ),
        ]

        self._test(test_cases)
