import operator
from dataclasses import dataclass, field
from typing import Any

import markupsafe
import pytest

from liquid import Environment, FilterContext, RenderContext
from liquid.filters import script_tag
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
        val="assets/app.js",
        args=[],
        kwargs={},
        expect='<script src="assets/app.js" type="text/javascript"></script>',
    ),
    Case(
        description="remote url",
        val="https://example.com/static/assets/app.js",
        args=[],
        kwargs={},
        expect=(
            "<script "
            'src="https://example.com/static/assets/app.js" '
            'type="text/javascript">'
            "</script>"
        ),
    ),
    Case(
        description="not a string",
        val=42,
        args=[],
        kwargs={},
        expect='<script src="42" type="text/javascript"></script>',
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
def test_script_tag_filter(case: Case) -> None:
    assert script_tag(CONTEXT, case.val, *case.args, **case.kwargs) == case.expect


AUTO_ESCAPE_TEST_CASES = [
    Case(
        description="relative url",
        val="assets/assets/app.js",
        args=[],
        kwargs={},
        expect='<script src="assets/assets/app.js" type="text/javascript"></script>',
    ),
    Case(
        description="unsafe url from context",
        val="<b>assets/assets/app.js</b>",
        args=[],
        kwargs={},
        expect=(
            '<script src="&lt;b&gt;assets/assets/app.js&lt;/b&gt;" '
            'type="text/javascript"></script>'
        ),
    ),
    Case(
        description="safe url from context",
        val=markupsafe.Markup("<b>assets/assets/app.js</b>"),
        args=[],
        kwargs={},
        expect=(
            '<script src="&lt;b&gt;assets/assets/app.js&lt;/b&gt;" '
            'type="text/javascript"></script>'
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
def test_script_tag_filter_auto_escape(case: Case) -> None:
    assert (
        script_tag(AUTO_ESCAPE_CONTEXT, case.val, *case.args, **case.kwargs)
        == case.expect
    )
