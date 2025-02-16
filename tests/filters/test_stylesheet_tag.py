import operator
from dataclasses import dataclass
from dataclasses import field
from functools import partial
from inspect import isclass
from typing import Any
from typing import Dict
from typing import List

import pytest

from liquid import Environment
from liquid import Markup
from liquid.exceptions import Error
from liquid.extra.filters.html import stylesheet_tag


@dataclass
class Case:
    """Test helper class."""

    description: str
    val: Any
    expect: Any
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)


ENV = Environment()

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


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_stylesheet_tag_filter(case: Case) -> None:
    stylesheet_tag_ = partial(stylesheet_tag, environment=ENV)
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            stylesheet_tag_(case.val, *case.args, **case.kwargs)
    else:
        assert stylesheet_tag_(case.val, *case.args, **case.kwargs) == case.expect


AUTO_ESCAPE_ENV = Environment(autoescape=True)

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
        val=Markup("<b>assets/style.css</b>"),
        args=[],
        kwargs={},
        expect=(
            '<link href="&lt;b&gt;assets/style.css&lt;/b&gt;" rel="stylesheet" '
            'type="text/css" media="all" />'
        ),
    ),
]


@pytest.mark.parametrize(
    "case", AUTO_ESCAPE_TEST_CASES, ids=operator.attrgetter("description")
)
def test_stylesheet_tag_filter_auto_escape(case: Case) -> None:
    stylesheet_tag_ = partial(stylesheet_tag, environment=AUTO_ESCAPE_ENV)
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            stylesheet_tag_(case.val, *case.args, **case.kwargs)
    else:
        assert stylesheet_tag_(case.val, *case.args, **case.kwargs) == case.expect
