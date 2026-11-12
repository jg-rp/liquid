import operator
from dataclasses import dataclass, field
from typing import Any

import markupsafe
import pytest

from liquid import Environment, FilterContext, RenderContext
from liquid.filters import stylesheet_tag
from liquid.tokens import TOKEN_EOI


@dataclass
class Case:
    description: str
    val: Any
    expect: Any
    args: list[Any] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    kwargs: dict[str, Any] = field(default_factory=dict)  # pyright: ignore[reportUnknownVariableType]


TEST_CASES = [
    Case(
        description="relative url",
        val="assets/style.css",
        args=[],
        kwargs={},
        expect=(
            '<link href="assets/style.css" rel="stylesheet" '
            'type="text/css" media="all" />'
        ),
    ),
    Case(
        description="remote url",
        val="https://example.com/static/style.css",
        args=[],
        kwargs={},
        expect=(
            '<link href="https://example.com/static/style.css" '
            'rel="stylesheet" type="text/css" media="all" />'
        ),
    ),
    Case(
        description="html escape url",
        val="<b>assets/style.css</b>",
        args=[],
        kwargs={},
        expect=(
            '<link href="&lt;b&gt;assets/style.css&lt;/b&gt;" rel="stylesheet" '
            'type="text/css" media="all" />'
        ),
    ),
    Case(
        description="not a string",
        val=42,
        args=[],
        kwargs={},
        expect=('<link href="42" rel="stylesheet" type="text/css" media="all" />'),
    ),
]

ENV = Environment(extra=True)

CONTEXT = FilterContext(
    RenderContext(
        ENV.parse(""),
    ),
    (TOKEN_EOI, 0, 0),
)


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_stylesheet_tag_filter(case: Case) -> None:
    assert stylesheet_tag(CONTEXT, case.val, *case.args, **case.kwargs) == case.expect


AUTO_ESCAPE_TEST_CASES = [
    Case(
        description="relative url",
        val="assets/style.css",
        args=[],
        kwargs={},
        expect=(
            '<link href="assets/style.css" rel="stylesheet" '
            'type="text/css" media="all" />'
        ),
    ),
    Case(
        description="unsafe url from context",
        val="<b>assets/style.css</b>",
        args=[],
        kwargs={},
        expect=(
            '<link href="&lt;b&gt;assets/style.css&lt;/b&gt;" rel="stylesheet" '
            'type="text/css" media="all" />'
        ),
    ),
    Case(
        description="safe url from context",
        val=markupsafe.Markup("<b>assets/style.css</b>"),
        args=[],
        kwargs={},
        expect=(
            '<link href="&lt;b&gt;assets/style.css&lt;/b&gt;" rel="stylesheet" '
            'type="text/css" media="all" />'
        ),
    ),
]

AUTO_ESCAPE_ENV = Environment(extra=True, autoescape=True)

AUTO_ESCAPE_CONTEXT = FilterContext(
    RenderContext(
        AUTO_ESCAPE_ENV.parse(""),
    ),
    (TOKEN_EOI, 0, 0),
)


@pytest.mark.parametrize(
    "case", AUTO_ESCAPE_TEST_CASES, ids=operator.attrgetter("description")
)
def test_stylesheet_tag_filter_auto_escape(case: Case) -> None:
    assert (
        stylesheet_tag(AUTO_ESCAPE_CONTEXT, case.val, *case.args, **case.kwargs)
        == case.expect
    )
