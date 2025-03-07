import operator
from typing import NamedTuple

import pytest

from liquid import Environment
from liquid.token import TOKEN_CONTENT
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_OUTPUT
from liquid.token import TOKEN_TAG
from liquid.token import Token


class Case(NamedTuple):
    description: str
    source: str
    expect: list[Token]


TEST_CASES = [
    Case(
        "simple template literal",
        "<HTML>some</HTML>",
        [
            Token(TOKEN_CONTENT, "<HTML>some</HTML>", 0, ""),
        ],
    ),
    Case(
        "template literal and object",
        r"<HTML>{{ other }}</HTML>",
        [
            Token(TOKEN_CONTENT, "<HTML>", 0, ""),
            Token(TOKEN_OUTPUT, "{{ other }}", 0, ""),
            Token(TOKEN_EXPRESSION, "other", 0, ""),
            Token(TOKEN_CONTENT, "</HTML>", 0, ""),
        ],
    ),
    Case(
        "template literal and object with filters",
        r"<HTML>{{ other | upper }}</HTML>",
        [
            Token(TOKEN_CONTENT, "<HTML>", 0, ""),
            Token(TOKEN_OUTPUT, "{{ other | upper }}", 0, ""),
            Token(TOKEN_EXPRESSION, "other | upper", 0, ""),
            Token(TOKEN_CONTENT, "</HTML>", 0, ""),
        ],
    ),
    Case(
        "template literal and object with whitespace control",
        r"<HTML>{{- other -}}</HTML>",
        [
            Token(TOKEN_CONTENT, "<HTML>", 0, ""),
            Token(TOKEN_OUTPUT, "{{- other -}}", 0, ""),
            Token(TOKEN_EXPRESSION, "other", 0, ""),
            Token(TOKEN_CONTENT, "</HTML>", 0, ""),
        ],
    ),
    Case(
        "template literal and control flow",
        "<HTML>{% if product %}some{% else %}other{% endif %}</HTML>",
        [
            Token(TOKEN_CONTENT, "<HTML>", 0, ""),
            Token(TOKEN_TAG, "if", 0, ""),
            Token(TOKEN_EXPRESSION, "product", 0, ""),
            Token(TOKEN_CONTENT, "some", 0, ""),
            Token(TOKEN_TAG, "else", 0, ""),
            Token(TOKEN_CONTENT, "other", 0, ""),
            Token(TOKEN_TAG, "endif", 0, ""),
            Token(TOKEN_CONTENT, "</HTML>", 0, ""),
        ],
    ),
    Case(
        "template literal and control flow and inconsistent whitespace",
        "<HTML>{%if  product %}some{% else  %}other{% endif%}</HTML>",
        [
            Token(TOKEN_CONTENT, "<HTML>", 0, ""),
            Token(TOKEN_TAG, "if", 0, ""),
            Token(TOKEN_EXPRESSION, "product", 0, ""),
            Token(TOKEN_CONTENT, "some", 0, ""),
            Token(TOKEN_TAG, "else", 0, ""),
            Token(TOKEN_CONTENT, "other", 0, ""),
            Token(TOKEN_TAG, "endif", 0, ""),
            Token(TOKEN_CONTENT, "</HTML>", 0, ""),
        ],
    ),
    Case(
        "newlines inside tags",
        "<HTML>{%if\nproduct %}some{% else\n %}other{% endif%}</HTML>",
        [
            Token(TOKEN_CONTENT, "<HTML>", 0, ""),
            Token(TOKEN_TAG, "if", 0, ""),
            Token(TOKEN_EXPRESSION, "product", 0, ""),
            Token(TOKEN_CONTENT, "some", 0, ""),
            Token(TOKEN_TAG, "else", 0, ""),
            Token(TOKEN_CONTENT, "other", 0, ""),
            Token(TOKEN_TAG, "endif", 0, ""),
            Token(TOKEN_CONTENT, "</HTML>", 0, ""),
        ],
    ),
    Case(
        "carriage return inside tags",
        "<HTML>{%if\rproduct %}some{% else\r %}other{% endif%}</HTML>",
        [
            Token(TOKEN_CONTENT, "<HTML>", 0, ""),
            Token(TOKEN_TAG, "if", 0, ""),
            Token(TOKEN_EXPRESSION, "product", 0, ""),
            Token(TOKEN_CONTENT, "some", 0, ""),
            Token(TOKEN_TAG, "else", 0, ""),
            Token(TOKEN_CONTENT, "other", 0, ""),
            Token(TOKEN_TAG, "endif", 0, ""),
            Token(TOKEN_CONTENT, "</HTML>", 0, ""),
        ],
    ),
    Case(
        "carriage return and newline inside tags",
        "<HTML>{%if\r\nproduct %}some{% else\r\n %}other{% endif%}</HTML>",
        [
            Token(TOKEN_CONTENT, "<HTML>", 0, ""),
            Token(TOKEN_TAG, "if", 0, ""),
            Token(TOKEN_EXPRESSION, "product", 0, ""),
            Token(TOKEN_CONTENT, "some", 0, ""),
            Token(TOKEN_TAG, "else", 0, ""),
            Token(TOKEN_CONTENT, "other", 0, ""),
            Token(TOKEN_TAG, "endif", 0, ""),
            Token(TOKEN_CONTENT, "</HTML>", 0, ""),
        ],
    ),
    Case(
        "inconsistent whitespace and whitespace control",
        "<HTML>{%if  product %}some  {%- else  %}other{% endif -%}</HTML>",
        [
            Token(TOKEN_CONTENT, "<HTML>", 0, ""),
            Token(TOKEN_TAG, "if", 0, ""),
            Token(TOKEN_EXPRESSION, "product", 0, ""),
            Token(TOKEN_CONTENT, "some", 0, ""),
            Token(TOKEN_TAG, "else", 0, ""),
            Token(TOKEN_CONTENT, "other", 0, ""),
            Token(TOKEN_TAG, "endif", 0, ""),
            Token(TOKEN_CONTENT, "</HTML>", 0, ""),
        ],
    ),
    Case(
        "raw",
        "{% raw %}{{ hello }} %}{% {{ {% endraw %}",
        [
            Token(TOKEN_CONTENT, r"{{ hello }} %}{% {{ ", 0, ""),
        ],
    ),
    Case(
        "assign",
        "{% assign foo = 'bar' %}",
        [
            Token(TOKEN_TAG, "assign", 0, ""),
            Token(TOKEN_EXPRESSION, "foo = 'bar'", 0, ""),
        ],
    ),
    Case(
        "assign a range literal",
        "{% assign foo = (1..5) %}",
        [
            Token(TOKEN_TAG, "assign", 0, ""),
            Token(TOKEN_EXPRESSION, "foo = (1..5)", 0, ""),
        ],
    ),
    Case(
        "capture",
        ("{% capture greeting %}Hello, {{ customer.first_name }}.{% endcapture %}"),
        [
            Token(TOKEN_TAG, "capture", 0, ""),
            Token(TOKEN_EXPRESSION, "greeting", 0, ""),
            Token(TOKEN_CONTENT, "Hello, ", 0, ""),
            Token(TOKEN_OUTPUT, "{{ customer.first_name }}", 0, ""),
            Token(TOKEN_EXPRESSION, "customer.first_name", 0, ""),
            Token(TOKEN_CONTENT, ".", 0, ""),
            Token(TOKEN_TAG, "endcapture", 0, ""),
        ],
    ),
    Case(
        "inline comment tag",
        "{% # this is a comment %}",
        [
            Token(TOKEN_TAG, "#", 0, ""),
            Token(TOKEN_EXPRESSION, "this is a comment", 0, ""),
        ],
    ),
]

ENV = Environment()


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_lex_template(case: Case) -> None:
    tokenize = ENV.tokenizer()
    tokens = list(tokenize(case.source))

    assert len(tokens) == len(case.expect)

    for token, expect in zip(tokens, case.expect):
        assert token.kind == expect.kind
        assert token.value == expect.value
