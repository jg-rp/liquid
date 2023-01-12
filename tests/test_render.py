"""Liquid render tests."""
# pylint: disable=missing-function-docstring,too-many-public-methods,missing-class-docstring
import asyncio
import unittest

from typing import List

from liquid.environment import Environment
from liquid.future import Environment as FutureEnvironment
from liquid.template import AwareBoundTemplate
from liquid.template import BoundTemplate
from liquid.template import FutureAwareBoundTemplate
from liquid.mode import Mode
from liquid.loaders import DictLoader

from liquid import golden
from liquid.exceptions import Error
from liquid.golden.case import Case


class RenderTestCase(unittest.TestCase):
    def _test(
        self,
        test_cases: List[Case],
        template_class=AwareBoundTemplate,
        future_template_class=FutureAwareBoundTemplate,
        tolerance=Mode.STRICT,
    ):
        """Run all tests in `test_cases` through sync and async paths."""
        self._test_sync(
            test_cases,
            template_class=template_class,
            future_template_class=future_template_class,
            tolerance=tolerance,
        )
        self._test_async(
            test_cases,
            template_class=template_class,
            future_template_class=future_template_class,
            tolerance=tolerance,
        )

    def _test_sync(
        self,
        test_cases: List[Case],
        *,
        template_class=AwareBoundTemplate,
        future_template_class=FutureAwareBoundTemplate,
        tolerance=Mode.STRICT,
    ):
        """Helper method for testing lists of test cases."""

        def sub_test(env: Environment, case: Case, future=False) -> None:
            with self.subTest(msg=case.description, future=future, mode=tolerance):
                if case.error:
                    with self.assertRaises(Error):
                        template = env.from_string(case.template, globals=case.globals)
                        template.render()
                else:
                    template = env.from_string(case.template, globals=case.globals)
                    result = template.render()
                    self.assertEqual(result, case.expect)

        for case in test_cases:
            loader = DictLoader(case.partials)

            env = Environment(loader=loader, tolerance=tolerance)
            env.template_class = template_class

            future_env = FutureEnvironment(loader=loader, tolerance=tolerance)
            future_env.template_class = future_template_class

            if case.future:
                sub_test(env=future_env, case=case, future=True)
            else:
                sub_test(env=env, case=case, future=False)
                sub_test(env=future_env, case=case, future=True)

    def _test_async(
        self,
        test_cases: List[Case],
        template_class=AwareBoundTemplate,
        future_template_class=FutureAwareBoundTemplate,
        tolerance=Mode.STRICT,
    ):
        """Helper method for table driven testing of asynchronous rendering."""

        async def coro(template: BoundTemplate):
            return await template.render_async()

        def sub_test(env: Environment, case: Case, future=False) -> None:
            with self.subTest(
                msg=case.description, asynchronous=True, future=future, mode=tolerance
            ):
                if case.error:
                    with self.assertRaises(Error):
                        template = env.from_string(case.template, globals=case.globals)
                        asyncio.run(coro(template))
                else:
                    template = env.from_string(case.template, globals=case.globals)
                    result = asyncio.run(coro(template))
                    self.assertEqual(result, case.expect)

        for case in test_cases:
            loader = DictLoader(case.partials)

            env = Environment(loader=loader, tolerance=tolerance)
            env.template_class = template_class

            future_env = FutureEnvironment(loader=loader, tolerance=tolerance)
            future_env.template_class = future_template_class

            if case.future:
                sub_test(env=future_env, case=case, future=True)
            else:
                sub_test(env=env, case=case, future=False)
                sub_test(env=future_env, case=case, future=True)


