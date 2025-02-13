import operator
from dataclasses import dataclass
from dataclasses import field
from functools import partial
from inspect import isclass
from typing import Any

try:
    import markupsafe  # noqa: F401

    MARKUPSAFE_AVAILABLE = True
except ImportError:
    MARKUPSAFE_AVAILABLE = False


import pytest

from liquid import Environment
from liquid import Markup
from liquid.exceptions import Error
from liquid.extra.filters.html import script_tag


@dataclass(kw_only=True)
class Case:
    """Test helper class."""

    description: str
    val: Any
    expect: Any
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)


ENV = Environment()

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


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_script_tag_filter(case: Case) -> None:
    script_tag_ = partial(script_tag, environment=ENV)
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            script_tag_(case.val, *case.args, **case.kwargs)
    else:
        assert script_tag_(case.val, *case.args, **case.kwargs) == case.expect


AUTO_ESCAPE_ENV = Environment(autoescape=True)

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
]

if MARKUPSAFE_AVAILABLE:
    AUTO_ESCAPE_TEST_CASES.append(
        Case(
            description="safe url from context",
            val=Markup("<b>assets/assets/app.js</b>"),
            args=[],
            kwargs={},
            expect=(
                '<script src="&lt;b&gt;assets/assets/app.js&lt;/b&gt;" '
                'type="text/javascript"></script>'
            ),
        ),
    )


@pytest.mark.parametrize(
    "case", AUTO_ESCAPE_TEST_CASES, ids=operator.attrgetter("description")
)
def test_script_tag_filter_auto_escape(case: Case) -> None:
    if not MARKUPSAFE_AVAILABLE:
        pytest.skip(reason="this test requires markupsafe")

    script_tag_ = partial(script_tag, environment=AUTO_ESCAPE_ENV)
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            script_tag_(case.val, *case.args, **case.kwargs)
    else:
        assert script_tag_(case.val, *case.args, **case.kwargs) == case.expect
