import asyncio
import operator
import re
from dataclasses import dataclass, field

import pytest

from liquid import (
    Environment,
    ExtendedParser,
    FalsyStrictUndefined,
    StrictUndefined,
    Template,
)
from liquid.exceptions import LiquidNameError, UndefinedVariableError
from liquid.tokens import TOKEN_EOI


@dataclass
class Case:
    description: str
    template: str
    expect: str
    context: dict[str, object] = field(default_factory=dict)  # pyright: ignore[reportUnknownVariableType]


TEST_CASES = [
    Case(
        description="undefined in output statement",
        template=r"{{ nosuchthing }}",
        expect="",
    ),
    Case(
        description="undefined in loop expression",
        template=r"{% for tag in nosuchthing %}{tag}{% endfor %}",
        expect="",
    ),
    Case(
        description="index undefined",
        template=r"{{ nosuchthing[0] }}",
        expect="",
    ),
    Case(
        description="test undefined for truthy-ness",
        template=r"{% if nosuchthing %}hello{% endif %}",
        expect="",
    ),
    Case(
        description="compare undefined",
        template=r"{% if nosuchthing == 'hello' %}hello{% endif %}",
        expect="",
    ),
    Case(
        description="undefined equals undefined",
        template=r"{% if nosuchthing == noway %}hello{% endif %}",
        expect="hello",
    ),
    Case(
        description="undefined contains string",
        template=r"{% if nosuchthing contains 'hello' %}hello{% endif %}",
        expect="",
    ),
    Case(
        description="access `last` from undefined",
        template=r"{{ nosuchthing.last }}",
        expect="",
    ),
    Case(
        description="access `size` from undefined",
        template=r"{{ nosuchthing.size }}",
        expect="",
    ),
    Case(
        description="filtered undefined",
        template=r"hello {{ nosuchthing | last }} there",
        expect="hello  there",
    ),
    Case(
        description="math filter undefined",
        template=r"hello {{ nosuchthing | abs }} there",
        expect="hello 0 there",
    ),
    Case(
        description="undefined filter argument",
        template=r"hello {{ '1,2,3' | split: nosuchthing }} there",
        expect="hello 1,2,3 there",
    ),
    Case(
        description="filter undefined through date",
        template=r"hello {{ nosuchthing | date: '%b %d, %y' }} there",
        expect="hello  there",
    ),
    Case(
        description="array index out or range",
        template=r"{% assign a = '1,2,3,4,5' | split: ',' %}{{ a[100] }}",
        expect="",
    ),
    Case(
        description="negative array index out or range",
        template=r"{% assign a = '1,2,3,4,5' | split: ',' %}{{ a[-100] }}",
        expect="",
    ),
]

ENV = Environment()


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_default_undefined(case: Case) -> None:
    """Test that the default undefined type is quiet and forgiving."""
    template = ENV.parse(case.template)
    result = template.render()
    assert case.expect == result


STRICT_TEST_CASES = [
    Case(
        description="undefined in output statement",
        template=r"{{ nosuchthing }}",
        expect="nosuchthing is undefined",
    ),
    Case(
        description="undefined in loop expression",
        template=r"{% for tag in nosuchthing %}{tag}{% endfor %}",
        expect="nosuchthing is undefined",
    ),
    Case(
        description="index undefined",
        template=r"{{ nosuchthing[0] }}",
        expect=re.escape("nosuchthing[0] is undefined"),
    ),
    Case(
        description="test undefined for truthy-ness",
        template=r"{% if nosuchthing %}hello{% endif %}",
        expect="nosuchthing is undefined",
    ),
    Case(
        description="compare undefined",
        template=r"{% if nosuchthing == 'hello' %}hello{% endif %}",
        expect="nosuchthing is undefined",
    ),
    Case(
        description="undefined equals undefined",
        template=r"{% if nosuchthing == noway %}hello{% endif %}",
        expect="noway is undefined",
    ),
    Case(
        description="undefined contains string",
        template=r"{% if nosuchthing contains 'hello' %}hello{% endif %}",
        expect="nosuchthing is undefined",
    ),
    Case(
        description="access `last` from undefined",
        template=r"{{ nosuchthing.last }}",
        expect="nosuchthing.last is undefined",
    ),
    Case(
        description="access `size` from undefined",
        template=r"{{ nosuchthing.size }}",
        expect="nosuchthing.size is undefined",
    ),
    Case(
        description="filtered undefined",
        template=r"hello {{ nosuchthing | last }} there",
        expect="nosuchthing is undefined",
    ),
    Case(
        description="undefined filter argument",
        template=r"hello {{ '1,2,3' | split: nosuchthing }} there",
        expect="nosuchthing is undefined",
    ),
    Case(
        description="math filter undefined",
        template=r"hello {{ nosuchthing | abs }} there",
        expect="nosuchthing is undefined",
    ),
    Case(
        description="array index out of range",
        template=r"{% assign a = '1,2,3,4,5' | split: ',' %}{{ a[100] }}",
        expect=re.escape("a[100] is undefined"),
    ),
    Case(
        description="negative array index out of range",
        template=r"{% assign a = '1,2,3,4,5' | split: ',' %}{{ a[-100] }}",
        expect=re.escape("a[-100] is undefined"),
    ),
    Case(
        description="key error",
        template=r"{{ obj['bar'] }}",
        expect=re.escape("obj['bar'] is undefined"),
        context={"obj": {"foo": 1}},
    ),
    Case(
        description="default filter undefined",
        template=r"hello {{ nosuchthing | default: 'foo' }} there",
        expect="nosuchthing is undefined",
    ),
]


