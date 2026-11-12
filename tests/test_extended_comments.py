import operator
from dataclasses import dataclass

import pytest

from liquid import Environment, ExtendedLexer


@dataclass
class Case:
    description: str
    template: str
    expect: str


def test_shorthand_comments_are_disabled_by_default() -> None:
    env = Environment()
    source = "Hello, {# this is a comment #} World!"
    assert env.parse(source).render() == source


TEST_CASES = [
    Case(
        description="shorthand comments are ignored",
        template=r"Hello, {# this is a comment #} World!",
        expect="Hello,  World!",
    ),
    Case(
        description="shorthand comments must have a trailing hash.",
        template=r"Hello, {# this is not a comment } World!",
        expect="Hello, {# this is not a comment } World!",
    ),
    Case(
        description="shorthand comments can contain tags and statements",
        template=r"Hello, {# this is {% if %} a {{ comment }} #} World!",
        expect="Hello,  World!",
    ),
    Case(
        description="liquid expression line comments are ignored",
        template="\n".join(
            (
                r"{% liquid ",
                r"if true",
                r"echo 'foo'",
                r"endif",
                r"# this is a comment",
                r"%}",
            )
        ),
        expect="foo",
    ),
    Case(
        description="shorthand comments can remove trailing whitespace",
        template=r"Hello, {# this is a comment -#} World!",
        expect="Hello, World!",
    ),
    Case(
        description="shorthand comments can remove leading whitespace",
        template=r"Hello, {#- this is a comment #} World!",
        expect="Hello, World!",
    ),
]

MOCK_ENV = Environment(tokenizer=ExtendedLexer)


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_shorthand_comments(case: Case) -> None:
    assert MOCK_ENV.parse(case.template).render() == case.expect


ALT_TEST_CASES = [
    Case(
        description="shorthand comments are ignored",
        template="Hello, {// this is a comment //} World!",
        expect="Hello,  World!",
    ),
    Case(
        description="shorthand comments must have a valid end sequence.",
        template=r"Hello, {// this is not a comment } World!",
        expect="Hello, {// this is not a comment } World!",
    ),
    Case(
        description="shorthand comments can contain tags and statements",
        template=r"Hello, {// this is {% if %} a {{ comment }} //} World!",
        expect="Hello,  World!",
    ),
    Case(
        description="liquid expression line comments are ignored",
        template="\n".join(
            (
                r"{% liquid ",
                r"if true",
                r"echo 'foo'",
                r"endif",
                r"// this is a comment",
                r"%}",
            )
        ),
        expect="foo",
    ),
]


class MockLexer(ExtendedLexer):
    comment_start = "{//"
    comment_end = "//}"
    line_comment_start = "//"


ALT_MOCK_ENV = Environment(tokenizer=MockLexer)


@pytest.mark.parametrize("case", ALT_TEST_CASES, ids=operator.attrgetter("description"))
def test_alternate_shorthand_comments(case: Case) -> None:
    assert ALT_MOCK_ENV.parse(case.template).render() == case.expect
