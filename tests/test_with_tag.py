import asyncio
import json
import operator
from dataclasses import dataclass, field
from typing import Any

import pytest

from liquid import Environment, ExtendedParser
from liquid.tags import WithTag


@dataclass
class Case:
    name: str
    template: str
    data: dict[str, Any] = field(default_factory=dict)  # type: ignore
    result: str | None = None


SKIP: set[str] = set()

ENV = Environment(
    parser=ExtendedParser,
    conventional_operator_precedence=True,
)

ENV.tags["with"] = WithTag


with open("tests/with_tag.json", encoding="utf8") as fd:
    TEST_CASES = [Case(**case) for case in json.load(fd)["tests"]]


@pytest.mark.parametrize(
    "case",
    TEST_CASES,
    ids=operator.attrgetter("name"),
)
def test_filter(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    assert ENV.parse(case.template).render(case.data) == case.result


@pytest.mark.parametrize(
    "case",
    TEST_CASES,
    ids=operator.attrgetter("name"),
)
def test_filter_async(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    template = ENV.parse(case.template)

    async def coro() -> str:
        return await template.render_async(case.data)

    assert asyncio.run(coro()) == case.result