class RenderTagsTestCase(RenderTestCase):
    def test_literal(self):
        """Test that we can render template literals."""
        self._test(golden.not_liquid.cases)

    def test_whitespace_control(self):
        """Test that we can control whitespace."""
        self._test(golden.whitespace_control.cases)

    def test_output_statement(self):
        """Test that we can render output statements."""
        self._test(golden.output_statement.cases)

    def test_echo_tag(self):
        """Test that we can render `echo` tags."""
        self._test(golden.echo_tag.cases)

    def test_assign_tag(self):
        """Test that we can render assigned variables."""
        self._test(golden.assign_tag.cases)

    def test_if_tag(self):
        """Test that we can render `if` tags."""
        self._test(golden.if_tag.cases)

    def test_comment_tag(self):
        """Test that we can render comment tags."""
        self._test(golden.comment_tag.cases)

    def test_unless_tag(self):
        """Test that we can render `unless` tags."""
        self._test(golden.unless_tag.cases)

    def test_capture_tag(self):
        """Test that we can render `capture` tags."""
        self._test(golden.capture_tag.cases)

    def test_case_tag(self):
        """Test that we can render `case` tags."""
        self._test(golden.case_tag.cases)

    def test_cycle_tag(self):
        """Test that we can render `cycle` tags."""
        self._test(golden.cycle_tag.cases)

    def test_decrement_tag(self):
        """Test that we can render `decrement` tags."""
        self._test(golden.decrement_tag.cases)

    def test_increment_tag(self):
        """Test that we can render `increment` tags."""
        self._test(golden.increment_tag.cases)

    def test_for_tag(self):
        """Test that we can render `for` tags."""
        self._test(golden.for_tag.cases)

    def test_raw_tag(self):
        """Test that we can render `raw` tags."""
        self._test(golden.raw_tag.cases)

    def test_tablerow_tag(self):
        """Test that we can render `tablerow` tags."""
        self._test(golden.tablerow_tag.cases)

    def test_liquid_tag(self):
        """Test that we can render `liquid` tags."""
        self._test(golden.liquid_tag.cases)

    def test_illegal(self):
        """Test that we can render an `illegal` token in LAX mode."""
        self._test(golden.illegal.cases)

    def test_include_tag(self):
        """Test that we can render `include` tags."""
        self._test(golden.include_tag.cases)

    def test_render_tag(self):
        """Test that we can render `render` tags."""
        self._test(golden.render_tag.cases)

    def test_ifchanged_tag(self):
        """Test that we can render `ifchanged` tags."""
        self._test(golden.ifchanged_tag.cases)

    def test_inline_comment_tag(self):
        """Test that we can render `#` tags."""
        self._test(golden.inline_comment_tag.cases)


