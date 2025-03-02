import asyncio

import pytest

from liquid import DictLoader
from liquid import Environment
from liquid import Mode
from liquid import golden
from liquid.exceptions import Error
from liquid.golden.case import Case
from liquid.template import AwareBoundTemplate

TEST_CASES: list[tuple[str, Case]] = [
    (suite.__name__.split(".")[-1], case)
    for suite in golden.test_cases
    for case in suite.cases
]


@pytest.mark.parametrize(
    "case", TEST_CASES, ids=lambda c: f"{c[0]}: {c[1].description}"
)
def test_golden_liquid(case: tuple[str, Case]) -> None:
    case_ = case[1]

    loader = DictLoader(case_.partials)
    env = Environment(loader=loader, tolerance=Mode.STRICT, globals=case_.globals)
    env.template_class = AwareBoundTemplate

    if case_.error:
        with pytest.raises(Error):
            env.from_string(case_.template).render()
    else:
        assert env.from_string(case_.template).render() == case_.expect


@pytest.mark.parametrize(
    "case", TEST_CASES, ids=lambda c: f"{c[0]}: {c[1].description}"
)
def test_golden_liquid_async(case: tuple[str, Case]) -> None:
    case_ = case[1]

    loader = DictLoader(case_.partials)
    env = Environment(loader=loader, tolerance=Mode.STRICT, globals=case_.globals)
    env.template_class = AwareBoundTemplate

    async def coro() -> str:
        template = env.from_string(case_.template)
        return await template.render_async()

    if case_.error:
        with pytest.raises(Error):
            asyncio.run(coro())
    else:
        assert asyncio.run(coro()) == case_.expect
