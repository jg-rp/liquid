"""Test cases for shorthand comment syntax."""

import operator
from dataclasses import dataclass
from typing import Type
from typing import Union

import pytest

from liquid import Environment
from liquid import Template


@dataclass
class Case:
    description: str
    template: str
    expect: Union[str, Type[Exception]]


def test_shorthand_comments_are_disabled_by_default() -> None:
    env = Environment()
    source = "Hello, {# this is a comment #} World!"
    assert env.from_string(source).render() == source
    assert Template(source).render() == source


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

MOCK_ENV = Environment(template_comments=True)


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_shorthand_comments(case: Case) -> None:
    assert MOCK_ENV.from_string(case.template).render() == case.expect
    assert Template(case.template, template_comments=True).render() == case.expect


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

ALT_MOCK_ENV = Environment(
    template_comments=True, comment_start_string="{//", comment_end_string="//}"
)


@pytest.mark.parametrize("case", ALT_TEST_CASES, ids=operator.attrgetter("description"))
def test_alternate_shorthand_comments(case: Case) -> None:
    assert ALT_MOCK_ENV.from_string(case.template).render() == case.expect
    assert (
        Template(
            case.template,
            template_comments=True,
            comment_start_string="{//",
            comment_end_string="//}",
        ).render()
        == case.expect
    )
