"""Test cases for analyzing a template's tags using `Environment.analyze_tags`."""
import asyncio
from dataclasses import dataclass
from dataclasses import field
from typing import List
from unittest import TestCase

from liquid import Environment
from liquid import DictLoader
from liquid.analyze_tags import TagAnalysis
from liquid.analyze_tags import TagMap
from liquid.context import Context
from liquid.extra.tags import WithTag


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


class AnalyzeTagsTestCase(TestCase):
    """Test cases for analyzing a template's tags using `Environment.analyze_tags`."""

    def setUp(self) -> None:
        self.standard_env = Environment()

    def _test(self, env: Environment, test_cases: List[Case]) -> None:
        """Test helper function."""
        for case in test_cases:
            with self.subTest(msg=case.description):
                tag_analysis = env.analyze_tags_from_string(case.source)
                self.assertEqual(tag_analysis.all_tags, case.all_tags)
                self.assertEqual(tag_analysis.tags, case.tags)
                self.assertEqual(tag_analysis.unclosed_tags, case.unclosed_tags)
                self.assertEqual(tag_analysis.unexpected_tags, case.unexpected_tags)
                self.assertEqual(tag_analysis.unknown_tags, case.unknown_tags)

    def test_analyze_tags(self) -> None:
        """Test that we can analyze a template's tags."""
        test_cases = [
            Case(description="no tags", source="hello"),
            Case(
                description="inline tag",
                source="{% assign foo = 'bar' %}",
                all_tags={"assign": [("<string>", 1)]},
                tags={"assign": [("<string>", 1)]},
            ),
            Case(
                description="one block tag",
                source="{% if foo %}{% endif %}",
                all_tags={
                    "if": [("<string>", 1)],
                    "endif": [("<string>", 1)],
                },
                tags={"if": [("<string>", 1)]},
            ),
            Case(
                description="two block tags",
                source="{% if foo %}{% endif %}\n{% if bar %}{% endif %}",
                all_tags={
                    "if": [("<string>", 1), ("<string>", 2)],
                    "endif": [("<string>", 1), ("<string>", 2)],
                },
                tags={"if": [("<string>", 1), ("<string>", 2)]},
            ),
            Case(
                description="unknown block tag",
                source="{% form foo %}{% endform %}",
                all_tags={
                    "form": [("<string>", 1)],
                    "endform": [("<string>", 1)],
                },
                tags={"form": [("<string>", 1)]},
                unknown_tags={"form": [("<string>", 1)]},
            ),
            Case(
                description="unbalanced block tag",
                source="{% if foo %}{% if bar %}{% endif %}\n{% if baz %}{% endif %}",
                all_tags={
                    "if": [("<string>", 1), ("<string>", 1), ("<string>", 2)],
                    "endif": [("<string>", 1), ("<string>", 2)],
                },
                tags={"if": [("<string>", 1), ("<string>", 1), ("<string>", 2)]},
                unclosed_tags={"if": [("<string>", 1)]},
            ),
            Case(
                description="unbalanced block tag without inferred end tag",
                source=(
                    "{% for foo in bar %}\n"
                    "{% if foo %}\n"
                    "    {{ foo | upcase }}\n"
                    "{% endif %}"
                ),
                all_tags={
                    "for": [("<string>", 1)],
                    "if": [("<string>", 2)],
                    "endif": [("<string>", 4)],
                },
                tags={"if": [("<string>", 2)], "for": [("<string>", 1)]},
                unclosed_tags={"for": [("<string>", 1)]},
            ),
            Case(
                description="end block typo",
                source="{% if foo %}{% if bar %}{% endif %}\n{% endi %}",
                all_tags={
                    "if": [("<string>", 1), ("<string>", 1)],
                    "endif": [("<string>", 1)],
                    "endi": [("<string>", 2)],
                },
                tags={"if": [("<string>", 1), ("<string>", 1)]},
                unclosed_tags={"if": [("<string>", 1)]},
                unknown_tags={"endi": [("<string>", 2)]},
            ),
            Case(
                description="end block with wrong name",
                source="{% if foo %}{% if bar %}{% endif %}\n{% endfor %}",
                all_tags={
                    "if": [("<string>", 1), ("<string>", 1)],
                    "endif": [("<string>", 1)],
                    "endfor": [("<string>", 2)],
                },
                tags={"if": [("<string>", 1), ("<string>", 1)]},
                unclosed_tags={"if": [("<string>", 1)]},
            ),
            Case(
                description="unexpected closing of inline tag",
                source="{% increment foo %}{% endincrement %}",
                all_tags={
                    "increment": [("<string>", 1)],
                    "endincrement": [("<string>", 1)],
                },
                tags={"increment": [("<string>", 1)]},
                unknown_tags={"endincrement": [("<string>", 1)]},
            ),
            Case(
                description="inner tag",
                source="{% if foo %}{% else %}{% endif %}",
                all_tags={
                    "if": [("<string>", 1)],
                    "else": [("<string>", 1)],
                    "endif": [("<string>", 1)],
                },
                tags={"if": [("<string>", 1)]},
            ),
            Case(
                description="inner break tag",
                source="{% for foo in bar %}{% break %}{% endfor %}",
                all_tags={
                    "for": [("<string>", 1)],
                    "break": [("<string>", 1)],
                    "endfor": [("<string>", 1)],
                },
                tags={"for": [("<string>", 1)]},
            ),
            Case(
                description="inner continue tag",
                source="{% for foo in bar %}{% continue %}{% endfor %}",
                all_tags={
                    "for": [("<string>", 1)],
                    "continue": [("<string>", 1)],
                    "endfor": [("<string>", 1)],
                },
                tags={"for": [("<string>", 1)]},
            ),
            Case(
                description="orphaned inner tag",
                source="{% if foo %}{% endif %}{% else %}",
                all_tags={
                    "if": [("<string>", 1)],
                    "else": [("<string>", 1)],
                    "endif": [("<string>", 1)],
                },
                tags={"if": [("<string>", 1)]},
                unexpected_tags={"else": [("<string>", 1)]},
            ),
            Case(
                description="orphaned break tag",
                source="{% for foo in bar %}{% endfor %}{% break %}",
                all_tags={
                    "for": [("<string>", 1)],
                    "break": [("<string>", 1)],
                    "endfor": [("<string>", 1)],
                },
                tags={"for": [("<string>", 1)]},
                unexpected_tags={"break": [("<string>", 1)]},
            ),
            Case(
                description="orphaned continue tag",
                source="{% for foo in bar %}{% endfor %}{% continue %}",
                all_tags={
                    "for": [("<string>", 1)],
                    "continue": [("<string>", 1)],
                    "endfor": [("<string>", 1)],
                },
                tags={"for": [("<string>", 1)]},
                unexpected_tags={"continue": [("<string>", 1)]},
            ),
        ]

        self._test(self.standard_env, test_cases)

    def test_analyze_tags_with_loader(self) -> None:
        """Test the `Environment.analyze_tags` method."""
        case = Case(
            description="",
            source="{% for foo in bar %}{% if foo %}\n{% endif %}{% endfor %}",
            all_tags={
                "if": [("some.liquid", 1)],
                "for": [("some.liquid", 1)],
                "endif": [("some.liquid", 2)],
                "endfor": [("some.liquid", 2)],
            },
            tags={"if": [("some.liquid", 1)], "for": [("some.liquid", 1)]},
        )

        loader = DictLoader({"some.liquid": case.source})
        env = Environment(loader=loader)

        async def coro():
            return await env.analyze_tags_async("some.liquid")

        def assert_tags(tag_analysis: TagAnalysis) -> None:
            self.assertEqual(tag_analysis.all_tags, case.all_tags)
            self.assertEqual(tag_analysis.tags, case.tags)
            self.assertEqual(tag_analysis.unclosed_tags, case.unclosed_tags)
            self.assertEqual(tag_analysis.unexpected_tags, case.unexpected_tags)
            self.assertEqual(tag_analysis.unknown_tags, case.unknown_tags)

        assert_tags(env.analyze_tags("some.liquid"))

        with self.subTest(msg="async"):
            assert_tags(asyncio.run(coro()))

    def test_analyze_tags_with_loader_context(self) -> None:
        """Test the `Environment.analyze_tags` method with context."""
        case = Case(
            description="",
            source="{% for foo in bar %}{% if foo %}\n{% endif %}{% endfor %}",
            all_tags={
                "if": [("some.liquid", 1)],
                "for": [("some.liquid", 1)],
                "endif": [("some.liquid", 2)],
                "endfor": [("some.liquid", 2)],
            },
            tags={"if": [("some.liquid", 1)], "for": [("some.liquid", 1)]},
        )

        loader = DictLoader({"some.liquid": case.source})
        env = Environment(loader=loader)
        context = Context(env)

        async def coro():
            return await env.analyze_tags_async("some.liquid", context=context)

        def assert_tags(tag_analysis: TagAnalysis) -> None:
            self.assertEqual(tag_analysis.all_tags, case.all_tags)
            self.assertEqual(tag_analysis.tags, case.tags)
            self.assertEqual(tag_analysis.unclosed_tags, case.unclosed_tags)
            self.assertEqual(tag_analysis.unexpected_tags, case.unexpected_tags)
            self.assertEqual(tag_analysis.unknown_tags, case.unknown_tags)

        assert_tags(env.analyze_tags("some.liquid", context=context))

        with self.subTest(msg="async"):
            assert_tags(asyncio.run(coro()))

    def test_analyze_tags_with_extra_tag(self) -> None:
        """Test analyze non-standard, extra tag."""
        case = Case(
            description="",
            source="{% with foo:bar %}{% endwith %}",
            all_tags={
                "with": [("<string>", 1)],
                "endwith": [("<string>", 1)],
            },
            tags={"with": [("<string>", 1)]},
        )

        env = Environment()
        env.add_tag(WithTag)

        tag_analysis = env.analyze_tags_from_string(case.source)
        self.assertEqual(tag_analysis.all_tags, case.all_tags)
        self.assertEqual(tag_analysis.tags, case.tags)
        self.assertEqual(tag_analysis.unclosed_tags, case.unclosed_tags)
        self.assertEqual(tag_analysis.unexpected_tags, case.unexpected_tags)
        self.assertEqual(tag_analysis.unknown_tags, case.unknown_tags)
