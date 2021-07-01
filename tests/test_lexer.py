from unittest import TestCase
from typing import NamedTuple, Any

from liquid.environment import Environment
from liquid.stream import TokenStream

from liquid.exceptions import LiquidSyntaxError

from liquid.lex import tokenize_liquid_expression
from liquid.lex import tokenize_loop_expression
from liquid.lex import tokenize_filtered_expression
from liquid.lex import tokenize_boolean_expression
from liquid.lex import tokenize_include_expression
from liquid.lex import get_lexer

from liquid.token import Token
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_STATEMENT
from liquid.token import TOKEN_LITERAL
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_EMPTY
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_NULL
from liquid.token import TOKEN_BLANK
from liquid.token import TOKEN_NEGATIVE
from liquid.token import TOKEN_TRUE
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_CONTAINS
from liquid.token import TOKEN_IN
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_RANGE
from liquid.token import TOKEN_LIMIT
from liquid.token import TOKEN_OFFSET
from liquid.token import TOKEN_REVERSED
from liquid.token import TOKEN_CONTINUE
from liquid.token import TOKEN_PIPE
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_RBRACKET
from liquid.token import TOKEN_AND
from liquid.token import TOKEN_OR
from liquid.token import TOKEN_EQ
from liquid.token import TOKEN_NE
from liquid.token import TOKEN_LG
from liquid.token import TOKEN_GT
from liquid.token import TOKEN_LE
from liquid.token import TOKEN_GE
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_WITH
from liquid.token import TOKEN_AS
from liquid.token import TOKEN_FOR


class Case(NamedTuple):
    description: str
    source: str
    expect: Any


