"""Test built-in "undefined" types."""

import asyncio
import operator
from dataclasses import dataclass
from dataclasses import field

import pytest

from liquid import BoundTemplate
from liquid import DebugUndefined
from liquid import Environment
from liquid import StrictDefaultUndefined
from liquid import StrictUndefined
from liquid import Undefined
from liquid.exceptions import UndefinedError
from liquid.exceptions import UnknownFilterError


@dataclass
class Case:
    """Table driven test case helper."""

    description: str
    template: str
    expect: str
    context: dict[str, object] = field(default_factory=dict)


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
    template = ENV.from_string(case.template)
    result = template.render()
    assert case.expect == result


STRICT_TEST_CASES = [
    Case(
        description="undefined in output statement",
        template=r"{{ nosuchthing }}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="undefined in loop expression",
        template=r"{% for tag in nosuchthing %}{tag}{% endfor %}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="index undefined",
        template=r"{{ nosuchthing[0] }}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="test undefined for truthy-ness",
        template=r"{% if nosuchthing %}hello{% endif %}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="compare undefined",
        template=r"{% if nosuchthing == 'hello' %}hello{% endif %}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="undefined equals undefined",
        template=r"{% if nosuchthing == noway %}hello{% endif %}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="undefined contains string",
        template=r"{% if nosuchthing contains 'hello' %}hello{% endif %}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="access `last` from undefined",
        template=r"{{ nosuchthing.last }}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="access `size` from undefined",
        template=r"{{ nosuchthing.size }}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="filtered undefined",
        template=r"hello {{ nosuchthing | last }} there",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="undefined filter argument",
        template=r"hello {{ '1,2,3' | split: nosuchthing }} there",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="math filter undefined",
        template=r"hello {{ nosuchthing | abs }} there",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="array index out of range",
        template=r"{% assign a = '1,2,3,4,5' | split: ',' %}{{ a[100] }}",
        expect="index out of range",
    ),
    Case(
        description="negative array index out of range",
        template=r"{% assign a = '1,2,3,4,5' | split: ',' %}{{ a[-100] }}",
        expect="index out of range",
    ),
    Case(
        description="key error",
        template=r"{{ obj['bar'] }}",
        expect="obj.bar is undefined",
        context={"obj": {"foo": 1}},
    ),
    Case(
        description="default filter undefined",
        template=r"hello {{ nosuchthing | default: 'foo' }} there",
        expect="'nosuchthing' is undefined",
    ),
]


STRICT_ENV = Environment(undefined=StrictUndefined)


@pytest.mark.parametrize(
    "case", STRICT_TEST_CASES, ids=operator.attrgetter("description")
)
def test_strict_undefined(case: Case) -> None:
    """Test that the strict undefined type raises an exception for everything."""
    template = STRICT_ENV.from_string(case.template)

    with pytest.raises(UndefinedError, match=case.expect):
        template.render(**case.context)


def test_debug_undefined() -> None:
    """Test that the debugging undefined type prints debugging information."""
    env = Environment(undefined=DebugUndefined)
    template = env.from_string(r"{{ nosuchthing }}")
    result = template.render()
    assert result == "'nosuchthing' is undefined"


def test_debug_undefined_hint() -> None:
    """Test that the debugging undefined type prints debugging hints."""
    env = Environment(undefined=DebugUndefined)
    undef = DebugUndefined(
        name="nosuchthing", hint="can't resolve identifier", token=None
    )
    template = env.from_string(r"{{ undef }}")
    result = template.render(undef=undef)
    assert result == "can't resolve identifier"


def test_debug_undefined_object() -> None:
    """Test that the debugging undefined type prints related object information."""
    env = Environment(undefined=DebugUndefined)
    undef = DebugUndefined(name="nosuchthing", obj="foo", token=None)
    template = env.from_string(r"{{ nosuchthing }}")
    result = template.render(nosuchthing=undef)
    assert result == "str has no attribute 'nosuchthing'"


def test_strict_default_undefined_with_default_filter() -> None:
    """Test that we can use an undefined type with the default filter."""
    env = Environment(undefined=StrictDefaultUndefined)
    template = env.from_string(r"{{ nosuchthing | default: 'hello' }}")
    result = template.render()
    assert result == "hello"

    template = env.from_string(r"{{ thing | default: 'hello' }}")
    result = template.render(thing="foo")
    assert result == "foo"

    template = env.from_string(r"{{ nosuchthing }}")
    with pytest.raises(UndefinedError, match="'nosuchthing' is undefined"):
        template.render()


