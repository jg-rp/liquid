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
    # TODO:
    "self_dotted_special_names_delegate_to_scope",
    "Range bound lax int string parsing [error_mode=strict2]",
    # TODO: maybe
    "self_inside_capture_body",
    "self_inside_for_loop_body",
    "self_contains_nil_valued_key",
    "self_contains_absent_key",
    "self_contains_present_key",
    "self_recursive_lookup",
    "self_bracket_in_bracket_recursion",
    "self_nested_property_access",
    "self_returns_empty_for_unknown_keys_strict2",
    "self_returns_empty_for_unknown_keys",
    "self_can_be_assigned",
    "self_sees_local_assigns",
    "self_dynamic_lookup_with_assigned_key",
    "self_dynamic_lookup_strict2",
    "self_dynamic_lookup",
    "self_bracket_access_strict2",
    "self_bracket_access_resolves_variable",
    "self_dynamic_lookup_strict2 [error_mode=strict2]",
    "self_bracket_access_strict2 [error_mode=strict2]",
    "url_encode_filter_stringifies_self_drop",
    "truncatewords_filter_stringifies_self_drop",
    "truncate_filter_stringifies_self_drop",
    "slice_filter_stringifies_self_drop",
    "escape_filter_stringifies_self_drop",
    "map_filter_looks_up_self_drop_properties",
    "last_filter_returns_empty_for_self_with_last_key",
    "first_filter_returns_empty_for_self_with_first_key",
    "self_size_filter_has_no_intrinsic_size",
    "self_can_be_passed_as_bare_drop_to_render",
    "self_with_strict_variables_returns_empty_for_undefined_var",
    "self_with_strict_variables_does_not_raise_for_defined_var",
    "self_reflects_variables_assigned_after_creation",
    "captured_self_tracks_each_scope_across_nested_render_boundaries",
    "captured_self_distinguishes_original_and_snippet_scope_at_boundary",
    "self_passed_to_nested_renders_preserves_each_level",
    "self_passed_as_self_render_param_preserves_original_scope",
    "self_passed_as_render_param_preserves_original_scope",
    "self_in_render_without_passing_resolves_inner_scope",
    "distinct_self_assignments_compare_equal",
    "bare_self_compares_equal_to_bare_self",
    "assigned_self_compares_equal_to_itself",
    "self_with_strict_variables_does_not_raise_for_defined_var [error_mode=strict2]",
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


# TODO: async