class RenderFiltersTestCase(RenderTestCase):
    def test_render_concat_filter(self):
        """Test that we render the `concat` filter correctly."""
        self._test(golden.concat_filter.cases)

    def test_render_first_filter(self):
        """Test that we render the `first` filter correctly."""
        self._test(golden.first_filter.cases)

    def test_render_join_filter(self):
        """Test that we render the `join` filter correctly."""
        self._test(golden.join_filter.cases)

    def test_render_last_filter(self):
        """Test that we render the `last` filter correctly."""
        self._test(golden.last_filter.cases)

    def test_render_map_filter(self):
        """Test that we render the `map` filter correctly."""
        self._test(golden.map_filter.cases)

    def test_render_reverse_filter(self):
        """Test that we render the `reverse` filter correctly."""
        self._test(golden.reverse_filter.cases)

    def test_render_sort_filter(self):
        """Test that we render the `sort` filter correctly."""
        self._test(golden.sort_filter.cases)

    def test_render_sort_natural_filter(self):
        """Test that we render the `sort_natural` filter correctly."""
        self._test(golden.sort_natural_filter.cases)

    def test_render_where_filter(self):
        """Test that we render the `where` filter correctly."""
        self._test(golden.where_filter.cases)

    def test_render_uniq_filter(self):
        """Test that we render the `uniq` filter correctly."""
        self._test(golden.uniq_filter.cases)

    def test_render_compact_filter(self):
        """Test that we render the `compact` filter correctly."""
        self._test(golden.compact_filter.cases)

    def test_render_abs_filter(self):
        """Test that we render the `abs` filter correctly."""
        self._test(golden.abs_filter.cases)

    def test_render_at_most_filter(self):
        """Test that we render the `at_most` filter correctly."""
        self._test(golden.at_most_filter.cases)

    def test_render_at_least_filter(self):
        """Test that we render the `at_least` filter correctly."""
        self._test(golden.at_least_filter.cases)

    def test_render_ceil_filter(self):
        """Test that we render the `ceil` filter correctly."""
        self._test(golden.ceil_filter.cases)

    def test_render_floor_filter(self):
        """Test that we render the `floor` filter correctly."""
        self._test(golden.floor_filter.cases)

    def test_render_divided_by_filter(self):
        """Test that we render the `divided_by` filter correctly."""
        self._test(golden.divided_by_filter.cases)

    def test_render_minus_filter(self):
        """Test that we render the `minus` filter correctly."""
        self._test(golden.minus_filter.cases)

    def test_render_plus_filter(self):
        """Test that we render the `plus` filter correctly."""
        self._test(golden.plus_filter.cases)

    def test_render_round_filter(self):
        """Test that we render the `round` filter correctly."""
        self._test(golden.round_filter.cases)

    def test_render_times_filter(self):
        """Test that we render the `times` filter correctly."""
        self._test(golden.times_filter.cases)

    def test_render_modulo_filter(self):
        """Test that we render the `modulo` filter correctly."""
        self._test(golden.modulo_filter.cases)

    def test_render_size_filter(self):
        """Test that we render the `size` filter correctly."""
        self._test(golden.size_filter.cases)

    def test_render_default_filter(self):
        """Test that we render the `default` filter correctly."""
        self._test(golden.default_filter.cases)

    def test_render_date_filter(self):
        """Test that we render the `date` filter correctly."""
        self._test(golden.date_filter.cases)

    def test_render_capitalize_filter(self):
        """Test that we can render the `capitalize` filter correctly."""
        self._test(golden.capitalize_filter.cases)

    def test_render_append_filter(self):
        """Test that we can render the `append` filter correctly."""
        self._test(golden.append_filter.cases)

    def test_render_downcase_filter(self):
        """Test that we can render the `downcase` filter correctly."""
        self._test(golden.downcase_filter.cases)

    def test_render_escape_filter(self):
        """Test that we can render the `escape` filter correctly."""
        self._test(golden.escape_filter.cases)

    def test_render_escape_once_filter(self):
        """Test that we can render the `escape_once` filter correctly."""
        self._test(golden.escape_once_filter.cases)

    def test_render_lstrip_filter(self):
        """Test that we can render the `lstrip` filter correctly."""
        self._test(golden.lstrip_filter.cases)

    def test_render_newline_to_br_filter(self):
        """Test that we can render the `newline_to_br` filter correctly."""
        self._test(golden.newline_to_br_filter.cases)

    def test_render_prepend_filter(self):
        """Test that we can render the `prepend` filter correctly."""
        self._test(golden.prepend_filter.cases)

    def test_render_remove_filter(self):
        """Test that we can render the `remove` filter correctly."""
        self._test(golden.remove_filter.cases)

    def test_render_remove_first_filter(self):
        """Test that we can render the `remove_first` filter correctly."""
        self._test(golden.remove_first_filter.cases)

    def test_render_remove_last_filter(self):
        """Test that we can render the `remove_last` filter correctly."""
        self._test(golden.remove_last_filter.cases)

    def test_render_replace_filter(self):
        """Test that we can render the `replace` filter correctly."""
        self._test(golden.replace_filter.cases)

    def test_render_replace_first_filter(self):
        """Test that we can render the `replace_first` filter correctly."""
        self._test(golden.replace_first_filter.cases)

    def test_render_replace_last_filter(self):
        """Test that we can render the `replace_last` filter correctly."""
        self._test(golden.replace_last_filter.cases)

    def test_render_slice_filter(self):
        """Test that we can render the `slice` filter correctly."""
        self._test(golden.slice_filter.cases)

    def test_render_split_filter(self):
        """Test that we can render the `split` filter correctly."""
        self._test(golden.split_filter.cases)

    def test_render_upcase_filter(self):
        """Test that we can render the `upcase` filter correctly."""
        self._test(golden.upcase_filter.cases)

    def test_render_strip_filter(self):
        """Test that we can render the `strip` filter correctly."""
        self._test(golden.strip_filter.cases)

    def test_render_rstrip_filter(self):
        """Test that we can render the `rstrip` filter correctly."""
        self._test(golden.rstrip_filter.cases)

    def test_render_strip_html_filter(self):
        """Test that we can render the `strip_html` filter correctly."""
        self._test(golden.strip_html_filter.cases)

    def test_render_strip_newlines_filter(self):
        """Test that we can render the `strip_newlines` filter correctly."""
        self._test(golden.strip_newlines_filter.cases)

    def test_render_truncate_filter(self):
        """Test that we can render the `truncate` filter correctly."""
        self._test(golden.truncate_filter.cases)

    def test_render_truncatewords_filter(self):
        """Test that we can render the `truncatewords` filter correctly."""
        self._test(golden.truncatewords_filter.cases)

    def test_render_url_encode_filter(self):
        """Test that we can render the `url_encode` filter correctly."""
        self._test(golden.url_encode_filter.cases)

    def test_render_url_decode_filter(self):
        """Test that we can render the `url_decode` filter correctly."""
        self._test(golden.url_decode_filter.cases)

    def test_render_base64_encode_filter(self):
        """Test that we can render the `base64_encode` filter correctly."""
        self._test(golden.base64_encode_filter.cases)

    def test_render_base64_decode_filter(self):
        """Test that we can render the `base64_decode` filter correctly."""
        self._test(golden.base64_decode_filter.cases)

    def test_render_base64_url_safe_encode_filter(self):
        """Test that we can render the `base64_url_safe_encode` filter correctly."""
        self._test(golden.base64_url_safe_encode_filter.cases)

    def test_render_base64_url_safe_decode_filter(self):
        """Test that we can render the `base64_url_safe_decode` filter correctly."""
        self._test(golden.base64_url_safe_decode_filter.cases)


class RenderMiscTestCase(RenderTestCase):
    def test_render_range_objects(self):
        """Test that we can render range objects."""
        self._test(golden.range_objects.cases)

    def test_special_properties(self):
        """Test that we can use special, built-in properties."""
        self._test(golden.special.cases)

    def test_identifiers(self):
        """Test permitted identifiers."""
        self._test(golden.identifiers.cases)
