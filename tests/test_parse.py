"""Liquid template and expression parsing tests."""
# pylint: disable=missing-class-docstring missing-function-docstring

import unittest

from typing import Iterable
from typing import List
from typing import NamedTuple
from typing import Union

from liquid.environment import Environment
from liquid.mode import Mode

from liquid.builtin import literal
from liquid.builtin import statement
from liquid.builtin import if_tag
from liquid.builtin import comment_tag
from liquid.builtin import unless_tag
from liquid.builtin import case_tag
from liquid.builtin import for_tag
from liquid.builtin import tablerow_tag
from liquid.builtin import capture_tag
from liquid.builtin import cycle_tag
from liquid.builtin import assign_tag
from liquid.builtin import increment_tag
from liquid.builtin import decrement_tag
from liquid.builtin import echo_tag
from liquid.builtin import include_tag
from liquid.builtin import render_tag
from liquid.builtin import ifchanged_tag


class Case(NamedTuple):
    description: str
    template: str
    expect: Union[str, List[str]]
    expect_statements: int = 1

    @property
    def expected(self):
        if isinstance(self.expect, str):
            return [self.expect]
        return self.expect


# pylint: disable=too-many-public-methods
class ParserTestCase(unittest.TestCase):
    def _test(self, test_cases: Iterable[Case], instance, mode: Mode = Mode.STRICT):
        """Helper method for testing lists of `Case`s."""
        env = Environment()
        env.mode = mode

        for case in test_cases:
            with self.subTest(msg=case.description):
                template = env.from_string(case.template)

                self.assertIsNotNone(template)
                self.assertEqual(len(template.tree.statements), case.expect_statements)
                if case.expect_statements:
                    self.assertIsInstance(template.tree.statements[0], instance)
                    self.assertIn(str(template.tree), case.expected)

    def test_template_literal(self):
        """Test that we can parse a template literal."""
        test_cases = [
            Case("plain html", "<HTML>Some text</HTML>", "<HTML>Some text</HTML>"),
        ]

        self._test(test_cases, literal.LiteralNode)

    def test_output_statement(self):
        """Test that we can parse output statements."""
        test_cases = [
            Case("string literal", r"{{ 'hello' }}", "`'hello'`"),
            Case("negative integer", r"{{ -5 }}", ["`(-5)`", "`-5`"]),
            Case("identifier", r"{{ product }}", "`product`"),
            Case(
                "identifier with a filter with args and kwargs",
                r"{{ product.title | default: 'foo', allow_false:true }}",
                "`product.title | default: 'foo', allow_false: True`",
            ),
        ]

        self._test(test_cases, statement.StatementNode)

    def test_illegal_tag(self):
        """Test that we can handle illegal tokens in lax mode."""

        test_cases = [
            Case(
                "unknown tag name",
                "{% foobar some %}{% endfoobar %}",
                "",
                expect_statements=0,
            ),
            Case(
                "unknown tag name with surrounding literal",
                "<HTML>{% foobar %}{% endfoobar %}</HTML>",
                "<HTML></HTML>",
                expect_statements=2,
            ),
        ]

        env = Environment(tolerance=Mode.LAX)

        for case in test_cases:
            with self.subTest(msg=case.description):
                template = env.from_string(case.template)

                self.assertIsNotNone(template)
                self.assertEqual(len(template.tree.statements), case.expect_statements)

                if case.expect_statements:
                    self.assertEqual(str(template.tree), case.expect)

    def test_if_tag(self):
        """Test that we can parse an if expression."""
        test_cases = [
            Case(
                "condition with literal consequence",
                "{% if product == 'foo' %}foo{% endif %}",
                "if (product == 'foo') { foo }",
            ),
            Case(
                "condition with literal consequence and following literal",
                "{% if product == 'foo' %}foo{% endif %} hello",
                "if (product == 'foo') { foo } hello",
                expect_statements=2,
            ),
            Case(
                "condition with literal consequence and literal alternative",
                "{% if product == 'foo' %}foo{% else %}bar{% endif %}",
                "if (product == 'foo') { foo } else { bar }",
            ),
            Case(
                "condition with literal and object consequence",
                "{% if product == 'foo' %}foo {{collection}} bar{% endif %}",
                "if (product == 'foo') { foo `collection` bar }",
            ),
            Case(
                "condition with nested condition in the consequence block",
                (
                    "{% if product == 'foo' %}"
                    "{% if title == 'baz' %}baz{% endif %}"
                    "{% endif %}"
                ),
                "if (product == 'foo') { if (title == 'baz') { baz } }",
            ),
            Case(
                "condition with nested, alternative condition in the consequence block",
                (
                    "{% if product == 'foo' %}{% if title == 'baz' %}baz"
                    "{% else %}bar{% endif %}{% endif %}"
                ),
                "if (product == 'foo') { if (title == 'baz') { baz } else { bar } }",
            ),
            Case(
                "condition with nested condition in the alternative block",
                (
                    "{% if product == 'foo' %}"
                    "foo"
                    "{% else %}"
                    "{% if title == 'baz' %}bar{% endif %}"
                    "{% endif %}"
                ),
                "if (product == 'foo') { foo } else { if (title == 'baz') { bar } }",
            ),
            Case(
                "condition with conditional alternative",
                (
                    "{% if product == 'foo' %}"
                    "foo"
                    "{% elsif product == 'bar' %}"
                    "bar"
                    "{% endif %}"
                ),
                "if (product == 'foo') { foo } elsif (product == 'bar') { bar }",
            ),
            Case(
                "condition with conditional and final alternatives",
                (
                    "{% if product == 'foo' %}"
                    "foo"
                    "{% elsif product == 'bar' %}"
                    "bar"
                    "{% else %}"
                    "baz"
                    "{% endif %}"
                ),
                (
                    "if (product == 'foo') { foo } "
                    "elsif (product == 'bar') { bar } else { baz }"
                ),
            ),
            Case(
                "condition with multiple alternatives",
                (
                    "{% if product == 'foo' %}"
                    "foo"
                    "{% elsif product == 'bar' %}"
                    "bar{% elsif x == 1 %}"
                    "baz"
                    "{% endif %}"
                ),
                (
                    "if (product == 'foo') { foo } "
                    "elsif (product == 'bar') { bar } elsif (x == 1) { baz }"
                ),
            ),
        ]

        self._test(test_cases, if_tag.IfNode)

    def test_default_comment_tag(self):
        """Test that we can parse comment tags."""
        test_cases = [
            Case("simple comment", "{% comment %}foo{% endcomment %}", "/* foo */"),
            Case(
                "commented object",
                "{% comment %}{{ product }}{% endcomment %}",
                "/* product */",
            ),
        ]

        self._test(test_cases, comment_tag.CommentNode)

    def test_base_comment_tag(self):
        """Test that we can parse the space efficient base comment tag."""
        test_cases = [
            Case("simple comment", "{% comment %}foo{% endcomment %}", "/* */"),
            Case(
                "commented object",
                "{% comment %}{{ product }}{% endcomment %}",
                "/* */",
            ),
        ]

        env = Environment()
        env.add_tag(comment_tag.CommentTag)

        for case in test_cases:
            with self.subTest(msg=case.description):
                template = env.from_string(case.template)
                self.assertIn(str(template.tree), case.expected)

    def test_inline_comment_tag(self):
        """Test that we can parse inline comment tags."""
        test_cases = [
            Case("simple comment", "{% # foo %}", "/* foo */"),
            Case(
                "commented object",
                "{% # {{ product }} %}",
                "/* {{ product }} */",
            ),
        ]

        self._test(test_cases, comment_tag.CommentNode)

    def test_unless_tag(self):
        """Test that we can parse `unless` tags."""
        test_cases = [
            Case(
                "simple unless",
                "{% unless x == 1 %}foo{% endunless %}",
                "if !(x == 1) { foo }",
            ),
            Case(
                "unless with object and literal",
                "{% unless x == 1 %}foo {{ title }} bar{% endunless %}",
                "if !(x == 1) { foo `title` bar }",
            ),
            Case(
                "unless with alternative",
                "{% unless true %}foo{% else %}bar{% endunless %}",
                "if !(True) { foo } else { bar }",
            ),
            Case(
                "unless with conditional alternative",
                "{% unless true %}foo{% elsif true %}hello{% else %}bar{% endunless %}",
                "if !(True) { foo } elsif (True) { hello } else { bar }",
            ),
            Case(
                "unless with falsy conditional alternative",
                (
                    r"{% unless true %}foo"
                    r"{% elsif false %}bar"
                    r"{% else %}hello"
                    r"{% endunless %}"
                ),
                "if !(True) { foo } elsif (False) { bar } else { hello }",
            ),
        ]

        self._test(test_cases, unless_tag.UnlessNode)

    def test_case_tag(self):
        """Test that we can parse `case`/`when` tags."""
        test_cases = [
            Case(
                "simple case",
                "{% case title %}{% when 'foo' %}foo{% when 'bar' %}bar{% endcase %}",
                "if (title == 'foo') { foo } elsif (title == 'bar') { bar }",
            ),
            Case(
                "case with default",
                "{% case title %}{% when 'foo' %}foo{% else %}bar{% endcase %}",
                "if (title == 'foo') { foo } else { bar }",
            ),
            Case(
                "case with no whens",
                "{% case title %}{% else %}bar{% endcase %}",
                "if (False) { } else { bar }",
            ),
            Case(
                "case with no whens or default",
                "{% case title %}{% endcase %}",
                "if (False) { }",
            ),
            Case(
                "simple case with whitespace",
                "{% case title %} {% when 'foo' %}foo{% when 'bar' %}bar{% endcase %}",
                "if (title == 'foo') { foo } elsif (title == 'bar') { bar }",
            ),
        ]

        self._test(test_cases, case_tag.CaseNode)

    def test_for_tag(self):
        """Test that we can parse for loop tags."""
        test_cases = [
            Case(
                "simple for loop",
                "{% for prod in collection %}{{ prod.title }}{% endfor %}",
                "for (prod in collection) { `prod.title` }",
            ),
            Case(
                "for loop with default",
                "{% for prod in collection %}{{ prod.title }}{% else %}foo{% endfor %}",
                "for (prod in collection) { `prod.title` } else { foo }",
            ),
            Case(
                "for loop with break",
                (
                    "{% for prod in collection %}"
                    "{% if prod.title %}{{ prod.title }}{% else %}{% break %}"
                    "{% endif %}"
                    "{% endfor %}"
                ),
                (
                    "for (prod in collection) { "
                    "if (prod.title) { `prod.title` } else { `break` } "
                    "}"
                ),
            ),
            Case(
                "for loop with continue",
                (
                    "{% for prod in collection %}"
                    "{% if prod.title %}{{ prod.title }}"
                    "{% else %}{% continue %}"
                    "{% endif %}"
                    "{% endfor %}"
                ),
                (
                    "for (prod in collection) { "
                    "if (prod.title) { `prod.title` } else { `continue` } "
                    "}"
                ),
            ),
            Case(
                "for loop with limit",
                (
                    "{% for prod in collection limit:2 %}"
                    "{% if prod.title %}{{ prod.title }}"
                    "{% else %}{% continue %}"
                    "{% endif %}"
                    "{% endfor %}"
                ),
                (
                    "for (prod in collection limit:2) { "
                    "if (prod.title) { `prod.title` } else { `continue` } "
                    "}"
                ),
            ),
            Case(
                "for loop with offset",
                (
                    "{% for prod in collection offset:1 %}"
                    "{% if prod.title %}{{ prod.title }}"
                    "{% else %}{% continue %}"
                    "{% endif %}"
                    "{% endfor %}"
                ),
                (
                    "for (prod in collection offset:1) { "
                    "if (prod.title) { `prod.title` } else { `continue` } "
                    "}"
                ),
            ),
        ]

        self._test(test_cases, for_tag.ForNode)

    def test_tablerow_tag(self):
        """Test that we can parse tablerow tags."""
        test_cases = [
            Case(
                "simple table row",
                (
                    "{% tablerow prod in collection.products %}"
                    "{{ prod.title }}"
                    "{% endtablerow %}"
                ),
                "tablerow(prod in collection.products) { `prod.title` }",
            ),
            Case(
                "table row with whitespace",
                (
                    "{% tablerow prod in collection.products %} "
                    "{{ prod.title }} "
                    "{% endtablerow %}"
                ),
                "tablerow(prod in collection.products) {  `prod.title`  }",
            ),
            Case(
                "table row with arguments",
                (
                    "{% tablerow prod in collection.products cols:2 limit:3 %}"
                    "{{ prod.title }}"
                    "{% endtablerow %}"
                ),
                "tablerow(prod in collection.products limit:3 cols:2) { `prod.title` }",
            ),
        ]

        self._test(test_cases, tablerow_tag.TablerowNode)

    def test_raw_tag(self):
        """Test that we can parse raw tags."""
        test_cases = [
            Case("raw literal", "{% raw %}foo{% endraw %}", "foo"),
            Case("raw object", "{% raw %}{{ foo }}{% endraw %}", r"{{ foo }}"),
            Case(
                "raw tag",
                "{% raw %}{% assign x = 1 %}{% endraw %}",
                "{% assign x = 1 %}",
            ),
        ]

        self._test(test_cases, literal.LiteralNode)

    def test_capture_tag(self):
        """Test that we can parse capture tags."""
        test_cases = [
            Case(
                "capture literal",
                "{% capture some %}foo{% endcapture %}",
                "var some = { foo }",
            ),
            Case(
                "capture literal and statement",
                (
                    "{% capture greeting %}"
                    "Hello, {{ customer.first_name }}."
                    "{% endcapture %}"
                ),
                "var greeting = { Hello, `customer.first_name`. }",
            ),
        ]

        self._test(test_cases, capture_tag.CaptureNode)

    def test_cycle_tag(self):
        """Test that we can parse cycle tags."""
        test_cases = [
            Case(
                "cycle with no identifier",
                '{% cycle "some", "other" %}',
                "cycle ('some', 'other')",
            ),
            Case(
                "cycle with identifier",
                '{% cycle "foo": "some", "other" %}',
                "cycle ('foo': 'some', 'other')",
            ),
        ]

        self._test(test_cases, cycle_tag.CycleNode)

    def test_assign_tag(self):
        """Test that we can parse assign tags."""
        test_cases = [
            Case(
                "assign a string",
                '{% assign foo = "some" %}',
                "var (foo = 'some')",
            ),
        ]

        self._test(test_cases, assign_tag.AssignNode)

    def test_increment_tag(self):
        """Test that we can parse increment tags."""
        test_cases = [
            Case(
                "increment a named counter",
                "{% increment foo %}",
                "foo += 1",
            ),
        ]

        self._test(test_cases, increment_tag.IncrementNode)

    def test_decrement_tag(self):
        """Test that we can parse decrement tags."""
        test_cases = [
            Case(
                "decrement a named counter",
                "{% decrement foo %}",
                "foo -= 1",
            ),
        ]

        self._test(test_cases, decrement_tag.DecrementNode)

    def test_echo_tag(self):
        """Test that we can parse 'echo' tags."""
        test_cases = [
            Case("string literal", "{% echo 'hello' %}", "`'hello'`"),
            Case("identifier", "{% echo product %}", "`product`"),
            Case(
                "identifier with a filter",
                "{% echo product.title | upcase %}",
                "`product.title | upcase`",
            ),
        ]

        self._test(test_cases, echo_tag.EchoNode)

    def test_include_tag(self):
        """Test that we can parse 'include' tags."""
        test_cases = [
            Case(
                "simple string literal", "{% include 'product' %}", "include('product')"
            ),
            Case(
                "name from identifier", "{% include some.name %}", "include(some.name)"
            ),
            Case(
                "string literal with variable",
                "{% include 'product' with products[0] %}",
                "include('product' with products.0)",
            ),
            Case(
                "string literal with aliased variable",
                "{% include 'product' with products[0] as foo %}",
                "include('product' with products.0 as foo)",
            ),
            Case(
                "string literal with keyword argument",
                "{% include 'product', foo: 'bar' %}",
                "include('product', foo='bar')",
            ),
        ]

        self._test(test_cases, include_tag.IncludeNode)

    def test_render_tag(self):
        """Test that we can parse 'render' tags."""
        test_cases = [
            Case(
                "simple string literal", "{% render 'product' %}", "render('product')"
            ),
            Case(
                "string literal with variable",
                "{% render 'product' with products[0] %}",
                "render('product' with products.0)",
            ),
            Case(
                "string literal with aliased variable",
                "{% render 'product' with products[0] as foo %}",
                "render('product' with products.0 as foo)",
            ),
            Case(
                "string literal with keyword argument",
                "{% render 'product', foo: 'bar' %}",
                "render('product', foo='bar')",
            ),
        ]

        self._test(test_cases, render_tag.RenderNode)

    def test_ifchanged_tag(self):
        """Test that we can parse ifchanged tags."""
        test_cases = [
            Case(
                "initial state - no change",
                "{% ifchanged %}hello{% endifchanged %}",
                r"ifchanged { hello }",
            ),
        ]

        self._test(test_cases, ifchanged_tag.IfChangedNode)
