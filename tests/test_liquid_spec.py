import json
import operator
from dataclasses import dataclass
from typing import Any

import pytest

from liquid import DictLoader, Environment, RenderContext, TemplateSource
from liquid.exceptions import LiquidError, TemplateNotFoundError

FILENAME = "tests/liquid_spec/liquid_spec.jsonl"

SKIP = {
    "tablerow_offset_from_dotted_variable",
    "tablerow_limit_from_dotted_variable",
    "tablerow_cols_from_dotted_variable",
    "date_format_P_am_pm_lowercase",
    "date_now_keyword",
    "date_today_keyword",
    "date_Today_capitalized",
}


@dataclass
class Case:
    name: str
    source: str
    data: dict[str, Any]
    templates: dict[str, str]
    expected: str | None


class MockLoader(DictLoader):
    def get_source(
        self,
        env: Environment,
        name: str,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> TemplateSource:
        if name in self.templates:
            return TemplateSource(name=name, text=self.templates[name])

        if name + ".liquid" in self.templates:
            return TemplateSource(name=name, text=self.templates[name + ".liquid"])

        if (name + ".liquid").lower() in self.templates:
            return TemplateSource(
                name=name, text=self.templates[(name + ".liquid").lower()]
            )

        raise TemplateNotFoundError(name)


with open(FILENAME, encoding="utf8") as fd:
    TEST_CASES = [Case(**json.loads(line)) for line in fd]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("name"))
def test_liquid_spec(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    env = Environment(loader=MockLoader(case.templates), strict_filters=False)

    if case.expected is None:
        with pytest.raises(LiquidError):
            env.parse(case.source).render(case.data)

    else:
        assert env.parse(case.source).render(case.data) == case.expected


# TODO: async
