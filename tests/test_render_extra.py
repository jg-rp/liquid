"""Test cases for rendering non-standard "extra" tags."""
import asyncio
import unittest
from typing import List

from liquid import golden
from liquid.environment import Environment
from liquid.golden.case import Case
from liquid.loaders import DictLoader
from liquid.template import BoundTemplate

from liquid.extra import IfNotTag
from liquid.extra import WithTag
from liquid.extra import add_inline_expression_tags
from liquid.extra import add_extended_inline_expression_tags


class BaseRenderTestCase(unittest.TestCase):
    """Base class for test cases that render synchronously and asynchronously."""

    def setUp(self) -> None:
        self.partials = {}
        self.loader = DictLoader(self.partials)
        self.env = Environment(loader=self.loader)

    def _test(self, test_cases: List[Case]) -> None:
        for case in test_cases:
            self.partials.update(case.partials)

            with self.subTest(msg=case.description):
                template = self.env.from_string(case.template, globals=case.globals)
                result = template.render()
                self.assertEqual(result, case.expect)

        async def coro(template: BoundTemplate):
            return await template.render_async()

        for case in test_cases:
            self.partials.update(case.partials)

            with self.subTest(msg=case.description, asynchronous=True):
                template = self.env.from_string(case.template, globals=case.globals)
                result = asyncio.run(coro(template))
                self.assertEqual(result, case.expect)


class RenderIfNotTagTestCase(BaseRenderTestCase):
    """Test cases for non-standard `if` tag."""

    def setUp(self) -> None:
        super().setUp()
        self.env.add_tag(IfNotTag)

    def test_render_standard_if_tag(self) -> None:
        """Test that the `if (not)` tag renders standard `if` tags."""
        self._test(golden.if_tag.cases)

    def test_render_non_standard_if_tag(self) -> None:
        """Test that we can render `if` tags with logical `not` and grouping
        with parentheses."""
        test_cases = [
            Case(
                description="not false",
                template=r"{% if not false %}foo{% endif %}",
                expect="foo",
            ),
            Case(
                description="not true",
                template=r"{% if not true %}foo{% endif %}",
                expect="",
            ),
            Case(
                description="literal boolean filter",
                template=r"{{ false | default: true }}",
                expect="true",
            ),
            Case(
                description="not comparison to empty",
                template=r"{% if not '' == empty %}foo{% endif %}",
                expect="",
            ),
            Case(
                description="not contains",
                template=r"{% if not foo contains 'z' %}bar{% endif %}",
                expect="bar",
                globals={"foo": ["a", "b", "c"]},
            ),
            Case(
                description="and not",
                template=r"{% if not foo and not bar %}hello{% endif %}",
                expect="hello",
                globals={"foo": False, "bar": False},
            ),
            Case(
                description="true and not",
                template=r"{% if foo and not bar %}hello{% endif %}",
                expect="hello",
                globals={"foo": True, "bar": False},
            ),
            Case(
                description="not equals",
                template=r"{% if not foo == True %}hello{% endif %}",
                expect="hello",
                globals={"foo": False},
            ),
            Case(
                description="not not equals False",
                template=r"{% if not foo != true %}hello{% endif %}",
                expect="",
                globals={"foo": False},
            ),
            Case(
                description="not not equals true",
                template=r"{% if not foo != true %}hello{% endif %}",
                expect="hello",
                globals={"foo": True},
            ),
            Case(
                description="not contains with parens",
                template=r"{% if not (foo contains 'z') %}bar{% endif %}",
                expect="bar",
                globals={"foo": ["a", "b", "c"]},
            ),
        ]
        self._test(test_cases)


