import asyncio

from liquid import parse
from liquid.static_analysis import Segments

SOURCE = """\
Hello, {{ you }}!
{% assign x = 'foo' | upcase %}
{% for ch in x %}
    - {{ ch }}
{% endfor %}
Goodbye, {{ you.first_name | capitalize }} {{ you.last_name }}
Goodbye, {{ you.first_name }} {{ you.last_name }}
"""

TEMPLATE = parse(SOURCE)


def test_get_variables() -> None:
    assert TEMPLATE.variables() == ["you", "x", "ch"]


def test_get_variables_async() -> None:
    async def coro() -> list[str]:
        return await TEMPLATE.variables_async()

    assert asyncio.run(coro()) == ["you", "x", "ch"]


def test_get_paths() -> None:
    assert sorted(TEMPLATE.variable_paths()) == sorted(
        [
            "you",
            "x",
            "ch",
            "you.first_name",
            "you.last_name",
        ]
    )


def test_get_paths_async() -> None:
    async def coro() -> list[str]:
        return await TEMPLATE.variable_paths_async()

    assert sorted(asyncio.run(coro())) == sorted(
        ["you", "x", "ch", "you.first_name", "you.last_name"]
    )


def test_get_segments() -> None:
    assert sorted(TEMPLATE.variable_segments()) == sorted(
        [
            ["you"],
            ["x"],
            ["ch"],
            ["you", "first_name"],
            ["you", "last_name"],
        ]
    )


def test_get_segments_async() -> None:
    async def coro() -> list[Segments]:
        return await TEMPLATE.variable_segments_async()

    assert sorted(asyncio.run(coro())) == sorted(
        [
            ["you"],
            ["x"],
            ["ch"],
            ["you", "first_name"],
            ["you", "last_name"],
        ]
    )


def test_get_global_variables() -> None:
    assert TEMPLATE.global_variables() == ["you"]


def test_get_global_variables_async() -> None:
    async def coro() -> list[str]:
        return await TEMPLATE.global_variables_async()

    assert asyncio.run(coro()) == ["you"]


def test_get_global_paths() -> None:
    assert sorted(TEMPLATE.global_variable_paths()) == sorted(
        [
            "you",
            "you.first_name",
            "you.last_name",
        ]
    )


def test_get_global_paths_async() -> None:
    async def coro() -> list[str]:
        return await TEMPLATE.global_variable_paths_async()

    assert sorted(asyncio.run(coro())) == sorted(
        ["you", "you.first_name", "you.last_name"]
    )


def test_get_global_segments() -> None:
    assert sorted(TEMPLATE.global_variable_segments()) == sorted(
        [
            ["you"],
            ["you", "first_name"],
            ["you", "last_name"],
        ]
    )


def test_get_global_segments_async() -> None:
    async def coro() -> list[Segments]:
        return await TEMPLATE.global_variable_segments_async()

    assert sorted(asyncio.run(coro())) == sorted(
        [
            ["you"],
            ["you", "first_name"],
            ["you", "last_name"],
        ]
    )


def test_get_filter_names() -> None:
    assert sorted(TEMPLATE.filter_names()) == sorted(["upcase", "capitalize"])


def test_get_filter_names_async() -> None:
    async def coro() -> list[str]:
        return await TEMPLATE.filter_names_async()

    assert sorted(asyncio.run(coro())) == sorted(["upcase", "capitalize"])


def test_get_tag_names() -> None:
    assert sorted(TEMPLATE.tag_names()) == sorted(["assign", "for"])


def test_get_tag_names_async() -> None:
    async def coro() -> list[str]:
        return await TEMPLATE.tag_names_async()

    assert sorted(asyncio.run(coro())) == sorted(["assign", "for"])
