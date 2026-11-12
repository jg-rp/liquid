import asyncio
import json
import operator
from dataclasses import dataclass, field
from typing import Any

import pytest

from liquid import DictLoader, Environment, ExtendedParser


@dataclass(kw_only=True)
class Case:
    name: str
    template: str
    templates: dict[str, str] = field(default_factory=dict)  # pyright: ignore[reportUnknownVariableType]
    data: dict[str, Any] = field(default_factory=dict)  # pyright: ignore[reportUnknownVariableType]
    result: str | None = None


SKIP: set[str] = set()

with open("tests/extends_tag.json", encoding="utf8") as fd:
    TEST_CASES = [Case(**case) for case in json.load(fd)["tests"]]


@pytest.mark.parametrize(
    "case",
    TEST_CASES,
    ids=operator.attrgetter("name"),
)
def test_extends_tag(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    env = Environment(
        extra=True,
        loader=DictLoader(case.templates),
        parser=ExtendedParser,
        conventional_operator_precedence=True,
    )

    assert env.parse(case.template).render(case.data) == case.result


@pytest.mark.parametrize(
    "case",
    TEST_CASES,
    ids=operator.attrgetter("name"),
)
def test_extends_tag_async(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    env = Environment(
        extra=True,
        loader=DictLoader(case.templates),
        parser=ExtendedParser,
        conventional_operator_precedence=True,
    )

    template = env.parse(case.template)

    async def coro() -> str:
        return await template.render_async(case.data)

    assert asyncio.run(coro()) == case.result