class RenderInlineIfTestCase(BaseRenderTestCase):
    """Test cases for rendering inline `if` tags and output statements."""

    def setUp(self) -> None:
        super().setUp()
        add_inline_expression_tags(self.env)

    def test_render_inline_if_output_statement(self) -> None:
        """Test that we can render output statements with inline `if` expressions."""
        test_cases = [
            Case(
                description="string literal with true condition",
                template=r"{{ 'hello' if true }}",
                expect="hello",
                globals={},
                partials={},
            ),
            Case(
                description="default to undefined",
                template=r"{{ 'hello' if false }}",
                expect="",
                globals={},
                partials={},
            ),
            Case(
                description="early filter",
                template=r"{{ 'hello' | upcase if true }}",
                expect="HELLO",
                globals={},
                partials={},
            ),
            Case(
                description="string literal with false condition and alternative",
                template=r"{{ 'hello' if false else 'goodbye' }}",
                expect="goodbye",
                globals={},
                partials={},
            ),
            Case(
                description="object and condition from context with tail filter",
                template=r"{{ greeting if settings.foo else 'bar' || upcase }}",
                expect="HELLO",
                globals={"settings": {"foo": True}, "greeting": "hello"},
                partials={},
            ),
        ]
        self._test(test_cases)

    def test_render_inline_if_assignment_tags(self) -> None:
        """Test that we can render `assign` tags with inline `if` expressions."""
        test_cases = [
            Case(
                description="string literal",
                template=r"{% assign foo = 'hello' %}{{ foo }}",
                expect="hello",
                globals={},
                partials={},
            ),
            Case(
                description="string literal with true condition",
                template=r"{% assign foo = 'hello' if true %}{{ foo }}",
                expect="hello",
                globals={},
                partials={},
            ),
            Case(
                description="default to undefined",
                template=r"{% assign foo = 'hello' if false %}{{ foo }}",
                expect="",
                globals={},
                partials={},
            ),
            Case(
                description="early  filter",
                template=r"{% assign foo = 'hello' | upcase if true %}{{ foo }}",
                expect="HELLO",
                globals={},
                partials={},
            ),
            Case(
                description="string literal with false condition and alternative",
                template=r"{% assign foo = 'hello' if false else 'goodbye' %}{{ foo }}",
                expect="goodbye",
                globals={},
                partials={},
            ),
            Case(
                description="object and condition from context with tail filter",
                template=(
                    r"{% assign foo = greeting if settings.foo else 'bar' || upcase %}"
                    r"{{ foo }}"
                ),
                expect="HELLO",
                globals={"settings": {"foo": True}, "greeting": "hello"},
                partials={},
            ),
        ]
        self._test(test_cases)

    def test_render_inline_if_echo_tags(self) -> None:
        """Test that we can render `echo` tags with inline `if` expressions."""
        test_cases = [
            Case(
                description="string literal",
                template=r"{% echo 'hello' %}",
                expect="hello",
                globals={},
                partials={},
            ),
            Case(
                description="string literal with true condition",
                template=r"{% echo 'hello' if true %}",
                expect="hello",
                globals={},
                partials={},
            ),
            Case(
                description="default to undefined",
                template=r"{% echo 'hello' if false %}",
                expect="",
                globals={},
                partials={},
            ),
            Case(
                description="early  filter",
                template=r"{% echo 'hello' | upcase if true %}",
                expect="HELLO",
                globals={},
                partials={},
            ),
            Case(
                description="string literal with false condition and alternative",
                template=r"{% echo 'hello' if false else 'goodbye' %}",
                expect="goodbye",
                globals={},
                partials={},
            ),
            Case(
                description="object and condition from context with tail filter",
                template=(r"{% echo greeting if settings.foo else 'bar' || upcase %}"),
                expect="HELLO",
                globals={"settings": {"foo": True}, "greeting": "hello"},
                partials={},
            ),
        ]
        self._test(test_cases)


