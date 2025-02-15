import asyncio
from typing import List
from typing import Tuple

import pytest

from liquid import DictLoader
from liquid import Environment
from liquid import Mode
from liquid import golden
from liquid.exceptions import Error
from liquid.future import Environment as FutureEnvironment
from liquid.golden.case import Case
from liquid.template import AwareBoundTemplate
from liquid.template import FutureAwareBoundTemplate

TEST_CASES: List[Tuple[str, Case]] = [
    (suite.__name__.split(".")[-1], case)
    for suite in golden.test_cases
    for case in suite.cases
]

DEFAULT_TEST_CASES = [case for case in TEST_CASES if not case[1].future]


@pytest.mark.parametrize(
    "case", DEFAULT_TEST_CASES, ids=lambda c: f"{c[0]}: {c[1].description}"
)
def test_golden_liquid(case: Tuple[str, Case]) -> None:
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
    "case", DEFAULT_TEST_CASES, ids=lambda c: f"{c[0]}: {c[1].description}"
)
def test_golden_liquid_async(case: Tuple[str, Case]) -> None:
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


@pytest.mark.parametrize(
    "case", TEST_CASES, ids=lambda c: f"{c[0]}: {c[1].description}"
)
def test_golden_future(case: Tuple[str, Case]) -> None:
    case_ = case[1]

    loader = DictLoader(case_.partials)
    env = FutureEnvironment(loader=loader, tolerance=Mode.STRICT, globals=case_.globals)
    env.template_class = FutureAwareBoundTemplate

    if case_.error:
        with pytest.raises(Error):
            env.from_string(case_.template).render()
    else:
        assert env.from_string(case_.template).render() == case_.expect


@pytest.mark.parametrize(
    "case", TEST_CASES, ids=lambda c: f"{c[0]}: {c[1].description}"
)
def test_golden_future_async(case: Tuple[str, Case]) -> None:
    case_ = case[1]

    loader = DictLoader(case_.partials)
    env = FutureEnvironment(loader=loader, tolerance=Mode.STRICT, globals=case_.globals)
    env.template_class = FutureAwareBoundTemplate

    async def coro() -> str:
        template = env.from_string(case_.template)
        return await template.render_async()

    if case_.error:
        with pytest.raises(Error):
            asyncio.run(coro())
    else:
        assert asyncio.run(coro()) == case_.expect
