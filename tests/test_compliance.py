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
    data: dict[str, Any] = field(default_factory=dict)  # type: ignore
    templates: Optional[dict[str, str]] = None
    result: Optional[str] = None
    results: Optional[list[str]] = None
    invalid: Optional[bool] = None
    tags: list[str] = field(default_factory=list)  # type: ignore


FILENAME = "tests/golden-liquid/golden_liquid.json"

SKIP = {
    "filters, has, array of ints, default value": "Ruby behavioral quirk",
    "tags, case, unexpected when token, strict2": "TODO",
    "blank and empty, blank followed by bracketed segments is not a reserved word": "TODO",
    "blank and empty, blank followed by variable segments is not a reserved word": "TODO",
    "blank and empty, blank followed by variable segments is not a reserved word in a condition": "TODO",
    "blank and empty, blank followed by variable segments is not a reserved word on the right of a comparison": "TODO",
    "blank and empty, blank on left of a relational operators is false": "TODO",
    "blank and empty, blank on right of a relational operators is false": "TODO",
    "blank and empty, empty followed by bracketed segments is an error": "TODO",
    "blank and empty, empty followed by bracketed segments is not a reserved word": "TODO",
    "blank and empty, empty on left of a relational operators is false": "TODO",
    "blank and empty, empty on right of a relational operators is false": "TODO",
    "blank and empty, false is equal to blank": "TODO",
    "blank and empty, nil is equal to blank": "TODO",
    "blank and empty, null is equal to blank": "TODO",
    "blank and empty, undefined is equal to blank": "TODO",
    "identifiers, allowed symbols": "TODO",
    "identifiers, allowed symbols, parens": "TODO",
    "identifiers, false followed by variable segments is not a reserved word": "TODO",
    "identifiers, nil followed by variable segments is not a reserved word": "TODO",
    "identifiers, repeated parens": "TODO",
    "identifiers, true followed by variable segments is not a reserved word": "TODO",
    "range, slice uses range string representation": "TODO",
    "special, first of a string": "TODO",
    "special, last of a string": "TODO",
    "filters, first, first of a string": "TODO",
    "filters, last, last of a string": "TODO",
    "filters, squish, left is false": "TODO",
    "filters, squish, left is true": "TODO",
    "tags, for, range loop, negative offset, continue": "TODO",
    "tags, for, range loop, negative offset, negative limit": "TODO",
    "tags, for, range loop, offset, negative limit": "TODO",
    "identifiers, only digits, self": "TODO",
    "range, float from a variable is an error": "TODO",
    "tags, comment, incomplete nested output markup is a syntax error": "TODO",
    "tags, comment, unbalanced nested raw tag": "TODO",
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
    return [
        case for case in cases() if not case.invalid and "error string" not in case.tags
    ]


def invalid_cases() -> list[Case]:
    return [case for case in cases() if case.invalid or "error string" in case.tags]


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