class RenderInlineIfWithParensTestCase(BaseRenderTestCase):
    """Test cases for rendering inline `if` tags that support logical `not`
    and grouping terms with parentheses."""

    def setUp(self) -> None:
        super().setUp()
        add_extended_inline_expression_tags(self.env)

    def test_render_inline_if_output_statement(self) -> None:
        """Test that we can render output statements with inline `if` expressions."""
        test_cases = [
            Case(
                description="string literal with true condition",
                template=r"{{ 'hello' if true }}",
                expect="hello",
                globals={},
                partials={},
            ),
            Case(
                description="default to undefined",
                template=r"{{ 'hello' if false }}",
                expect="",
                globals={},
                partials={},
            ),
            Case(
                description="early  filter",
                template=r"{{ 'hello' | upcase if true }}",
                expect="HELLO",
                globals={},
                partials={},
            ),
            Case(
                description="string literal with false condition and alternative",
                template=r"{{ 'hello' if false else 'goodbye' }}",
                expect="goodbye",
                globals={},
                partials={},
            ),
            Case(
                description="negate condition",
                template=r"{{ 'hello' if not false else 'goodbye' }}",
                expect="hello",
                globals={},
                partials={},
            ),
            Case(
                description="group condition terms",
                template=r"{{ 'hello' if (false and true) or true }}",
                expect="hello",
                globals={},
                partials={},
            ),
            Case(
                description="object and condition from context with tail filter",
                template=r"{{ greeting if settings.foo else 'bar' || upcase }}",
                expect="HELLO",
                globals={"settings": {"foo": True}, "greeting": "hello"},
                partials={},
            ),
        ]
        self._test(test_cases)

    def test_render_inline_if_assignment_tags(self) -> None:
        """Test that we can render `assign` tags with inline `if` expressions."""
        test_cases = [
            Case(
                description="string literal",
                template=r"{% assign foo = 'hello' %}{{ foo }}",
                expect="hello",
                globals={},
                partials={},
            ),
            Case(
                description="string literal with true condition",
                template=r"{% assign foo = 'hello' if true %}{{ foo }}",
                expect="hello",
                globals={},
                partials={},
            ),
            Case(
                description="default to undefined",
                template=r"{% assign foo = 'hello' if false %}{{ foo }}",
                expect="",
                globals={},
                partials={},
            ),
            Case(
                description="early  filter",
                template=r"{% assign foo = 'hello' | upcase if true %}{{ foo }}",
                expect="HELLO",
                globals={},
                partials={},
            ),
            Case(
                description="string literal with false condition and alternative",
                template=r"{% assign foo = 'hello' if false else 'goodbye' %}{{ foo }}",
                expect="goodbye",
                globals={},
                partials={},
            ),
            Case(
                description="negate condition",
                template=r"{% assign foo = 'hello' if not false %}{{ foo }}",
                expect="hello",
                globals={},
                partials={},
            ),
            Case(
                description="group condition terms",
                template=(
                    r"{% assign foo = 'hello' if (false and true) or true %}"
                    r"{{ foo }}"
                ),
                expect="hello",
                globals={},
                partials={},
            ),
            Case(
                description="object and condition from context with tail filter",
                template=(
                    r"{% assign foo = greeting if settings.foo else 'bar' || upcase %}"
                    r"{{ foo }}"
                ),
                expect="HELLO",
                globals={"settings": {"foo": True}, "greeting": "hello"},
                partials={},
            ),
        ]
        self._test(test_cases)

    def test_render_inline_if_echo_tags(self) -> None:
        """Test that we can render `echo` tags with inline `if` expressions."""
        test_cases = [
            Case(
                description="string literal",
                template=r"{% echo 'hello' %}",
                expect="hello",
                globals={},
                partials={},
            ),
            Case(
                description="string literal with true condition",
                template=r"{% echo 'hello' if true %}",
                expect="hello",
                globals={},
                partials={},
            ),
            Case(
                description="default to undefined",
                template=r"{% echo 'hello' if false %}",
                expect="",
                globals={},
                partials={},
            ),
            Case(
                description="early filter",
                template=r"{% echo 'hello' | upcase if true %}",
                expect="HELLO",
                globals={},
                partials={},
            ),
            Case(
                description="string literal with false condition and alternative",
                template=r"{% echo 'hello' if false else 'goodbye' %}",
                expect="goodbye",
                globals={},
                partials={},
            ),
            Case(
                description="negate condition",
                template=r"{% echo 'hello' if not false else 'goodbye' %}",
                expect="hello",
                globals={},
                partials={},
            ),
            Case(
                description="group condition terms",
                template=r"{% echo 'hello' if (false and true) or true %}",
                expect="hello",
                globals={},
                partials={},
            ),
            Case(
                description="object and condition from context with tail filter",
                template=(r"{% echo greeting if settings.foo else 'bar' || upcase %}"),
                expect="HELLO",
                globals={"settings": {"foo": True}, "greeting": "hello"},
                partials={},
            ),
        ]
        self._test(test_cases)


class RenderWithTagTestCase(BaseRenderTestCase):
    """Test cases for non-standard `with` tag."""

    def setUp(self) -> None:
        super().setUp()
        self.env.add_tag(WithTag)

    def test_render_with_tag(self) -> None:
        """Test that we can render a `with` tag."""
        test_cases = [
            Case(
                description="block scoped variable",
                template=r"{{ x }}{% with x: 'foo' %}{{ x }}{% endwith %}{{ x }}",
                expect="foo",
            ),
            Case(
                description="block scoped alias",
                template=(
                    r"{% with p: collection.products.first %}"
                    r"{{ p.title }}"
                    r"{% endwith %}"
                    r"{{ p.title }}"
                    r"{{ collection.products.first.title }}"
                ),
                expect="A ShoeA Shoe",
                globals={"collection": {"products": [{"title": "A Shoe"}]}},
            ),
            Case(
                description="multiple block scoped variables",
                template=(
                    r"{% with a: 1, b: 3.4 %}"
                    r"{{ a }} + {{ b }} = {{ a | plus: b }}"
                    r"{% endwith %}"
                ),
                expect="1 + 3.4 = 4.4",
            ),
        ]
        self._test(test_cases)