class LiquidLexerTestCase(TestCase):
    """Liquid lexer test cases."""

    def setUp(self) -> None:
        self.env = Environment()

    def _test(self, test_cases):
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

    def test_lex_template(self):
        """Test that the lexer can tokenize literals, objects and tags."""

        test_cases = [
            Case(
                "simple template literal",
                "<HTML>some</HTML>",
                [Token(1, TOKEN_LITERAL, "<HTML>some</HTML>")],
            ),
            Case(
                "template literal and object",
                r"<HTML>{{ other }}</HTML>",
                [
                    Token(1, TOKEN_LITERAL, "<HTML>"),
                    Token(1, TOKEN_STATEMENT, "other"),
                    Token(1, TOKEN_LITERAL, "</HTML>"),
                ],
            ),
            Case(
                "template literal and object with filters",
                r"<HTML>{{ other | upper }}</HTML>",
                [
                    Token(1, TOKEN_LITERAL, "<HTML>"),
                    Token(1, TOKEN_STATEMENT, "other | upper"),
                    Token(1, TOKEN_LITERAL, "</HTML>"),
                ],
            ),
            Case(
                "template literal and object with whitespace control",
                r"<HTML>{{- other -}}</HTML>",
                [
                    Token(1, TOKEN_LITERAL, "<HTML>"),
                    Token(1, TOKEN_STATEMENT, "other"),
                    Token(1, TOKEN_LITERAL, "</HTML>"),
                ],
            ),
            Case(
                "template literal and control flow",
                "<HTML>{% if product %}some{% else %}other{% endif %}</HTML>",
                [
                    Token(1, TOKEN_LITERAL, "<HTML>"),
                    Token(1, TOKEN_TAG, "if"),
                    Token(1, TOKEN_EXPRESSION, "product"),
                    Token(1, TOKEN_LITERAL, "some"),
                    Token(1, TOKEN_TAG, "else"),
                    Token(1, TOKEN_LITERAL, "other"),
                    Token(1, TOKEN_TAG, "endif"),
                    Token(1, TOKEN_LITERAL, "</HTML>"),
                ],
            ),
            Case(
                "template literal and control flow and inconsistent whitespace",
                "<HTML>{%if  product %}some{% else  %}other{% endif%}</HTML>",
                [
                    Token(1, TOKEN_LITERAL, "<HTML>"),
                    Token(1, TOKEN_TAG, "if"),
                    Token(1, TOKEN_EXPRESSION, "product"),
                    Token(1, TOKEN_LITERAL, "some"),
                    Token(1, TOKEN_TAG, "else"),
                    Token(1, TOKEN_LITERAL, "other"),
                    Token(1, TOKEN_TAG, "endif"),
                    Token(1, TOKEN_LITERAL, "</HTML>"),
                ],
            ),
            Case(
                "newlines inside tags",
                "<HTML>{%if\nproduct %}some{% else\n %}other{% endif%}</HTML>",
                [
                    Token(1, TOKEN_LITERAL, "<HTML>"),
                    Token(1, TOKEN_TAG, "if"),
                    Token(1, TOKEN_EXPRESSION, "product"),
                    Token(2, TOKEN_LITERAL, "some"),
                    Token(2, TOKEN_TAG, "else"),
                    Token(3, TOKEN_LITERAL, "other"),
                    Token(3, TOKEN_TAG, "endif"),
                    Token(3, TOKEN_LITERAL, "</HTML>"),
                ],
            ),
            Case(
                "carriage return inside tags",
                "<HTML>{%if\rproduct %}some{% else\r %}other{% endif%}</HTML>",
                [
                    Token(1, TOKEN_LITERAL, "<HTML>"),
                    Token(1, TOKEN_TAG, "if"),
                    Token(1, TOKEN_EXPRESSION, "product"),
                    Token(1, TOKEN_LITERAL, "some"),
                    Token(1, TOKEN_TAG, "else"),
                    Token(1, TOKEN_LITERAL, "other"),
                    Token(1, TOKEN_TAG, "endif"),
                    Token(1, TOKEN_LITERAL, "</HTML>"),
                ],
            ),
            Case(
                "carriage return and newline inside tags",
                "<HTML>{%if\r\nproduct %}some{% else\r\n %}other{% endif%}</HTML>",
                [
                    Token(1, TOKEN_LITERAL, "<HTML>"),
                    Token(1, TOKEN_TAG, "if"),
                    Token(1, TOKEN_EXPRESSION, "product"),
                    Token(2, TOKEN_LITERAL, "some"),
                    Token(2, TOKEN_TAG, "else"),
                    Token(3, TOKEN_LITERAL, "other"),
                    Token(3, TOKEN_TAG, "endif"),
                    Token(3, TOKEN_LITERAL, "</HTML>"),
                ],
            ),
            Case(
                "template literal and control flow, inconsistent whitespace and whitespace control",
                "<HTML>{%if  product %}some  {%- else  %}other{% endif -%}</HTML>",
                [
                    Token(1, TOKEN_LITERAL, "<HTML>"),
                    Token(1, TOKEN_TAG, "if"),
                    Token(1, TOKEN_EXPRESSION, "product"),
                    Token(1, TOKEN_LITERAL, "some"),
                    Token(1, TOKEN_TAG, "else"),
                    Token(1, TOKEN_LITERAL, "other"),
                    Token(1, TOKEN_TAG, "endif"),
                    Token(1, TOKEN_LITERAL, "</HTML>"),
                ],
            ),
            Case(
                "line numbers",
                ("Some\n\n{{ obj }}\n{% assign x = 1 %}"),
                [
                    Token(1, TOKEN_LITERAL, "Some\n\n"),
                    Token(3, TOKEN_STATEMENT, "obj"),
                    Token(3, TOKEN_LITERAL, "\n"),
                    Token(4, TOKEN_TAG, "assign"),
                    Token(4, TOKEN_EXPRESSION, "x = 1"),
                ],
            ),
            Case(
                "line numbers with carriage return",
                ("Some\r\n\r\n{{ obj }}\r\n{% assign x = 1 %}"),
                [
                    Token(1, TOKEN_LITERAL, "Some\r\n\r\n"),
                    Token(3, TOKEN_STATEMENT, "obj"),
                    Token(3, TOKEN_LITERAL, "\r\n"),
                    Token(4, TOKEN_TAG, "assign"),
                    Token(4, TOKEN_EXPRESSION, "x = 1"),
                ],
            ),
            Case(
                "line numbers and whitespace control",
                "Some\n\n{{- obj -}}\n{% assign x = 1 %}",
                [
                    Token(1, TOKEN_LITERAL, "Some"),
                    Token(3, TOKEN_STATEMENT, "obj"),
                    Token(4, TOKEN_TAG, "assign"),
                    Token(4, TOKEN_EXPRESSION, "x = 1"),
                ],
            ),
            Case(
                "raw",
                "{% raw %}{{ hello }} %}{% {{ {% endraw %}",
                [
                    Token(1, TOKEN_LITERAL, r"{{ hello }} %}{% {{ "),
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
                "capture",
                "{% capture greeting %}Hello, {{ customer.first_name }}.{% endcapture %}",
                [
                    Token(1, TOKEN_TAG, "capture"),
                    Token(1, TOKEN_EXPRESSION, "greeting"),
                    Token(1, TOKEN_LITERAL, "Hello, "),
                    Token(1, TOKEN_STATEMENT, "customer.first_name"),
                    Token(1, TOKEN_LITERAL, "."),
                    Token(1, TOKEN_TAG, "endcapture"),
                ],
            ),
        ]

        self._test(test_cases)

    def test_lex_liquid_expression(self):
        """Test that the liquid expression lexer can tokenize line delimited expressions."""

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
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize_liquid_expression(case.source))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)

    def test_lex_errors(self):
        """Test that the lexer does not fall over at common errors."""

        test_cases = [
            Case(
                description="no close statement bracket",
                source=r"text {{method oh no!",
                expect=[
                    Token(1, TOKEN_LITERAL, "text "),
                    Token(1, TOKEN_STATEMENT, "method oh no!"),
                ],
            ),
            Case(
                description="no close statement bracket eof",
                source=r"text {{",
                expect=[
                    Token(1, TOKEN_LITERAL, "text "),
                    Token(1, TOKEN_STATEMENT, ""),
                ],
            ),
            Case(
                description="no close tag eof",
                source=r"text {%",
                expect=[
                    Token(1, TOKEN_LITERAL, "text "),
                    Token(1, TOKEN_TAG, ""),
                ],
            ),
            Case(
                description="single close statement bracket",
                source=r"text {{method} oh no!",
                expect=[
                    Token(1, TOKEN_LITERAL, "text "),
                    Token(1, TOKEN_STATEMENT, "method} oh no!"),
                ],
            ),
            Case(
                description="single close statement bracket",
                source=r"text {{ %} oh no!",
                expect=[
                    Token(1, TOKEN_LITERAL, "text "),
                    Token(1, TOKEN_STATEMENT, "%} oh no!"),
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

    def test_lex_output_statement_expression(self):
        """Test that the expression lexer can tokenize statement expressions."""
        test_cases = [
            Case(
                "string literal single quotes",
                "'foobar'",
                [Token(1, TOKEN_STRING, "foobar")],
            ),
            Case(
                "string literal double quotes",
                "'foobar'",
                [Token(1, TOKEN_STRING, "foobar")],
            ),
            Case(
                "integer literal",
                "7",
                [Token(1, TOKEN_INTEGER, "7")],
            ),
            Case(
                "negative integer literal",
                "-7",
                [
                    Token(1, TOKEN_NEGATIVE, "-"),
                    Token(1, TOKEN_INTEGER, "7"),
                ],
            ),
            Case(
                "float literal",
                "3.14",
                [Token(1, TOKEN_FLOAT, "3.14")],
            ),
            Case(
                "negative float literal",
                "-3.14",
                [
                    Token(1, TOKEN_NEGATIVE, "-"),
                    Token(1, TOKEN_FLOAT, "3.14"),
                ],
            ),
            Case(
                "lone identifier",
                "collection",
                [Token(1, TOKEN_IDENTIFIER, "collection")],
            ),
            Case(
                "lone identifier with a hyphen",
                "main-collection",
                [Token(1, TOKEN_IDENTIFIER, "main-collection")],
            ),
            Case(
                "chained identifier",
                "collection.products",
                [
                    Token(1, TOKEN_IDENTIFIER, "collection"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "products"),
                ],
            ),
            Case(
                "chained identifier by double quoted key",
                'collection["products"]',
                [
                    Token(1, TOKEN_IDENTIFIER, "collection"),
                    Token(1, TOKEN_LBRACKET, "["),
                    Token(1, TOKEN_STRING, "products"),
                    Token(1, TOKEN_RBRACKET, "]"),
                ],
            ),
            Case(
                "chained identifier by single quoted key",
                "collection['products']",
                [
                    Token(1, TOKEN_IDENTIFIER, "collection"),
                    Token(1, TOKEN_LBRACKET, "["),
                    Token(1, TOKEN_STRING, "products"),
                    Token(1, TOKEN_RBRACKET, "]"),
                ],
            ),
            Case(
                "chained identifier with array index",
                "collection.products[0]",
                [
                    Token(1, TOKEN_IDENTIFIER, "collection"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "products"),
                    Token(1, TOKEN_LBRACKET, "["),
                    Token(1, TOKEN_INTEGER, "0"),
                    Token(1, TOKEN_RBRACKET, "]"),
                ],
            ),
            Case(
                "chained identifier with array index from identifier",
                "collection.products[i]",
                [
                    Token(1, TOKEN_IDENTIFIER, "collection"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "products"),
                    Token(1, TOKEN_LBRACKET, "["),
                    Token(1, TOKEN_IDENTIFIER, "i"),
                    Token(1, TOKEN_RBRACKET, "]"),
                ],
            ),
            Case(
                "string literal with filter",
                "'foo' | upcase",
                [
                    Token(1, TOKEN_STRING, "foo"),
                    Token(1, TOKEN_PIPE, "|"),
                    Token(1, TOKEN_IDENTIFIER, "upcase"),
                ],
            ),
            Case(
                "identifier with filter",
                "collection.title | upcase",
                [
                    Token(1, TOKEN_IDENTIFIER, "collection"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "title"),
                    Token(1, TOKEN_PIPE, "|"),
                    Token(1, TOKEN_IDENTIFIER, "upcase"),
                ],
            ),
            Case(
                "integer literal with filter and integer argument",
                "4 | at_least: 5",
                [
                    Token(1, TOKEN_INTEGER, "4"),
                    Token(1, TOKEN_PIPE, "|"),
                    Token(1, TOKEN_IDENTIFIER, "at_least"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_INTEGER, "5"),
                ],
            ),
            Case(
                "float literal with filter and float argument",
                "4.1 | divided_by: 5.2",
                [
                    Token(1, TOKEN_FLOAT, "4.1"),
                    Token(1, TOKEN_PIPE, "|"),
                    Token(1, TOKEN_IDENTIFIER, "divided_by"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_FLOAT, "5.2"),
                ],
            ),
            Case(
                "string literal with filter and string argument",
                "'foo' | append: 'bar'",
                [
                    Token(1, TOKEN_STRING, "foo"),
                    Token(1, TOKEN_PIPE, "|"),
                    Token(1, TOKEN_IDENTIFIER, "append"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_STRING, "bar"),
                ],
            ),
            Case(
                "string literal with filter and identifier argument",
                "'foo' | append: collection.title",
                [
                    Token(1, TOKEN_STRING, "foo"),
                    Token(1, TOKEN_PIPE, "|"),
                    Token(1, TOKEN_IDENTIFIER, "append"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_IDENTIFIER, "collection"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "title"),
                ],
            ),
            Case(
                "string literal with filter and multiple arguments",
                '"Liquid" | slice: 2, 5',
                [
                    Token(1, TOKEN_STRING, "Liquid"),
                    Token(1, TOKEN_PIPE, "|"),
                    Token(1, TOKEN_IDENTIFIER, "slice"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_INTEGER, "2"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_INTEGER, "5"),
                ],
            ),
            Case(
                "string literal with multiple filters",
                '"Liquid" | slice: 2, 5 | upcase',
                [
                    Token(1, TOKEN_STRING, "Liquid"),
                    Token(1, TOKEN_PIPE, "|"),
                    Token(1, TOKEN_IDENTIFIER, "slice"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_INTEGER, "2"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_INTEGER, "5"),
                    Token(1, TOKEN_PIPE, "|"),
                    Token(1, TOKEN_IDENTIFIER, "upcase"),
                ],
            ),
            Case(
                "inconsistent whitespace",
                ' "Liquid"   |slice: 2,5',
                [
                    Token(1, TOKEN_STRING, "Liquid"),
                    Token(1, TOKEN_PIPE, "|"),
                    Token(1, TOKEN_IDENTIFIER, "slice"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_INTEGER, "2"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_INTEGER, "5"),
                ],
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize_filtered_expression(case.source))

                self.assertTrue(len(tokens) == len(case.expect))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)

    def test_lex_boolean_expression(self):
        """Test that we can tokenize comparison expressions."""
        test_cases = [
            Case(
                "literal boolean",
                "false == true",
                [
                    Token(1, TOKEN_FALSE, "false"),
                    Token(1, TOKEN_EQ, "=="),
                    Token(1, TOKEN_TRUE, "true"),
                ],
            ),
            Case(
                "not nil identifier",
                "user != nil",
                [
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_NE, "!="),
                    Token(1, TOKEN_NIL, "nil"),
                ],
            ),
            Case(
                "not null identifier",
                "user != null",
                [
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_NE, "!="),
                    Token(1, TOKEN_NULL, "null"),
                ],
            ),
            Case(
                "alternate not nil",
                "user <> nil",
                [
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_LG, "<>"),
                    Token(1, TOKEN_NIL, "nil"),
                ],
            ),
            Case(
                "identifier equals string literal",
                "user.name == 'brian'",
                [
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "name"),
                    Token(1, TOKEN_EQ, "=="),
                    Token(1, TOKEN_STRING, "brian"),
                ],
            ),
            Case(
                "equality with or",
                "user.name == 'bill' or user.name == 'bob'",
                [
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "name"),
                    Token(1, TOKEN_EQ, "=="),
                    Token(1, TOKEN_STRING, "bill"),
                    Token(1, TOKEN_OR, "or"),
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "name"),
                    Token(1, TOKEN_EQ, "=="),
                    Token(1, TOKEN_STRING, "bob"),
                ],
            ),
            Case(
                "equality with and",
                "user.name == 'bob' and user.age > 45",
                [
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "name"),
                    Token(1, TOKEN_EQ, "=="),
                    Token(1, TOKEN_STRING, "bob"),
                    Token(1, TOKEN_AND, "and"),
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "age"),
                    Token(1, TOKEN_GT, ">"),
                    Token(1, TOKEN_INTEGER, "45"),
                ],
            ),
            Case(
                "greater than or equal to integer literal",
                "user.age >= 21",
                [
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "age"),
                    Token(1, TOKEN_GE, ">="),
                    Token(1, TOKEN_INTEGER, "21"),
                ],
            ),
            Case(
                "less than or equal to integer literal",
                "user.age <= 21",
                [
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "age"),
                    Token(1, TOKEN_LE, "<="),
                    Token(1, TOKEN_INTEGER, "21"),
                ],
            ),
            Case(
                "identifier contains string",
                "product.tags contains 'sale'",
                [
                    Token(1, TOKEN_IDENTIFIER, "product"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "tags"),
                    Token(1, TOKEN_CONTAINS, "contains"),
                    Token(1, TOKEN_STRING, "sale"),
                ],
            ),
            Case(
                "identifier equals blank",
                "product.title == blank",
                [
                    Token(1, TOKEN_IDENTIFIER, "product"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "title"),
                    Token(1, TOKEN_EQ, "=="),
                    Token(1, TOKEN_BLANK, "blank"),
                ],
            ),
            Case(
                "identifier equals empty",
                "product.title == empty",
                [
                    Token(1, TOKEN_IDENTIFIER, "product"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "title"),
                    Token(1, TOKEN_EQ, "=="),
                    Token(1, TOKEN_EMPTY, "empty"),
                ],
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize_boolean_expression(case.source))

                self.assertTrue(len(tokens) == len(case.expect))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)

    def test_lex_loop_expression(self):
        """Test that we can tokenize loop expressions."""
        test_cases = [
            Case(
                "loop over identifier",
                "product in collection.products",
                [
                    Token(1, TOKEN_IDENTIFIER, "product"),
                    Token(1, TOKEN_IN, "in"),
                    Token(1, TOKEN_IDENTIFIER, "collection"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "products"),
                ],
            ),
            Case(
                "loop over identifier with limit and offset",
                "product in collection.products limit:4 offset:2",
                [
                    Token(1, TOKEN_IDENTIFIER, "product"),
                    Token(1, TOKEN_IN, "in"),
                    Token(1, TOKEN_IDENTIFIER, "collection"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "products"),
                    Token(1, TOKEN_LIMIT, "limit"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_INTEGER, "4"),
                    Token(1, TOKEN_OFFSET, "offset"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_INTEGER, "2"),
                ],
            ),
            Case(
                "loop over reversed range",
                "num in (1..10) reversed",
                [
                    Token(1, TOKEN_IDENTIFIER, "num"),
                    Token(1, TOKEN_IN, "in"),
                    Token(1, TOKEN_LPAREN, "("),
                    Token(1, TOKEN_INTEGER, "1"),
                    Token(1, TOKEN_RANGE, ".."),
                    Token(1, TOKEN_INTEGER, "10"),
                    Token(1, TOKEN_RPAREN, ")"),
                    Token(1, TOKEN_REVERSED, "reversed"),
                ],
            ),
            Case(
                "loop over range with identifier",
                "i in (1..num)",
                [
                    Token(1, TOKEN_IDENTIFIER, "i"),
                    Token(1, TOKEN_IN, "in"),
                    Token(1, TOKEN_LPAREN, "("),
                    Token(1, TOKEN_INTEGER, "1"),
                    Token(1, TOKEN_RANGE, ".."),
                    Token(1, TOKEN_IDENTIFIER, "num"),
                    Token(1, TOKEN_RPAREN, ")"),
                ],
            ),
            Case(
                description="loop over named iterable with continue offset",
                source="item in array limit: 3 offset: continue",
                expect=[
                    Token(1, TOKEN_IDENTIFIER, "item"),
                    Token(1, TOKEN_IN, "in"),
                    Token(1, TOKEN_IDENTIFIER, "array"),
                    Token(1, TOKEN_LIMIT, "limit"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_INTEGER, "3"),
                    Token(1, TOKEN_OFFSET, "offset"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_CONTINUE, "continue"),
                ],
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize_loop_expression(case.source))

                self.assertTrue(len(tokens) == len(case.expect))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)

    def test_lex_include_expression(self):
        """Test that we can tokenize include expressions."""
        test_cases = [
            Case(
                "string literal name no local variable",
                "'product'",
                [
                    Token(1, TOKEN_STRING, "product"),
                ],
            ),
            Case(
                "name from identifier and no local variable",
                "section.name",
                [
                    Token(1, TOKEN_IDENTIFIER, "section"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "name"),
                ],
            ),
            Case(
                "string literal name with identifier local variable",
                "'product' with products[0]",
                [
                    Token(1, TOKEN_STRING, "product"),
                    Token(1, TOKEN_WITH, "with"),
                    Token(1, TOKEN_IDENTIFIER, "products"),
                    Token(1, TOKEN_LBRACKET, "["),
                    Token(1, TOKEN_INTEGER, "0"),
                    Token(1, TOKEN_RBRACKET, "]"),
                ],
            ),
            Case(
                "string literal name with keyword arguments",
                "'product', foo: 'bar', some: other.tags",
                [
                    Token(1, TOKEN_STRING, "product"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_IDENTIFIER, "foo"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_STRING, "bar"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_IDENTIFIER, "some"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_IDENTIFIER, "other"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "tags"),
                ],
            ),
            Case(
                "string literal name with identifier aliased local variable",
                "'product' with products[0] as foo",
                [
                    Token(1, TOKEN_STRING, "product"),
                    Token(1, TOKEN_WITH, "with"),
                    Token(1, TOKEN_IDENTIFIER, "products"),
                    Token(1, TOKEN_LBRACKET, "["),
                    Token(1, TOKEN_INTEGER, "0"),
                    Token(1, TOKEN_RBRACKET, "]"),
                    Token(1, TOKEN_AS, "as"),
                    Token(1, TOKEN_IDENTIFIER, "foo"),
                ],
            ),
            Case(
                "string literal name with iterable local variable",
                "'product' for products",
                [
                    Token(1, TOKEN_STRING, "product"),
                    Token(1, TOKEN_FOR, "for"),
                    Token(1, TOKEN_IDENTIFIER, "products"),
                ],
            ),
            Case(
                "string literal name with aliased iterable local variable",
                "'product' for products as foo",
                [
                    Token(1, TOKEN_STRING, "product"),
                    Token(1, TOKEN_FOR, "for"),
                    Token(1, TOKEN_IDENTIFIER, "products"),
                    Token(1, TOKEN_AS, "as"),
                    Token(1, TOKEN_IDENTIFIER, "foo"),
                ],
            ),
            Case(
                "literal name with identifier aliased local variable and arguments",
                "'product' with products[0] as foo, bar: 42, baz: 'hello'",
                [
                    Token(1, TOKEN_STRING, "product"),
                    Token(1, TOKEN_WITH, "with"),
                    Token(1, TOKEN_IDENTIFIER, "products"),
                    Token(1, TOKEN_LBRACKET, "["),
                    Token(1, TOKEN_INTEGER, "0"),
                    Token(1, TOKEN_RBRACKET, "]"),
                    Token(1, TOKEN_AS, "as"),
                    Token(1, TOKEN_IDENTIFIER, "foo"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_IDENTIFIER, "bar"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_INTEGER, "42"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_IDENTIFIER, "baz"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_STRING, "hello"),
                ],
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize_include_expression(case.source))

                self.assertTrue(len(tokens) == len(case.expect))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)
