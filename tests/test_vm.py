import unittest

from typing import NamedTuple, Any

from liquid import Environment
from liquid.compiler import Compiler
from liquid.vm import VM, Noop


class Case(NamedTuple):
    description: str
    source: str
    expected: Any


class VMTestCase(unittest.TestCase):
    def _test(self, test_cases):
        """Helper method for testing lists of Cases."""
        env = Environment()

        for case in test_cases:
            with self.subTest(msg=case.description):
                root = env.parse(case.source)

                compiler = Compiler()
                compiler.compile(root)

                vm = VM(compiler.bytecode())
                vm.run()
                elem = vm.last_popped_stack_elem()

                self.assertEqual(elem, case.expected)

    def test_literals(self):
        test_cases = [
            Case(description="integer literal", source="{{ 1 }}", expected=1),
            Case(description="float literal", source="{{ 1.5 }}", expected=1.5),
            Case(description="negative integer", source="{{ -1 }}", expected=-1),
            Case(description="negative float", source="{{ -1.2 }}", expected=-1.2),
            Case(
                description="string literal", source="{{ 'hello' }}", expected="hello"
            ),
            Case(description="template literal", source="hello", expected="hello"),
        ]

        self._test(test_cases)

    def test_boolean_expression(self):
        test_cases = [
            Case(description="true", source="{{ true }}", expected=True),
            Case(description="false", source="{{ false }}", expected=False),
            Case(description="less than integers", source="{{ 1 < 2 }}", expected=True),
            Case(
                description="greater than integers",
                source="{{ 1 > 2 }}",
                expected=False,
            ),
            Case(
                description="greater than integers that are equal",
                source="{{ 1 > 1 }}",
                expected=False,
            ),
            Case(
                description="less than integers that are equal",
                source="{{ 1 < 1 }}",
                expected=False,
            ),
            Case(
                description="less than or equal integers",
                source="{{ 1 <= 1 }}",
                expected=True,
            ),
            Case(
                description="greater than or equal integers",
                source="{{ 1 >= 1 }}",
                expected=True,
            ),
            Case(
                description="equals integers",
                source="{{ 1 == 1 }}",
                expected=True,
            ),
            Case(
                description="true equals false",
                source="{{ true == false }}",
                expected=False,
            ),
            Case(
                description="true equals true",
                source="{{ true == true }}",
                expected=True,
            ),
            Case(
                description="false equals false",
                source="{{ false == false }}",
                expected=True,
            ),
            Case(
                description="false not equals true",
                source="{{ false != true }}",
                expected=True,
            ),
            Case(
                description="false not equals true alt",
                source="{{ false <> true }}",
                expected=True,
            ),
            Case(
                description="true not equals false",
                source="{{ true != false }}",
                expected=True,
            ),
            Case(
                description="true not equals false alt",
                source="{{ true <> false }}",
                expected=True,
            ),
            Case(
                description="string contains string",
                source="{{ 'hello' contains 'ell' }}",
                expected=True,
            ),
            Case(
                description="string does not contain string",
                source="{{ 'hello' contains 'foo' }}",
                expected=False,
            ),
            Case(
                description="empty string",
                source="{{ 'hello' == empty }}",
                expected=False,
            ),
            Case(
                description="and with boolean literals",
                source="{{ true and false }}",
                expected=False,
            ),
            Case(
                description="or with boolean literals",
                source="{{ true or false }}",
                expected=True,
            ),
        ]

        self._test(test_cases)

    def test_conditionals(self):
        """Test that we can execute "if" tags."""
        test_cases = [
            Case(
                description="literal true condition",
                source="{% if true %}10{% endif %}",
                expected="10",
            ),
            Case(
                description="literal true condition with alternative",
                source="{% if true %}10{% else %}20{% endif %}",
                expected="10",
            ),
            Case(
                description="literal false condition with alternative",
                source="{% if false %}10{% else %}20{% endif %}",
                expected="20",
            ),
            Case(
                description="truthy constant expression condition",
                source="{% if 1 < 2 %}10{% endif %}",
                expected="10",
            ),
            Case(
                description="truthy constant expression condition with alternative",
                source="{% if 1 < 2 %}10{% else %}20{% endif %}",
                expected="10",
            ),
            Case(
                description="falsey constant expression condition with alternative",
                source="{% if 1 > 2 %}10{% else %}20{% endif %}",
                expected="20",
            ),
            Case(
                description="falsey constant expression no alternative",
                source="{% if 1 > 2 %}10{% endif %}",
                expected=Noop,
            ),
            Case(
                description="conditional alternative with no default alternative",
                source="{% if false %}10{% elsif true %}20{% endif %}",
                expected="20",
            ),
            Case(
                description="truthy conditional alternative with default alternative",
                source="{% if false %}10{% elsif true %}20{% else %}30{% endif %}",
                expected="20",
            ),
            Case(
                description="falsey conditional alternative with default alternative",
                source="{% if false %}10{% elsif false %}20{% else %}30{% endif %}",
                expected="30",
            ),
        ]

        self._test(test_cases)

    def test_assign(self):
        """Test that we can execute assign tags."""

        test_cases = [
            Case(
                description="assign and resolve",
                source="{% assign one = 1 %}{{ one }}",
                expected=1,
            ),
            Case(
                description="assign and resolve in condition",
                source="{% assign x = true %}{% if x %}foo{% endif %}",
                expected="foo",
            ),
        ]

        self._test(test_cases)
