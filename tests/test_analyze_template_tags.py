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


# TODO: replace line numbers with indexes

TEST_CASES: list[Case] = [
    Case(description="no tags", source="hello"),
    Case(
        description="inline tag",
        source="{% assign foo = 'bar' %}",
        all_tags={"assign": [Span("<string>", 0)]},
        tags={"assign": [Span("<string>", 0)]},
    ),
    Case(
        description="one block tag",
        source="{% if foo %}{% endif %}",
        all_tags={
            "if": [Span("<string>", 0)],
            "endif": [Span("<string>", 12)],
        },
        tags={"if": [Span("<string>", 0)]},
    ),
    Case(
        description="two block tags",
        source="{% if foo %}{% endif %}\n{% if bar %}{% endif %}",
        all_tags={
            "if": [Span("<string>", 0), Span("<string>", 24)],
            "endif": [Span("<string>", 12), Span("<string>", 36)],
        },
        tags={"if": [Span("<string>", 0), Span("<string>", 24)]},
    ),
    Case(
        description="unknown block tag",
        source="{% form foo %}{% endform %}",
        all_tags={
            "form": [Span("<string>", 0)],
            "endform": [Span("<string>", 14)],
        },
        tags={"form": [Span("<string>", 0)]},
        unknown_tags={"form": [Span("<string>", 0)]},
    ),
    Case(
        description="unbalanced block tag",
        source="{% if foo %}{% if bar %}{% endif %}\n{% if baz %}{% endif %}",
        all_tags={
            "if": [Span("<string>", 0), Span("<string>", 12), Span("<string>", 36)],
            "endif": [Span("<string>", 24), Span("<string>", 48)],
        },
        tags={"if": [Span("<string>", 0), Span("<string>", 12), Span("<string>", 36)]},
        unclosed_tags={"if": [Span("<string>", 0)]},
    ),
    Case(
        description="unbalanced block tag without inferred end tag",
        source=(
            "{% for foo in bar %}\n{% if foo %}\n    {{ foo | upcase }}\n{% endif %}"
        ),
        all_tags={
            "for": [Span("<string>", 0)],
            "if": [Span("<string>", 21)],
            "endif": [Span("<string>", 57)],
        },
        tags={"if": [Span("<string>", 21)], "for": [Span("<string>", 0)]},
        unclosed_tags={"for": [Span("<string>", 0)]},
    ),
    Case(
        description="end block typo",
        source="{% if foo %}{% if bar %}{% endif %}\n{% endi %}",
        all_tags={
            "if": [Span("<string>", 0), Span("<string>", 12)],
            "endif": [Span("<string>", 24)],
            "endi": [Span("<string>", 36)],
        },
        tags={"if": [Span("<string>", 0), Span("<string>", 12)]},
        unclosed_tags={"if": [Span("<string>", 0)]},
        unknown_tags={"endi": [Span("<string>", 36)]},
    ),
    Case(
        description="end block with wrong name",
        source="{% if foo %}{% if bar %}{% endif %}\n{% endfor %}",
        all_tags={
            "if": [Span("<string>", 0), Span("<string>", 12)],
            "endif": [Span("<string>", 24)],
            "endfor": [Span("<string>", 36)],
        },
        tags={"if": [Span("<string>", 0), Span("<string>", 12)]},
        unclosed_tags={"if": [Span("<string>", 0)]},
    ),
    Case(
        description="unexpected closing of inline tag",
        source="{% increment foo %}{% endincrement %}",
        all_tags={
            "increment": [Span("<string>", 0)],
            "endincrement": [Span("<string>", 19)],
        },
        tags={"increment": [Span("<string>", 0)]},
        unknown_tags={"endincrement": [Span("<string>", 19)]},
    ),
    Case(
        description="inner tag",
        source="{% if foo %}{% else %}{% endif %}",
        all_tags={
            "if": [Span("<string>", 0)],
            "else": [Span("<string>", 12)],
            "endif": [Span("<string>", 22)],
        },
        tags={"if": [Span("<string>", 0)]},
    ),
    Case(
        description="inner break tag",
        source="{% for foo in bar %}{% break %}{% endfor %}",
        all_tags={
            "for": [Span("<string>", 0)],
            "break": [Span("<string>", 20)],
            "endfor": [Span("<string>", 31)],
        },
        tags={"for": [Span("<string>", 0)]},
    ),
    Case(
        description="inner continue tag",
        source="{% for foo in bar %}{% continue %}{% endfor %}",
        all_tags={
            "for": [Span("<string>", 0)],
            "continue": [Span("<string>", 20)],
            "endfor": [Span("<string>", 34)],
        },
        tags={"for": [Span("<string>", 0)]},
    ),
    Case(
        description="orphaned inner tag",
        source="{% if foo %}{% endif %}{% else %}",
        all_tags={
            "if": [Span("<string>", 0)],
            "else": [Span("<string>", 23)],
            "endif": [Span("<string>", 12)],
        },
        tags={"if": [Span("<string>", 0)]},
        unexpected_tags={"else": [Span("<string>", 23)]},
    ),
    Case(
        description="orphaned break tag",
        source="{% for foo in bar %}{% endfor %}{% break %}",
        all_tags={
            "for": [Span("<string>", 0)],
            "break": [Span("<string>", 32)],
            "endfor": [Span("<string>", 20)],
        },
        tags={"for": [Span("<string>", 0)]},
        unexpected_tags={"break": [Span("<string>", 32)]},
    ),
    Case(
        description="orphaned continue tag",
        source="{% for foo in bar %}{% endfor %}{% continue %}",
        all_tags={
            "for": [Span("<string>", 0)],
            "continue": [Span("<string>", 32)],
            "endfor": [Span("<string>", 20)],
        },
        tags={"for": [Span("<string>", 0)]},
        unexpected_tags={"continue": [Span("<string>", 32)]},
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
            "if": [Span("some.liquid", 20)],
            "for": [Span("some.liquid", 0)],
            "endif": [Span("some.liquid", 33)],
            "endfor": [Span("some.liquid", 44)],
        },
        tags={"if": [Span("some.liquid", 20)], "for": [Span("some.liquid", 0)]},
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
            "if": [Span("some.liquid", 20)],
            "for": [Span("some.liquid", 0)],
            "endif": [Span("some.liquid", 33)],
            "endfor": [Span("some.liquid", 44)],
        },
        tags={"if": [Span("some.liquid", 20)], "for": [Span("some.liquid", 0)]},
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
            "with": [Span("<string>", 0)],
            "endwith": [Span("<string>", 18)],
        },
        tags={"with": [Span("<string>", 0)]},
    )

    env = Environment()
    env.add_tag(WithTag)
    _assert_tags(env.analyze_tags_from_string(case.source), case)
