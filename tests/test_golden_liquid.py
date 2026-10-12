import asyncio
import json
import operator
import sys
from dataclasses import dataclass, field
from typing import Any

import pytest

from liquid import DictLoader, Environment
from liquid.exceptions import LiquidError


@dataclass
class Case:
    name: str
    template: str
    data: dict[str, Any] = field(default_factory=dict)  # type: ignore
    templates: dict[str, str] | None = None
    result: str | None = None
    results: list[str] | None = None
    invalid: bool | None = None
    tags: list[str] = field(default_factory=list)  # type: ignore


FILENAME = "tests/golden_liquid/golden_liquid.json"

SKIP = {
    "tags, comment, incomplete nested output markup is a syntax error",
    "tags, comment, incomplete nested tags are a syntax error",
    "filters, date, well formed string",
    "filters, date, literal percent",
    "filters, date, negative timestamp string",
    "filters, date, seconds since epoch format directive",
    "identifiers, capture only digits",
    "identifiers, allowed symbols",
    "identifiers, allowed symbols, parens",
    "identifiers, only digits",
    "identifiers, repeated parens",
    # TODO:
    "filters, find, array of hashes, with a nil",
    "filters, find, mixed array, default value",
    "filters, find index, array of hashes, with a nil",
    "filters, find index, mixed array, default value",
    "filters, has, array of hashes, with a nil",
    "filters, has, mixed array, default value",
}


try:
    with open(FILENAME, encoding="utf8") as fd:
        TEST_CASES = [Case(**case) for case in json.load(fd)["tests"]]
except FileNotFoundError:
    sys.stderr.write(
        "Did you forget to initialize the submodule? `git submodule update --init`"
    )
    raise


VALID_TEST_CASES = [
    case for case in TEST_CASES if not case.invalid and "error string" not in case.tags
]


INVALID_TEST_CASES = [
    case for case in TEST_CASES if case.invalid or "error string" in case.tags
]


@pytest.mark.parametrize("case", VALID_TEST_CASES, ids=operator.attrgetter("name"))
def test_golden(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    env = Environment(loader=DictLoader(case.templates or {}))

    if case.results is not None:
        assert env.parse(case.template).render(case.data) in case.results
    else:
        assert env.parse(case.template).render(case.data) == case.result


@pytest.mark.parametrize("case", VALID_TEST_CASES, ids=operator.attrgetter("name"))
def test_golden_async(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    env = Environment(loader=DictLoader(case.templates or {}))
    template = env.parse(case.template)

    async def coro() -> str:
        return await template.render_async(case.data)

    if case.results is not None:
        assert asyncio.run(coro()) in case.results
    else:
        assert asyncio.run(coro()) == case.result


@pytest.mark.parametrize("case", INVALID_TEST_CASES, ids=operator.attrgetter("name"))
def test_invalid_golden(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    env = Environment(loader=DictLoader(case.templates or {}))
    with pytest.raises(LiquidError):
        env.parse(case.template).render(case.data)


@pytest.mark.parametrize("case", INVALID_TEST_CASES, ids=operator.attrgetter("name"))
def test_invalid_golden_async(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    env = Environment(loader=DictLoader(case.templates or {}))

    async def coro() -> str:
        template = env.parse(case.template)
        return await template.render_async(case.data)

    with pytest.raises(LiquidError):
        asyncio.run(coro())
