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
