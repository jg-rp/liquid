"""Test cases for analyzing a template's tags using `Environment.analyze_tags`."""

import asyncio
import operator
from dataclasses import dataclass
from dataclasses import field

import pytest

from liquid import DictLoader
from liquid import Environment
from liquid.analyze_tags import TagAnalysis
from liquid.analyze_tags import TagMap
from liquid.context import RenderContext
from liquid.extra.tags import WithTag
from liquid.span import Span


@dataclass
class Case:
    """Table-driven test case helper."""

    description: str
    source: str
    all_tags: TagMap = field(default_factory=dict)
    tags: TagMap = field(default_factory=dict)
    unclosed_tags: TagMap = field(default_factory=dict)
    unexpected_tags: TagMap = field(default_factory=dict)
    unknown_tags: TagMap = field(default_factory=dict)


def _assert_tags(tag_analysis: TagAnalysis, case: Case) -> None:
    assert tag_analysis.all_tags == case.all_tags
    assert tag_analysis.tags == case.tags
    assert tag_analysis.unclosed_tags == case.unclosed_tags
    assert tag_analysis.unexpected_tags == case.unexpected_tags
    assert tag_analysis.unknown_tags == case.unknown_tags


TEST_CASES: list[Case] = [
    Case(description="no tags", source="hello"),
    Case(
        description="inline tag",
        source="{% assign foo = 'bar' %}",
        all_tags={"assign": [Span("<string>", 3)]},
        tags={"assign": [Span("<string>", 3)]},
    ),
    Case(
        description="one block tag",
        source="{% if foo %}{% endif %}",
        all_tags={
            "if": [Span("<string>", 3)],
            "endif": [Span("<string>", 15)],
        },
        tags={"if": [Span("<string>", 3)]},
    ),
    Case(
        description="two block tags",
        source="{% if foo %}{% endif %}\n{% if bar %}{% endif %}",
        all_tags={
            "if": [Span("<string>", 3), Span("<string>", 27)],
            "endif": [Span("<string>", 15), Span("<string>", 39)],
        },
        tags={"if": [Span("<string>", 3), Span("<string>", 27)]},
    ),
    Case(
        description="unknown block tag",
        source="{% form foo %}{% endform %}",
        all_tags={
            "form": [Span("<string>", 3)],
            "endform": [Span("<string>", 17)],
        },
        tags={"form": [Span("<string>", 3)]},
        unknown_tags={"form": [Span("<string>", 3)]},
    ),
    Case(
        description="unbalanced block tag",
        source="{% if foo %}{% if bar %}{% endif %}\n{% if baz %}{% endif %}",
        all_tags={
            "if": [Span("<string>", 3), Span("<string>", 15), Span("<string>", 39)],
            "endif": [Span("<string>", 27), Span("<string>", 51)],
        },
        tags={"if": [Span("<string>", 3), Span("<string>", 15), Span("<string>", 39)]},
        unclosed_tags={"if": [Span("<string>", 3)]},
    ),
    Case(
        description="unbalanced block tag without inferred end tag",
        source=(
            "{% for foo in bar %}\n{% if foo %}\n    {{ foo | upcase }}\n{% endif %}"
        ),
        all_tags={
            "for": [Span("<string>", 3)],
            "if": [Span("<string>", 24)],
            "endif": [Span("<string>", 60)],
        },
        tags={"if": [Span("<string>", 24)], "for": [Span("<string>", 3)]},
        unclosed_tags={"for": [Span("<string>", 3)]},
    ),
    Case(
        description="end block typo",
        source="{% if foo %}{% if bar %}{% endif %}\n{% endi %}",
        all_tags={
            "if": [Span("<string>", 3), Span("<string>", 15)],
            "endif": [Span("<string>", 27)],
            "endi": [Span("<string>", 39)],
        },
        tags={"if": [Span("<string>", 3), Span("<string>", 15)]},
        unclosed_tags={"if": [Span("<string>", 3)]},
        unknown_tags={"endi": [Span("<string>", 39)]},
    ),
    Case(
        description="end block with wrong name",
        source="{% if foo %}{% if bar %}{% endif %}\n{% endfor %}",
        all_tags={
            "if": [Span("<string>", 3), Span("<string>", 15)],
            "endif": [Span("<string>", 27)],
            "endfor": [Span("<string>", 39)],
        },
        tags={"if": [Span("<string>", 3), Span("<string>", 15)]},
        unclosed_tags={"if": [Span("<string>", 3)]},
    ),
    Case(
        description="unexpected closing of inline tag",
        source="{% increment foo %}{% endincrement %}",
        all_tags={
            "increment": [Span("<string>", 3)],
            "endincrement": [Span("<string>", 22)],
        },
        tags={"increment": [Span("<string>", 3)]},
        unknown_tags={"endincrement": [Span("<string>", 22)]},
    ),
    Case(
        description="inner tag",
        source="{% if foo %}{% else %}{% endif %}",
        all_tags={
            "if": [Span("<string>", 3)],
            "else": [Span("<string>", 15)],
            "endif": [Span("<string>", 25)],
        },
        tags={"if": [Span("<string>", 3)]},
    ),
    Case(
        description="inner break tag",
        source="{% for foo in bar %}{% break %}{% endfor %}",
        all_tags={
            "for": [Span("<string>", 3)],
            "break": [Span("<string>", 23)],
            "endfor": [Span("<string>", 34)],
        },
        tags={"for": [Span("<string>", 3)]},
    ),
    Case(
        description="inner continue tag",
        source="{% for foo in bar %}{% continue %}{% endfor %}",
        all_tags={
            "for": [Span("<string>", 3)],
            "continue": [Span("<string>", 23)],
            "endfor": [Span("<string>", 37)],
        },
        tags={"for": [Span("<string>", 3)]},
    ),
    Case(
        description="orphaned inner tag",
        source="{% if foo %}{% endif %}{% else %}",
        all_tags={
            "if": [Span("<string>", 3)],
            "else": [Span("<string>", 26)],
            "endif": [Span("<string>", 15)],
        },
        tags={"if": [Span("<string>", 3)]},
        unexpected_tags={"else": [Span("<string>", 26)]},
    ),
    Case(
        description="orphaned break tag",
        source="{% for foo in bar %}{% endfor %}{% break %}",
        all_tags={
            "for": [Span("<string>", 3)],
            "break": [Span("<string>", 35)],
            "endfor": [Span("<string>", 23)],
        },
        tags={"for": [Span("<string>", 3)]},
        unexpected_tags={"break": [Span("<string>", 35)]},
    ),
    Case(
        description="orphaned continue tag",
        source="{% for foo in bar %}{% endfor %}{% continue %}",
        all_tags={
            "for": [Span("<string>", 3)],
            "continue": [Span("<string>", 35)],
            "endfor": [Span("<string>", 23)],
        },
        tags={"for": [Span("<string>", 3)]},
        unexpected_tags={"continue": [Span("<string>", 35)]},
    ),
]

