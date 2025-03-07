import asyncio

import pytest

from liquid import Environment
from liquid import Undefined
from liquid.exceptions import LiquidSyntaxError


class MockEnv(Environment):
    keyword_assignment = True


ENV = MockEnv(extra=True)


def test_define_a_macro() -> None:
    source = "{% macro 'func' %}Hello, World!{% endmacro %}"
    want = ""

    async def coro() -> str:
        return await ENV.render_async(source)

    assert ENV.render(source) == want
    assert asyncio.run(coro()) == want


def test_define_and_call_a_macro() -> None:
    source = "{% macro 'func' %}Hello, World!{% endmacro %}{% call 'func' %}"
    want = "Hello, World!"

    async def coro() -> str:
        return await ENV.render_async(source)

    assert ENV.render(source) == want
    assert asyncio.run(coro()) == want


def test_unquoted_macro_names() -> None:
    source = (
        "{% macro 'func' %}Hello, World!{% endmacro %}{% call func %}{% call 'func' %}"
    )

    want = "Hello, World!Hello, World!"

    async def coro() -> str:
        return await ENV.render_async(source)

    assert ENV.render(source) == want
    assert asyncio.run(coro()) == want


def test_call_macro_with_a_positional_argument() -> None:
    source = (
        "{% macro func, you %}Hello, {{ you }}!{% endmacro %}"
        "{% call func, 'World' %}"
        "{% call func, 'Liquid' %}"
    )

    want = "Hello, World!Hello, Liquid!"

    async def coro() -> str:
        return await ENV.render_async(source)

    assert ENV.render(source) == want
    assert asyncio.run(coro()) == want


def test_call_macro_with_a_default_argument() -> None:
    source = (
        "{% macro func, you='Brian' %}Hello, {{ you }}!{% endmacro %}"
        "{% call func %} "
        "{% call func, 'Liquid' %}"
    )

    want = "Hello, Brian! Hello, Liquid!"

    async def coro() -> str:
        return await ENV.render_async(source)

    assert ENV.render(source) == want
    assert asyncio.run(coro()) == want


def test_call_macro_with_a_default_argument_by_name() -> None:
    source = (
        "{% macro func, you='Brian' %}Hello, {{ you }}!{% endmacro %}"
        "{% call func %} "
        "{% call func, you='Liquid' %}"
    )

    want = "Hello, Brian! Hello, Liquid!"

    async def coro() -> str:
        return await ENV.render_async(source)

    assert ENV.render(source) == want
    assert asyncio.run(coro()) == want


def test_call_macro_with_a_variable_default_argument() -> None:
    source = (
        "{% macro func, you=a.b %}Hello, {{ you }}!{% endmacro %}"
        "{% call func %} "
        "{% call func, 'Liquid' %}"
    )

    want = "Hello, Brian! Hello, Liquid!"
    data = {"a": {"b": "Brian"}}

    async def coro() -> str:
        return await ENV.render_async(source, **data)

    assert ENV.render(source, **data) == want
    assert asyncio.run(coro()) == want


def test_excess_arguments() -> None:
    source = (
        "{% macro 'func' %}{{ args | join: '-' }}{% endmacro %}{% call 'func' 1, 2 %}"
    )

    want = "1-2"

    async def coro() -> str:
        return await ENV.render_async(source)

    assert ENV.render(source) == want
    assert asyncio.run(coro()) == want


def test_excess_keyword_arguments() -> None:
    source = (
        "{% macro 'func' %}"
        "{% for arg in kwargs %}"
        "{{ arg[0] }} => {{ arg[1] }}, "
        "{% endfor %}"
        "{% endmacro %}"
        "{% call 'func', a: 1, b: 2 %}"
    )

    want = "a => 1, b => 2, "

    async def coro() -> str:
        return await ENV.render_async(source)

    assert ENV.render(source) == want
    assert asyncio.run(coro()) == want


class MockUndefined(Undefined):
    def __str__(self) -> str:
        return "UNDEFINED"


def test_missing_argument_is_undefined() -> None:
    source = "{% macro 'func', foo %}{{ foo }}{% endmacro %}{% call 'func' %}"
    want = "UNDEFINED"

    env = MockEnv(extra=True, undefined=MockUndefined)

    async def coro() -> str:
        return await env.from_string(source).render_async()

    assert env.from_string(source).render() == want
    assert asyncio.run(coro()) == want


def test_undefined_macro() -> None:
    source = "{% call 'func' %}"
    want = "UNDEFINED"

    env = MockEnv(extra=True, undefined=MockUndefined)

    async def coro() -> str:
        return await env.from_string(source).render_async()

    assert env.from_string(source).render() == want
    assert asyncio.run(coro()) == want


def test_default_argument_before_positional() -> None:
    source = (
        "{% macro 'func' you: 'brian', greeting %}"
        "{{ greeting }}, {{ you }}!"
        "{% endmacro %}"
        "{% call 'func' %} "
        "{% call 'func' you: 'World', greeting: 'Goodbye' %}"
    )

    want = ", brian! Goodbye, World!"

    async def coro() -> str:
        return await ENV.render_async(source)

    assert ENV.render(source) == want
    assert asyncio.run(coro()) == want


def test_no_comma_between_name_and_arg() -> None:
    source = (
        "{% macro func you %}Hello, {{ you }}!{% endmacro %}"
        "{% call func 'World' %}"
        "{% call func 'Liquid' %}"
    )

    want = "Hello, World!Hello, Liquid!"

    async def coro() -> str:
        return await ENV.render_async(source)

    assert ENV.render(source) == want
    assert asyncio.run(coro()) == want


def test_trailing_comma() -> None:
    source = (
        "{% macro func, you, %}Hello, {{ you }}!{% endmacro %}"
        "{% call func 'World', %}"
        "{% call func 'Liquid', %}"
    )

    want = "Hello, World!Hello, Liquid!"

    async def coro() -> str:
        return await ENV.render_async(source)

    assert ENV.render(source) == want
    assert asyncio.run(coro()) == want


def test_excess_commas() -> None:
    source = (
        "{% macro func, you,, %}Hello, {{ you }}!{% endmacro %}"
        "{% call func 'World',, %}"
        "{% call func 'Liquid',, %}"
    )

    async def coro() -> str:
        return await ENV.render_async(source)

    with pytest.raises(LiquidSyntaxError):
        ENV.render(source)

    with pytest.raises(LiquidSyntaxError):
        assert asyncio.run(coro())