def test_filter_strict_default_undefined() -> None:
    """Test that the default undefined type raises an exception when used as a
    filter left value."""
    env = Environment(undefined=StrictDefaultUndefined)
    template = env.from_string(r"{{ nosuchthing | floor }}")
    with pytest.raises(UndefinedError, match="'nosuchthing' is undefined"):
        template.render()


def test_isinstance_strict_default_filter() -> None:
    """Test that the default undefined type raises an exception when accessing
    __class__."""
    undef = StrictDefaultUndefined("nosuchthing", token=None)
    with pytest.raises(UndefinedError):
        undef.__class__  # noqa: B018


STRICT_DEFAULT_TEST_CASES = [
    Case(
        description="undefined in output statement",
        template=r"{{ nosuchthing }}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="undefined in loop expression",
        template=r"{% for tag in nosuchthing %}{tag}{% endfor %}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="index undefined",
        template=r"{{ nosuchthing[0] }}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="test undefined for truthy-ness",
        template=r"{% if nosuchthing %}hello{% endif %}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="compare undefined",
        template=r"{% if nosuchthing == 'hello' %}hello{% endif %}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="undefined equals undefined",
        template=r"{% if nosuchthing == noway %}hello{% endif %}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="undefined contains string",
        template=r"{% if nosuchthing contains 'hello' %}hello{% endif %}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="access `last` from undefined",
        template=r"{{ nosuchthing.last }}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="access `size` from undefined",
        template=r"{{ nosuchthing.size }}",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="filtered undefined",
        template=r"hello {{ nosuchthing | last }} there",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="undefined filter argument",
        template=r"hello {{ '1,2,3' | split: nosuchthing }} there",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="math filter undefined",
        template=r"hello {{ nosuchthing | abs }} there",
        expect="'nosuchthing' is undefined",
    ),
    Case(
        description="array index out of range",
        template=r"{% assign a = '1,2,3,4,5' | split: ',' %}{{ a[100] }}",
        expect="index out of range",
    ),
    Case(
        description="negative array index out of range",
        template=r"{% assign a = '1,2,3,4,5' | split: ',' %}{{ a[-100] }}",
        expect="index out of range",
    ),
    Case(
        description="key error",
        template=r"{{ obj['bar'] }}",
        expect="obj.bar is undefined",
        context={"obj": {"foo": 1}},
    ),
]


STRICT_DEFAULT_ENV = Environment(undefined=StrictDefaultUndefined)


@pytest.mark.parametrize(
    "case", STRICT_DEFAULT_TEST_CASES, ids=operator.attrgetter("description")
)
def test_strict_default_undefined(case: Case) -> None:
    """Test that the strict default undefined type raises an exception for
    everything other than the default filter."""
    template = STRICT_DEFAULT_ENV.from_string(case.template)

    with pytest.raises(UndefinedError, match=case.expect):
        template.render(**case.context)


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
    template = env.from_string(case.template)
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
    template = env.from_string(case.template)

    with pytest.raises(UnknownFilterError, match=case.expect):
        template.render()

    # And render async
    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    with pytest.raises(UnknownFilterError):
        asyncio.run(coro(template))


def test_default_undefined_magic() -> None:
    """Test the default undefined type magic methods."""
    undefined = Undefined("test", token=None)
    assert "foo" not in undefined
    assert int(undefined) == 0


def test_strict_undefined_magic() -> None:
    """Test the strict undefined type magic methods."""
    undefined = StrictUndefined("test", token=None)

    with pytest.raises(UndefinedError):
        _ = "foo" in undefined

    with pytest.raises(UndefinedError):
        int(undefined)  # type: ignore

    with pytest.raises(UndefinedError):
        list(undefined)

    with pytest.raises(UndefinedError):
        len(undefined)  # type: ignore

    with pytest.raises(UndefinedError):
        str(undefined)

    assert repr(undefined) == "StrictUndefined(test)"

    with pytest.raises(UndefinedError):
        bool(undefined)

    with pytest.raises(UndefinedError):
        hash(undefined)

    with pytest.raises(UndefinedError):
        reversed(undefined)  # type: ignore