ENV = Environment(autoescape=True)


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_analyze_tags(case: Case) -> None:
    _assert_tags(ENV.analyze_tags_from_string(case.source), case)


def test_analyze_tags_with_loader() -> None:
    """Test the `Environment.analyze_tags` method."""
    case = Case(
        description="",
        source="{% for foo in bar %}{% if foo %}\n{% endif %}{% endfor %}",
        all_tags={
            "if": [Span("some.liquid", 23)],
            "for": [Span("some.liquid", 3)],
            "endif": [Span("some.liquid", 36)],
            "endfor": [Span("some.liquid", 47)],
        },
        tags={"if": [Span("some.liquid", 23)], "for": [Span("some.liquid", 3)]},
    )

    loader = DictLoader({"some.liquid": case.source})
    env = Environment(loader=loader)

    async def coro() -> TagAnalysis:
        return await env.analyze_tags_async("some.liquid")

    _assert_tags(env.analyze_tags("some.liquid"), case)
    _assert_tags(asyncio.run(coro()), case)


def test_analyze_tags_with_loader_context() -> None:
    """Test the `Environment.analyze_tags` method with context."""
    case = Case(
        description="",
        source="{% for foo in bar %}{% if foo %}\n{% endif %}{% endfor %}",
        all_tags={
            "if": [Span("some.liquid", 23)],
            "for": [Span("some.liquid", 3)],
            "endif": [Span("some.liquid", 36)],
            "endfor": [Span("some.liquid", 47)],
        },
        tags={"if": [Span("some.liquid", 23)], "for": [Span("some.liquid", 3)]},
    )

    loader = DictLoader({"some.liquid": case.source})
    env = Environment(loader=loader)
    template = env.get_template("some.liquid")
    context = RenderContext(template)

    async def coro() -> TagAnalysis:
        return await env.analyze_tags_async("some.liquid", context=context)

    _assert_tags(env.analyze_tags("some.liquid", context=context), case)
    _assert_tags(asyncio.run(coro()), case)


def test_analyze_tags_with_extra_tag() -> None:
    """Test analyze non-standard, extra tag."""
    case = Case(
        description="",
        source="{% with foo:bar %}{% endwith %}",
        all_tags={
            "with": [Span("<string>", 3)],
            "endwith": [Span("<string>", 21)],
        },
        tags={"with": [Span("<string>", 3)]},
    )

    env = Environment()
    env.add_tag(WithTag)
    _assert_tags(env.analyze_tags_from_string(case.source), case)
