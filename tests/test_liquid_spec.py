import asyncio
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
    "date_now_with_complex_format",
    "for_dynamic_range_empty_body_charges_each_item [error_mode=strict2]",
    "date_unix_timestamp_output_pattern",
    "date_now_year_pattern",
    "date_now_iso_format_pattern",
    "date_now_full_timestamp_pattern",
    "tablerow_literal_range_empty_body_charges_each_item [error_mode=strict2]",
    "range_score_is_cumulative_across_isolated_render_partials [error_mode=strict2]",
    "tablerow_capture_output_respects_assign_score_limit [error_mode=strict2]",
    "tablerow_break_final_markup_respects_render_length_limit [error_mode=strict2]",
    "for_nonempty_range_over_render_score_boundary [error_mode=strict2]",
    "cumulative_render_score_across_partials [error_mode=strict2]",
    "per_template_limit_still_works_with_cumulative [error_mode=strict2]",
    # String repr of data?
    "StandardFilterTest#test_base64_url_safe_encode_4aece6f5",
    "StandardFilterTest#test_base64_encode_3b4b7075",
    "StandardFilterTest#test_url_encode_60c8b46a",
    "Range bound lax int string parsing [error_mode=strict2]",
    # TODO:
    "Render for with args where arg is assigned",
    "ParsingQuirksTest#test_blank_variable_markup_8535e1f3",
    "Tablerow renders empty string when collection is false",
    "Truncatewords only splits by UTF-8 ASCII whitespaces",
    "Comparing empty and empty resolves to false",
    "CaptureTest#test_capture_to_variable_from_outer_scope_if_existing_aa077c00",
    "StandardFilterTest#test_date_e5c63040",
    "StandardFilterTest#test_date_7d8d7e0f",
    "StandardFilterTest#test_date_5a853799",
    "truncatewords_nil_input_skips_length_coercion",
    "truncate_nil_input_skips_length_coercion",
    "StandardTagTest#test_has_a_block_which_does_nothing_165f8c96",
    "CommentTagUnitTest#test_delimiter_can_have_extra_strings_a5bd2c12",
    "CommentTagUnitTest#test_delimiter_can_have_extra_strings_a6438a36",
    "CommentTagUnitTest#test_delimiter_can_have_extra_strings_b64b1fc0",
    "CommentTagUnitTest#test_delimiter_can_have_extra_strings_ebee30d2",
    "CommentTagUnitTest#test_delimiter_can_have_extra_strings_5414d4f8",
    "CommentTagUnitTest#test_open_tags_in_comment_62298e16",
    "tablerow_offset_non_numeric_string_coerces_to_zero",
    "tablerow_limit_non_numeric_string_coerces_to_zero",
    "tablerow_cols_non_numeric_string_never_wraps",
    "StandardFilterTest#test_h_90aa2f49",
    "StandardFilterTest#test_escape_once_0fadc690",
    "StandardFilterTest#test_escape_fa9d5e38",
    "Tablerow renders single column when lookup is a string and offset is greater than 1",
    "Tablerow renders single column when lookup is a string and limit is less than 1",
    "Float serialization with very long float",
    # These are covered in test_environment.py
    "strict2_rejects_bare_bracket_in_assign",
    "strict2_rejects_bare_bracket_in_case",
    "strict2_rejects_bare_bracket_in_if",
    "strict2_rejects_bare_bracket_in_for",
    "strict2_rejects_bare_bracket_dynamic_lookup",
    "strict2_rejects_bare_bracket_double_quoted",
    "strict2_rejects_bare_bracket_string_variable",
    # This fails on Windows.
    "date_negative_timestamp",
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


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("name"))
def test_liquid_spec_async(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    env = Environment(loader=MockLoader(case.templates), strict_filters=False)

    async def coro() -> str:
        return await env.parse(case.source).render_async(case.data)

    if case.expected is None:
        with pytest.raises(LiquidError):
            asyncio.run(coro())

    else:
        assert asyncio.run(coro()) == case.expected
