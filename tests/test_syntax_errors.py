import operator
from typing import NamedTuple

import pytest

from liquid import Environment, ExtendedParser
from liquid.exceptions import LiquidSyntaxError


class Case(NamedTuple):
    description: str
    template: str
    expect_msg: str


TEST_CASES = [
    Case(
        description="no expression",
        template="{% if %}foo{% endif %}",
        expect_msg="missing expression",
    ),
    Case(
        description="end tag mismatch",
        template="{% if true %}foo{% endunless %}",
        expect_msg="unexpected tag 'endunless'",
    ),
    Case(
        description="unexpected outer tag name",
        template="{% foo true %}foo{% endfoo %}",
        expect_msg="unexpected tag 'foo'",
    ),
    Case(
        description="missing tag name",
        template="{% %}foo{% endif %}",
        expect_msg="missing tag name",
    ),
    Case(
        description="missing end tag at EOF",
        template="{% if true %}foo{% assign bar = 'baz' %}",
        expect_msg="expected tag 'endif'",
    ),
    Case(
        description="orphaned else",
        template="{% else %}",
        expect_msg="unexpected tag 'else'",
    ),
    Case(
        description="orphaned when",
        template="{% when %}",
        expect_msg="unexpected tag 'when'",
    ),
    Case(
        description="missing 'in' in forloop",
        template="{% for x (0..3) %}{{ x }}{% endfor %}",
        expect_msg="missing 'in'",
    ),
    Case(
        description="missing expression in forloop",
        template="{% for x in %}{{ x }}foo{% endfor %}",
        expect_msg="missing expression",
    ),
    Case(
        description="float with trailing dot in range literal",
        template="{% for x in (2...4) %}{{ x }}{% endfor %}",
        expect_msg="too many dots",
    ),
    Case(
        description="chained identifier for loop variable",
        template="{% for x.y in (2...4) %}{{ x }}{% endfor %}",
        expect_msg="expected an identifier, found a path",
    ),
    Case(
        description="missing equal in assignment tag",
        template="{% assign x 5 %}",
        expect_msg="bad identifier or missing '='",
    ),
    Case(
        description="invalid subscript identifier",
        template="{{ foo[1.2] }}",
        expect_msg="expected an integer, identifier or string",
    ),
    Case(
        description="float literal without a leading zero",
        template="{{ .1 }}",
        expect_msg="expected a basic expression, found '.'",
    ),
    Case(
        description="unknown infix operator",
        template="{% if 1 =! 2 %}ok{% endif %}",
        expect_msg="unknown or missing operator",
    ),
    Case(
        description="bad 'unless' expression",
        template="{% unless 1 ~ 2 %}ok{% endunless %}",
        expect_msg="unknown or missing operator",
    ),
    Case(
        description="bad conditional expression in unless block",
        template="{% unless true %}ok{% elsif £$! %}{% endunless %}",
        expect_msg="expected a basic expression, found symbol",
    ),
    Case(
        description="unknown symbol",
        template="{% if 1 ~ 2 %}ok{% endif %}",
        expect_msg="unknown or missing operator",
    ),
    Case(
        description="bad alternative condition expression",
        template="{% if false %}ok{% elsif 1~=2 %}not ok{% endif %}",
        expect_msg="unknown or missing operator",
    ),
    Case(
        description="junk in `liquid` tag",
        template="\n".join(  # noqa: FLY002
            [
                r"{{ 'hello' }}",
                r"{% liquid",
                r"echo 'foo'",
                r"aiu34bseu",
                r"%}",
            ]
        ),
        expect_msg="unexpected tag 'aiu34bseu'",
    ),
    Case(
        description="bad token in loop expression",
        template="{% for i$ in (1..3) %}{% endfor %}",
        expect_msg=r"missing 'in'",
    ),
    Case(
        description="invalid loop argument",
        template="{% for product in collections[0]['tags'] limit:| %}{% endfor %}",
        expect_msg="unexpected '|'",
    ),
    Case(
        description="unexpected token between left value and filter",
        template=r'{{ "hello" boo | upcase }}',
        expect_msg="malformed expression or missing output delimiter",
    ),
    Case(
        description="unexpected token after left value and no filters",
        template=r'{{ "hello" offset:2 }}',
        expect_msg="malformed expression or missing output delimiter",
    ),
    Case(
        description="include, target not a path or string",
        template="{% include 42 with product['some-tags'] as foo.bar %}",
        expect_msg="expected an identifier, found a path",
    ),
    Case(
        description="include, multi-segmented alias",
        template="{% include 'feature.liquid' with product['some-tags'] as foo.bar %}",
        expect_msg="expected an identifier, found a path",
    ),
    Case(
        description="chained keyword identifier",
        template="{% include 'product.liquid', foo.bar: 'hello' %}",
        expect_msg=r"expected an identifier, found a path",
    ),
    Case(
        description="unexpected identifier character",
        template=r"{% assign foo+bar = 'hello there'%}{{ foo+bar }}",
        expect_msg="bad identifier or missing '='",
    ),
    Case(
        description="unexpected assign path",
        template=r"{% assign foo.bar = 'hello there' %}{{ foo.bar }}",
        expect_msg="expected an identifier, found a path",
    ),
    Case(
        description="unexpected capture path",
        template=r"{% capture foo.bar %}{% endcapture %}",
        expect_msg="expected an identifier, found a path",
    ),
    # Case(
    #     description="consecutive commas in keyword argument list",
    #     template=r"{% with you='world',, some='thing' %}Hello, {{ you }}!{% endwith %}",
    #     expect_msg="expected an argument name, found comma",
    # ),
    # Case(
    #     description="consecutive commas in positional argument list",
    #     template=r"{% call macro a,, b %}",
    #     expect_msg="expected a primitive expression, found comma",
    # ),
    Case(
        description="path, empty brackets",
        template=r"{{ a.b[] }}",
        expect_msg="empty bracketed segment",
    ),
    Case(
        description="path, unbalanced brackets",
        template=r"{{ a.b['foo']] }}",
        expect_msg="malformed expression or missing output delimiter",
    ),
]


ENV = Environment(parser=ExtendedParser)


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_syntax_errors(case: Case) -> None:
    with pytest.raises(LiquidSyntaxError, match=case.expect_msg):
        ENV.parse(case.template).render()


# TODO:
# LAX_ENV = MockEnv(tolerance=Mode.LAX)

# SKIP = [
#     "missing output closing bracket",
#     "missing tag closing percent",
#     "missing tag closing bracket",
#     "missing tag name",
# ]

# LAX_TEST_CASES = [case for case in TEST_CASES if case.description not in SKIP]


# @pytest.mark.parametrize("case", LAX_TEST_CASES, ids=operator.attrgetter("description"))
# def test_syntax_errors_in_lax_mode(case: Case) -> None:
#     assert isinstance(LAX_ENV.from_string(case.template).render(), str)
