import asyncio
import json
import operator
import sys
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Optional

import pytest

from liquid import DictLoader
from liquid import Environment
from liquid.exceptions import LiquidError


@dataclass
class Case:
    """Test helper class."""

    name: str
    template: str
    data: dict[str, Any] = field(default_factory=dict)
    templates: Optional[dict[str, str]] = None
    result: Optional[str] = None
    results: Optional[list[str]] = None
    invalid: Optional[bool] = None
    tags: list[str] = field(default_factory=list)


FILENAME = "tests/golden-liquid/golden_liquid.json"

SKIP = {
    "filters, has, array of ints, default value": "Ruby behavioral quirk",
}


def cases() -> list[Case]:
    try:
        with open(FILENAME, encoding="utf8") as fd:
            data = json.load(fd)
    except FileNotFoundError:
        sys.stderr.write(
            "Did you forget to initialize the submodule? `git submodule update --init`"
        )
        raise
    return [Case(**case) for case in data["tests"]]


def valid_cases() -> list[Case]:
    return [case for case in cases() if not case.invalid]


def invalid_cases() -> list[Case]:
    return [case for case in cases() if case.invalid]


@pytest.mark.parametrize("case", valid_cases(), ids=operator.attrgetter("name"))
def test_compliance(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip(reason=SKIP[case.name])

    env = Environment(loader=DictLoader(case.templates or {}))
    if case.results is not None:
        assert env.from_string(case.template).render(**case.data) in case.results
    else:
        assert env.from_string(case.template).render(**case.data) == case.result


@pytest.mark.parametrize("case", valid_cases(), ids=operator.attrgetter("name"))
def test_compliance_async(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip(reason=SKIP[case.name])

    env = Environment(loader=DictLoader(case.templates or {}))
    template = env.from_string(case.template)

    async def coro() -> str:
        return await template.render_async(**case.data)

    if case.results is not None:
        assert asyncio.run(coro()) in case.results
    else:
        assert asyncio.run(coro()) == case.result


@pytest.mark.parametrize("case", invalid_cases(), ids=operator.attrgetter("name"))
def test_invalid_compliance(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip(reason=SKIP[case.name])

    env = Environment(loader=DictLoader(case.templates or {}))
    with pytest.raises(LiquidError):
        env.from_string(case.template).render(**case.data)


@pytest.mark.parametrize("case", invalid_cases(), ids=operator.attrgetter("name"))
def test_invalid_compliance_async(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip(reason=SKIP[case.name])

    env = Environment(loader=DictLoader(case.templates or {}))

    async def coro() -> str:
        template = env.from_string(case.template)
        return await template.render_async(**case.data)

    with pytest.raises(LiquidError):
        asyncio.run(coro())