STRICT_ENV = Environment(undefined=StrictUndefined)


@pytest.mark.parametrize(
    "case", STRICT_TEST_CASES, ids=operator.attrgetter("description")
)
def test_strict_undefined(case: Case) -> None:
    """Test that the strict undefined type raises an exception for everything."""
    template = STRICT_ENV.parse(case.template)

    with pytest.raises(UndefinedVariableError, match=case.expect):
        template.render(case.context)


def test_falsy_undefined_with_default_filter() -> None:
    """Test that we can use an undefined type with the default filter."""
    env = Environment(undefined=FalsyStrictUndefined)
    template = env.parse(r"{{ nosuchthing | default: 'hello' }}")
    result = template.render()
    assert result == "hello"

    template = env.parse(r"{{ thing | default: 'hello' }}")
    result = template.render({"thing": "foo"})
    assert result == "foo"

    template = env.parse(r"{{ nosuchthing }}")
    with pytest.raises(UndefinedVariableError, match="nosuchthing is undefined"):
        template.render()


@pytest.mark.parametrize(
    "template,want",
    [
        ("{% if nosuchthing %}TRUE{% else %}FALSE{% endif %}", "FALSE"),
        ("{% unless nosuchthing %}TRUE{% else %}FALSE{% endunless %}", "TRUE"),
        ("{{ nosuchthing or 'foo' }}", "foo"),
    ],
)
def test_falsy_undefined(template: str, want: str) -> None:
    env = Environment(undefined=FalsyStrictUndefined, parser=ExtendedParser)
    assert env.render(template) == want


LAX_FILTER_TEST_CASES = [
    Case(
        description="undefined filter",
        template=r"{{ 'hello' | nosuchthing }}",
        expect="hello",
    ),
    Case(
        description="undefined filter with argument",
        template=r"{{ 'hello' | nosuchthing: 'foo' }}",
        expect="hello",
    ),
    Case(
        description="undefined filter with more filters",
        template=r"{{ 'hello' | nosuchthing | upcase }}",
        expect="HELLO",
    ),
]


@pytest.mark.parametrize(
    "case", LAX_FILTER_TEST_CASES, ids=operator.attrgetter("description")
)
def test_lax_filter(case: Case) -> None:
    """Test that undefined filters can be silently ignored."""
    env = Environment(strict_filters=False)
    template = env.parse(case.template)
    result = template.render()
    assert case.expect == result


STRICT_FILTER_TEST_CASES = [
    Case(
        description="undefined filter",
        template=r"{{ 'hello' | nosuchthing }}",
        expect="unknown filter 'nosuchthing'",
    ),
    Case(
        description="undefined filter with argument",
        template=r"{{ 'hello' | nosuchthing: 'foo' }}",
        expect="unknown filter 'nosuchthing'",
    ),
    Case(
        description="undefined filter with more filters",
        template=r"{{ 'hello' | nosuchthing | upcase }}",
        expect="unknown filter 'nosuchthing'",
    ),
]


@pytest.mark.parametrize(
    "case", STRICT_FILTER_TEST_CASES, ids=operator.attrgetter("description")
)
def test_strict_filters(case: Case) -> None:
    """Test that undefined filters raise an exception in strict mode."""
    env = Environment(strict_filters=True)
    template = env.parse(case.template)

    with pytest.raises(LiquidNameError, match=case.expect):
        template.render()

    # And render async
    async def coro(template: Template) -> str:
        return await template.render_async()

    with pytest.raises(LiquidNameError):
        asyncio.run(coro(template))


def test_strict_undefined_magic() -> None:
    """Test the strict undefined type magic methods."""
    undefined = StrictUndefined("nosuchthing", (TOKEN_EOI, -1, -1), "", "")

    with pytest.raises(UndefinedVariableError):
        _ = "foo" in undefined

    with pytest.raises(UndefinedVariableError):
        int(undefined)

    with pytest.raises(UndefinedVariableError):
        list(undefined)

    with pytest.raises(UndefinedVariableError):
        len(undefined)

    with pytest.raises(UndefinedVariableError):
        str(undefined)

    assert repr(undefined) == "StrictUndefined(nosuchthing)"

    with pytest.raises(UndefinedVariableError):
        bool(undefined)

    with pytest.raises(UndefinedVariableError):
        hash(undefined)

    with pytest.raises(UndefinedVariableError):
        reversed(undefined)
