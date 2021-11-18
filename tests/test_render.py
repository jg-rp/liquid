"""Liquid render tests."""

import asyncio
import unittest

from typing import List

from liquid.environment import Environment
from liquid.template import AwareBoundTemplate
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
        tolerance=Mode.STRICT,
    ):
        """Run all tests in `test_cases` in sync and async modes."""
        self._test_sync(test_cases, template_class, tolerance)
        self._test_async(test_cases, template_class, tolerance)

    def _test_sync(
        self,
        test_cases: List[Case],
        template_class=AwareBoundTemplate,
        tolerance=Mode.STRICT,
    ):
        """Helper method for testing lists of test cases."""
        for case in test_cases:
            env = Environment(
                loader=DictLoader(case.partials),
                tolerance=tolerance,
            )
            env.template_class = template_class

            with self.subTest(msg=case.description, mode=tolerance):
                if case.error:
                    with self.assertRaises(Error):
                        template = env.from_string(case.template, globals=case.globals)
                        result = template.render()
                else:
                    template = env.from_string(case.template, globals=case.globals)
                    result = template.render()
                    self.assertEqual(result, case.expect)

    def _test_async(
        self,
        test_cases: List[Case],
        template_class=AwareBoundTemplate,
        tolerance=Mode.STRICT,
    ):
        """Helper method for table driven testing of asynchronous rendering."""

        async def coro(template):
            return await template.render_async()

        for case in test_cases:
            env = Environment(
                loader=DictLoader(case.partials),
                tolerance=tolerance,
            )
            env.template_class = template_class

            with self.subTest(msg=case.description, asynchronous=True, mode=tolerance):
                if case.error:
                    with self.assertRaises(Error):
                        template = env.from_string(case.template, globals=case.globals)
                        result = asyncio.run(coro(template))
                else:
                    template = env.from_string(case.template, globals=case.globals)
                    result = asyncio.run(coro(template))
                    self.assertEqual(result, case.expect)


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
        self._test(golden.illegal_tag.cases)

    def test_include_tag(self):
        """Test that we can render `include` tags."""
        self._test(golden.include_tag.cases)

    def test_render_tag(self):
        """Test that we can render `render` tags."""
        self._test(golden.render_tag.cases)

    def test_ifchanged_tag(self):
        """Test that we can render `ifchanged` tags."""
        self._test(golden.ifchanged_tag.cases)


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
