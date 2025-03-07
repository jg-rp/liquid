"""Test filter decorators and helpers."""

import asyncio

import pytest

from liquid import Environment
from liquid import RenderContext
from liquid.exceptions import FilterArgumentError
from liquid.filter import int_arg
from liquid.filter import liquid_filter
from liquid.filter import num_arg
from liquid.filter import with_context


@liquid_filter
@with_context
def some_filter(val: str, arg: str, *, context: RenderContext) -> str:
    """Contrived filter function making use of `with_context`."""
    return val + str(context.resolve(arg))


def test_filter_with_context() -> None:
    """Test that we can pass the active context to a filter function."""
    env = Environment(strict_filters=True)
    env.add_filter("some", some_filter)

    template = env.from_string(r"{{ 'Hello, ' | some: 'you' }}")
    result = template.render(you="World")

    assert result == "Hello, World"


def test_int_arg_fail() -> None:
    """Test that a suitable exception is raised if we can't cast to an int."""
    with pytest.raises(FilterArgumentError):
        int_arg("foo")


def test_int_arg_with_default() -> None:
    """Test that a default is returned if we can't cast to an int."""
    assert int_arg("foo", 99) == 99


def test_num_arg_fail_string() -> None:
    """Test that a suitable exception is raised if we can't cast to a number."""
    with pytest.raises(FilterArgumentError):
        num_arg("foo")


def test_num_arg_with_default() -> None:
    """Test that a default is returned if we can't cast to a number."""
    assert num_arg("foo", 99.8) == 99.8


def test_num_arg_no_default() -> None:
    """Test that an exception is raised if a default is not given."""
    with pytest.raises(FilterArgumentError):
        num_arg(object())


class SomeFilter:
    """A mock class-based filter implementing the async filter interface."""

    def __call__(self, val: object) -> str:
        return "Hello, " + str(val)

    async def filter_async(self, val: object) -> str:
        return "Goodbye, " + str(val)


class OtherFilter:
    """A mock class-based filter implementing the async filter interface.

    Includes arguments.
    """

    with_environment = True

    def __call__(self, val: object, post: str, environment: Environment) -> str:
        assert isinstance(environment, Environment)
        return "Hello, " + str(val) + post

    async def filter_async(
        self, val: object, post: str, environment: Environment
    ) -> str:
        assert isinstance(environment, Environment)
        return "Goodbye, " + str(val) + post


def test_call_an_async_filter() -> None:
    """Test that we can await an async filter."""
    env = Environment(strict_filters=True)
    env.add_filter("greeting", SomeFilter())
    template = env.from_string(r"{{ you | greeting }}")
    result = template.render(you="World")
    assert result == "Hello, World"


def test_await_an_async_filter() -> None:
    """Test that we can await an async filter."""
    env = Environment(strict_filters=True)
    env.add_filter("greeting", SomeFilter())
    template = env.from_string(r"{{ you | greeting }}")

    async def coro() -> str:
        return await template.render_async(you="World")

    result = asyncio.run(coro())
    assert result == "Goodbye, World"


def test_await_an_async_filter_with_args() -> None:
    """Test that we can await an async filter with arguments."""
    env = Environment(strict_filters=True)
    env.add_filter("greeting", OtherFilter())
    template = env.from_string(r"{{ you | greeting: '!' }}")

    async def coro() -> str:
        return await template.render_async(you="World")

    result = asyncio.run(coro())
    assert result == "Goodbye, World!"


def test_await_an_async_filter_with_keyword_args() -> None:
    """Test that we can await an async filter with keyword arguments."""
    env = Environment(strict_filters=True)
    env.add_filter("greeting", OtherFilter())
    template = env.from_string(r"{{ you | greeting: post:'!' }}")

    async def coro() -> str:
        return await template.render_async(you="World")

    result = asyncio.run(coro())
    assert result == "Goodbye, World!"
