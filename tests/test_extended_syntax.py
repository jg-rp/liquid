import asyncio
import json
import operator
from dataclasses import dataclass, field
from typing import Any

import pytest

from liquid import Environment, ExtendedParser


@dataclass
class Case:
    name: str
    expression: str
    data: dict[str, Any] = field(default_factory=dict)  # pyright: ignore[reportUnknownVariableType]
    result: str | None = None


SKIP: set[str] = set()

ENV = Environment(
    parser=ExtendedParser,
    conventional_operator_precedence=True,
)


def load_tests(path: str) -> list[Case]:
    with open(path, encoding="utf8") as fd:
        return [Case(**case) for case in json.load(fd)["tests"]]


@pytest.mark.parametrize(
    "case",
    load_tests("tests/extended_filter.json"),
    ids=operator.attrgetter("name"),
)
def test_filter(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    assert ENV.parse("{{ " + case.expression + " }}").render(case.data) == case.result


@pytest.mark.parametrize(
    "case",
    load_tests("tests/extended_filter.json"),
    ids=operator.attrgetter("name"),
)
def test_filter_async(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    template = ENV.parse("{{ " + case.expression + " }}")

    async def coro() -> str:
        return await template.render_async(case.data)

    assert asyncio.run(coro()) == case.result


@pytest.mark.parametrize(
    "case",
    load_tests("tests/extended_logic.json"),
    ids=operator.attrgetter("name"),
)
def test_logic(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    assert ENV.parse("{{ " + case.expression + " }}").render(case.data) == case.result


@pytest.mark.parametrize(
    "case",
    load_tests("tests/extended_logic.json"),
    ids=operator.attrgetter("name"),
)
def test_logic_async(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    template = ENV.parse("{{ " + case.expression + " }}")

    async def coro() -> str:
        return await template.render_async(case.data)

    assert asyncio.run(coro()) == case.result


@pytest.mark.parametrize(
    "case",
    load_tests("tests/extended_ternary.json"),
    ids=operator.attrgetter("name"),
)
def test_ternary(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    assert ENV.parse("{{ " + case.expression + " }}").render(case.data) == case.result


@pytest.mark.parametrize(
    "case",
    load_tests("tests/extended_ternary.json"),
    ids=operator.attrgetter("name"),
)
def test_ternary_async(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    template = ENV.parse("{{ " + case.expression + " }}")

    async def coro() -> str:
        return await template.render_async(case.data)

    assert asyncio.run(coro()) == case.result
