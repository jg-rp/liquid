"""Test tokenizing of liquid templates and expressions."""

from typing import Any
from typing import NamedTuple
from unittest import TestCase

from liquid.environment import Environment
from liquid.exceptions import LiquidSyntaxError
from liquid.lex import get_lexer
from liquid.lex import tokenize_liquid_expression
from liquid.stream import TokenStream
from liquid.token import TOKEN_CONTENT
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_OUTOUT
from liquid.token import TOKEN_TAG
from liquid.token import Token


class Case(NamedTuple):
    description: str
    source: str
    expect: Any


class LiquidLexerTestCase(TestCase):
    """Liquid lexer test cases."""

    def setUp(self) -> None:
        self.env = Environment()

    def _test(self, test_cases: list[Case]) -> None:
        tokenize = get_lexer(
            self.env.tag_start_string,
            self.env.tag_end_string,
            self.env.statement_start_string,
            self.env.statement_end_string,
        )

        for case in test_cases:
            with self.subTest(msg=case.description):
                tokens = TokenStream(tokenize(case.source))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)

    def test_lex_template(self) -> None:
        """Test that the lexer can tokenize literals, objects and tags."""
        test_cases = [
            Case(
                "simple template literal",
                "<HTML>some</HTML>",
                [Token(1, TOKEN_CONTENT, "<HTML>some</HTML>")],
            ),
            Case(
                "template literal and object",
                r"<HTML>{{ other }}</HTML>",
                [
                    Token(1, TOKEN_CONTENT, "<HTML>"),
                    Token(1, TOKEN_OUTOUT, "other"),
                    Token(1, TOKEN_CONTENT, "</HTML>"),
                ],
            ),
            Case(
                "template literal and object with filters",
                r"<HTML>{{ other | upper }}</HTML>",
                [
                    Token(1, TOKEN_CONTENT, "<HTML>"),
                    Token(1, TOKEN_OUTOUT, "other | upper"),
                    Token(1, TOKEN_CONTENT, "</HTML>"),
                ],
            ),
            Case(
                "template literal and object with whitespace control",
                r"<HTML>{{- other -}}</HTML>",
                [
                    Token(1, TOKEN_CONTENT, "<HTML>"),
                    Token(1, TOKEN_OUTOUT, "other"),
                    Token(1, TOKEN_CONTENT, "</HTML>"),
                ],
            ),
            Case(
                "template literal and control flow",
                "<HTML>{% if product %}some{% else %}other{% endif %}</HTML>",
                [
                    Token(1, TOKEN_CONTENT, "<HTML>"),
                    Token(1, TOKEN_TAG, "if"),
                    Token(1, TOKEN_EXPRESSION, "product"),
                    Token(1, TOKEN_CONTENT, "some"),
                    Token(1, TOKEN_TAG, "else"),
                    Token(1, TOKEN_CONTENT, "other"),
                    Token(1, TOKEN_TAG, "endif"),
                    Token(1, TOKEN_CONTENT, "</HTML>"),
                ],
            ),
            Case(
                "template literal and control flow and inconsistent whitespace",
                "<HTML>{%if  product %}some{% else  %}other{% endif%}</HTML>",
                [
                    Token(1, TOKEN_CONTENT, "<HTML>"),
                    Token(1, TOKEN_TAG, "if"),
                    Token(1, TOKEN_EXPRESSION, "product"),
                    Token(1, TOKEN_CONTENT, "some"),
                    Token(1, TOKEN_TAG, "else"),
                    Token(1, TOKEN_CONTENT, "other"),
                    Token(1, TOKEN_TAG, "endif"),
                    Token(1, TOKEN_CONTENT, "</HTML>"),
                ],
            ),
            Case(
                "newlines inside tags",
                "<HTML>{%if\nproduct %}some{% else\n %}other{% endif%}</HTML>",
                [
                    Token(1, TOKEN_CONTENT, "<HTML>"),
                    Token(1, TOKEN_TAG, "if"),
                    Token(2, TOKEN_EXPRESSION, "product"),
                    Token(2, TOKEN_CONTENT, "some"),
                    Token(2, TOKEN_TAG, "else"),
                    Token(3, TOKEN_CONTENT, "other"),
                    Token(3, TOKEN_TAG, "endif"),
                    Token(3, TOKEN_CONTENT, "</HTML>"),
                ],
            ),
            Case(
                "carriage return inside tags",
                "<HTML>{%if\rproduct %}some{% else\r %}other{% endif%}</HTML>",
                [
                    Token(1, TOKEN_CONTENT, "<HTML>"),
                    Token(1, TOKEN_TAG, "if"),
                    Token(1, TOKEN_EXPRESSION, "product"),
                    Token(1, TOKEN_CONTENT, "some"),
                    Token(1, TOKEN_TAG, "else"),
                    Token(1, TOKEN_CONTENT, "other"),
                    Token(1, TOKEN_TAG, "endif"),
                    Token(1, TOKEN_CONTENT, "</HTML>"),
                ],
            ),
            Case(
                "carriage return and newline inside tags",
                "<HTML>{%if\r\nproduct %}some{% else\r\n %}other{% endif%}</HTML>",
                [
                    Token(1, TOKEN_CONTENT, "<HTML>"),
                    Token(1, TOKEN_TAG, "if"),
                    Token(2, TOKEN_EXPRESSION, "product"),
                    Token(2, TOKEN_CONTENT, "some"),
                    Token(2, TOKEN_TAG, "else"),
                    Token(3, TOKEN_CONTENT, "other"),
                    Token(3, TOKEN_TAG, "endif"),
                    Token(3, TOKEN_CONTENT, "</HTML>"),
                ],
            ),
            Case(
                "inconsistent whitespace and whitespace control",
                "<HTML>{%if  product %}some  {%- else  %}other{% endif -%}</HTML>",
                [
                    Token(1, TOKEN_CONTENT, "<HTML>"),
                    Token(1, TOKEN_TAG, "if"),
                    Token(1, TOKEN_EXPRESSION, "product"),
                    Token(1, TOKEN_CONTENT, "some"),
                    Token(1, TOKEN_TAG, "else"),
                    Token(1, TOKEN_CONTENT, "other"),
                    Token(1, TOKEN_TAG, "endif"),
                    Token(1, TOKEN_CONTENT, "</HTML>"),
                ],
            ),
            Case(
                "line numbers",
                ("Some\n\n{{ obj }}\n{% assign x = 1 %}"),
                [
                    Token(1, TOKEN_CONTENT, "Some\n\n"),
                    Token(3, TOKEN_OUTOUT, "obj"),
                    Token(3, TOKEN_CONTENT, "\n"),
                    Token(4, TOKEN_TAG, "assign"),
                    Token(4, TOKEN_EXPRESSION, "x = 1"),
                ],
            ),
            Case(
                "line numbers with carriage return",
                ("Some\r\n\r\n{{ obj }}\r\n{% assign x = 1 %}"),
                [
                    Token(1, TOKEN_CONTENT, "Some\r\n\r\n"),
                    Token(3, TOKEN_OUTOUT, "obj"),
                    Token(3, TOKEN_CONTENT, "\r\n"),
                    Token(4, TOKEN_TAG, "assign"),
                    Token(4, TOKEN_EXPRESSION, "x = 1"),
                ],
            ),
            Case(
                "line numbers and whitespace control",
                "Some\n\n{{- obj -}}\n{% assign x = 1 %}",
                [
                    Token(1, TOKEN_CONTENT, "Some"),
                    Token(3, TOKEN_OUTOUT, "obj"),
                    Token(4, TOKEN_TAG, "assign"),
                    Token(4, TOKEN_EXPRESSION, "x = 1"),
                ],
            ),
            Case(
                "raw",
                "{% raw %}{{ hello }} %}{% {{ {% endraw %}",
                [
                    Token(1, TOKEN_CONTENT, r"{{ hello }} %}{% {{ "),
                ],
            ),
            Case(
                "assign",
                "{% assign foo = 'bar' %}",
                [
                    Token(1, TOKEN_TAG, "assign"),
                    Token(1, TOKEN_EXPRESSION, "foo = 'bar'"),
                ],
            ),
            Case(
                "assign a range literal",
                "{% assign foo = (1..5) %}",
                [
                    Token(1, TOKEN_TAG, "assign"),
                    Token(1, TOKEN_EXPRESSION, "foo = (1..5)"),
                ],
            ),
            Case(
                "capture",
                (
                    "{% capture greeting %}"
                    "Hello, {{ customer.first_name }}."
                    "{% endcapture %}"
                ),
                [
                    Token(1, TOKEN_TAG, "capture"),
                    Token(1, TOKEN_EXPRESSION, "greeting"),
                    Token(1, TOKEN_CONTENT, "Hello, "),
                    Token(1, TOKEN_OUTOUT, "customer.first_name"),
                    Token(1, TOKEN_CONTENT, "."),
                    Token(1, TOKEN_TAG, "endcapture"),
                ],
            ),
            Case(
                "inline comment tag",
                "{% # this is a comment %}",
                [
                    Token(1, TOKEN_TAG, "#"),
                    Token(1, TOKEN_EXPRESSION, "this is a comment"),
                ],
            ),
        ]

        self._test(test_cases)

    def test_lex_liquid_expression(self) -> None:
        """Test that the liquid expression lexer can tokenize line delimited
        expressions."""
        test_cases = [
            Case(
                "for loop",
                "for i in (0..5)\necho i\nendfor",
                [
                    Token(1, TOKEN_TAG, "for"),
                    Token(1, TOKEN_EXPRESSION, "i in (0..5)"),
                    Token(2, TOKEN_TAG, "echo"),
                    Token(2, TOKEN_EXPRESSION, "i"),
                    Token(3, TOKEN_TAG, "endfor"),
                ],
            ),
            Case(
                "case",
                "\n".join(
                    [
                        "case section.blocks.size",
                        "when 1",
                        "   assign column_size = ''",
                        "when 2",
                        "   assign column_size = 'one-half'",
                        "when 3",
                        "   assign column_size = 'one-third'",
                        "else",
                        "   assign column_size = 'one-quarter'",
                        "endcase",
                    ]
                ),
                [
                    Token(1, TOKEN_TAG, "case"),
                    Token(1, TOKEN_EXPRESSION, "section.blocks.size"),
                    Token(2, TOKEN_TAG, "when"),
                    Token(2, TOKEN_EXPRESSION, "1"),
                    Token(3, TOKEN_TAG, "assign"),
                    Token(3, TOKEN_EXPRESSION, "column_size = ''"),
                    Token(4, TOKEN_TAG, "when"),
                    Token(4, TOKEN_EXPRESSION, "2"),
                    Token(5, TOKEN_TAG, "assign"),
                    Token(5, TOKEN_EXPRESSION, "column_size = 'one-half'"),
                    Token(6, TOKEN_TAG, "when"),
                    Token(6, TOKEN_EXPRESSION, "3"),
                    Token(7, TOKEN_TAG, "assign"),
                    Token(7, TOKEN_EXPRESSION, "column_size = 'one-third'"),
                    Token(8, TOKEN_TAG, "else"),
                    Token(9, TOKEN_TAG, "assign"),
                    Token(9, TOKEN_EXPRESSION, "column_size = 'one-quarter'"),
                    Token(10, TOKEN_TAG, "endcase"),
                ],
            ),
            Case(
                "conditional",
                "\n".join(
                    [
                        "if product.featured_image",
                        "   echo product.featured_image | img_tag",
                        "else",
                        "   echo 'product-1' | placeholder_svg_tag",
                        "endif",
                    ]
                ),
                [
                    Token(1, TOKEN_TAG, "if"),
                    Token(1, TOKEN_EXPRESSION, "product.featured_image"),
                    Token(2, TOKEN_TAG, "echo"),
                    Token(2, TOKEN_EXPRESSION, "product.featured_image | img_tag"),
                    Token(3, TOKEN_TAG, "else"),
                    Token(4, TOKEN_TAG, "echo"),
                    Token(4, TOKEN_EXPRESSION, "'product-1' | placeholder_svg_tag"),
                    Token(5, TOKEN_TAG, "endif"),
                ],
            ),
            Case(
                "multiple tags",
                "\n".join(
                    [
                        "if product.featured_image",
                        "   echo product.featured_image | img_tag",
                        "else",
                        "   echo 'product-1' | placeholder_svg_tag",
                        "endif",
                        "for i in (0..5)",
                        "   echo i",
                        "endfor",
                    ]
                ),
                [
                    Token(1, TOKEN_TAG, "if"),
                    Token(1, TOKEN_EXPRESSION, "product.featured_image"),
                    Token(2, TOKEN_TAG, "echo"),
                    Token(2, TOKEN_EXPRESSION, "product.featured_image | img_tag"),
                    Token(3, TOKEN_TAG, "else"),
                    Token(4, TOKEN_TAG, "echo"),
                    Token(4, TOKEN_EXPRESSION, "'product-1' | placeholder_svg_tag"),
                    Token(5, TOKEN_TAG, "endif"),
                    Token(6, TOKEN_TAG, "for"),
                    Token(6, TOKEN_EXPRESSION, "i in (0..5)"),
                    Token(7, TOKEN_TAG, "echo"),
                    Token(7, TOKEN_EXPRESSION, "i"),
                    Token(8, TOKEN_TAG, "endfor"),
                ],
            ),
            Case(
                "liquid in liquid",
                "liquid\necho 'foo'",
                [
                    Token(1, TOKEN_TAG, "liquid"),
                    Token(2, TOKEN_TAG, "echo"),
                    Token(2, TOKEN_EXPRESSION, "'foo'"),
                ],
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize_liquid_expression(case.source))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)

    def test_lex_errors(self) -> None:
        """Test that the lexer does not fall over at common errors."""
        test_cases = [
            Case(
                description="no close statement bracket",
                source=r"text {{method oh no!",
                expect=[
                    Token(1, TOKEN_CONTENT, "text "),
                    Token(1, TOKEN_OUTOUT, "method oh no!"),
                ],
            ),
            Case(
                description="no close statement bracket eof",
                source=r"text {{",
                expect=[
                    Token(1, TOKEN_CONTENT, "text "),
                    Token(1, TOKEN_OUTOUT, ""),
                ],
            ),
            Case(
                description="no close tag eof",
                source=r"text {%",
                expect=[
                    Token(1, TOKEN_CONTENT, "text "),
                    Token(1, TOKEN_TAG, ""),
                ],
            ),
            Case(
                description="single close statement bracket",
                source=r"text {{method} oh no!",
                expect=[
                    Token(1, TOKEN_CONTENT, "text "),
                    Token(1, TOKEN_OUTOUT, "method} oh no!"),
                ],
            ),
            Case(
                description="single close statement bracket",
                source=r"text {{ %} oh no!",
                expect=[
                    Token(1, TOKEN_CONTENT, "text "),
                    Token(1, TOKEN_OUTOUT, "%} oh no!"),
                ],
            ),
        ]

        tokenize = get_lexer(
            self.env.tag_start_string,
            self.env.tag_end_string,
            self.env.statement_start_string,
            self.env.statement_end_string,
        )

        for case in test_cases:
            with self.subTest(msg=case.description):
                with self.assertRaises(LiquidSyntaxError):
                    list(tokenize(case.source))
