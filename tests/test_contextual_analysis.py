"""Test cases for analyzing a template given some render context data."""

import asyncio
import unittest

from typing import Dict, Optional

from liquid import Context
from liquid import DictLoader
from liquid import Environment
from liquid import Template

from liquid.filter import with_context
from liquid.template import BoundTemplate


class ContextualAnalysisTestCase(unittest.TestCase):
    """Contextual template analysis test cases."""

    def _test(
        self,
        template: BoundTemplate,
        data: Dict[str, object],
        variables: Dict[str, int],
        assigns: Dict[str, int],
        undefined: Dict[str, int],
        filters: Optional[Dict[str, int]] = None,
    ) -> None:
        refs = template.analyze_with_context(**data)
        self.assertEqual(refs.all_variables, variables)
        self.assertEqual(refs.local_variables, assigns)
        self.assertEqual(refs.undefined_variables, undefined)
        if filters is not None:
            self.assertEqual(refs.filters, filters)
        else:
            self.assertEqual(refs.filters, {})

        async def coro():
            return await template.analyze_with_context_async(**data)

        refs = asyncio.run(coro())
        self.assertEqual(refs.all_variables, variables)
        self.assertEqual(refs.local_variables, assigns)
        self.assertEqual(refs.undefined_variables, undefined)
        if filters is not None:
            self.assertEqual(refs.filters, filters)
        else:
            self.assertEqual(refs.filters, {})

    def test_analyze_output(self):
        """Test that we count references to variables in output statements."""
        template = Template("{{ x | default: y, allow_false: z }}")
        data = {"y": 1, "z": 2}
        expect_variables = {"x": 1, "y": 1, "z": 1}
        expect_locals = {}
        expect_undefined = {"x": 1}
        expect_filters = {"default": 1}

        self._test(
            template,
            data,
            expect_variables,
            expect_locals,
            expect_undefined,
            filters=expect_filters,
        )

    def test_analyze_output_with_bracketed_properties(self):
        """Test that we handle bracketed property access with dots."""
        template = Template("{{ some['foo.bar'].other }}")
        data = {}
        expect_variables = {'some["foo.bar"].other': 1}
        expect_locals = {}
        expect_undefined = {'some["foo.bar"].other': 1}

        self._test(template, data, expect_variables, expect_locals, expect_undefined)

    def test_visit_branches(self):
        """Test that we only count references to variables in visited branches."""
        template = Template(
            "{% if false %}{{ x | default: y, allow_false: z }}{% endif %}"
        )
        data = {"y": 1, "z": 2}
        expect_variables = {}
        expect_locals = {}
        expect_undefined = {}
        expect_filters = {}

        self._test(
            template,
            data,
            expect_variables,
            expect_locals,
            expect_undefined,
            filters=expect_filters,
        )

    def test_analyze_assign(self):
        """Test that we count references to variables in assignment tags."""
        template = Template("{% assign x = a %}{{ x | default: y, allow_false: z }}")
        data = {"a": 1, "y": 1, "z": 2}
        expect_variables = {"x": 1, "y": 1, "z": 1, "a": 1}
        expect_locals = {"x": 1}
        expect_undefined = {}
        expect_filters = {"default": 1}

        self._test(
            template,
            data,
            expect_variables,
            expect_locals,
            expect_undefined,
            filters=expect_filters,
        )

    def test_count_number_of_references(self):
        """Test that we count multiple references to the same variable name."""
        template = Template("{{ x | default: y, allow_false: z }}{{ x | append: x }}")
        data = {"y": 1, "z": 2}
        expect_variables = {"x": 3, "y": 1, "z": 1}
        expect_locals = {}
        expect_undefined = {"x": 3}
        expect_filters = {"default": 1, "append": 1}

        self._test(
            template,
            data,
            expect_variables,
            expect_locals,
            expect_undefined,
            filters=expect_filters,
        )

    def test_analyze_included_template(self):
        """Test that we count references to variables in included templates."""
        loader = DictLoader({"foo": "{{ x | append: y }}"})
        env = Environment(loader=loader)

        template = env.from_string("{{ x }}{% include 'foo' %}")
        data = {"y": 1, "z": 2}
        expect_variables = {"x": 2, "y": 1}
        expect_locals = {}
        expect_undefined = {"x": 2}
        expect_filters = {"append": 1}

        self._test(
            template,
            data,
            expect_variables,
            expect_locals,
            expect_undefined,
            filters=expect_filters,
        )

    def test_analyze_rendered_template(self):
        """Test that we count references to variables in rendered templates."""
        loader = DictLoader({"foo": "{% assign bar = 42 %}{{ x | append: y }}"})
        env = Environment(loader=loader)

        template = env.from_string("{{ x }}{% render 'foo' %}{{ bar }}")
        data = {"y": 1, "z": 2}
        expect_variables = {"bar": 1, "x": 2, "y": 1}
        expect_locals = {"bar": 1}
        expect_undefined = {"x": 2, "bar": 1}
        expect_filters = {"append": 1}

        self._test(
            template,
            data,
            expect_variables,
            expect_locals,
            expect_undefined,
            filters=expect_filters,
        )

    def test_analyze_loop(self):
        """Test that we count variables in every iteration of a for loop."""
        template = Template(
            "{% for x in (1..5) %}{{ forloop.index }} {{ x }}{% endfor %}"
        )
        data = {"y": 1, "z": 2}
        expect_variables = {"x": 5, "forloop.index": 5}
        expect_locals = {}
        expect_undefined = {}

        self._test(template, data, expect_variables, expect_locals, expect_undefined)

    def test_analyze_broken_loop(self):
        """Test that we don't count variables after a loop break."""
        template = Template(
            "{% for x in (1..5) %}"
            "{{ forloop.index }} {{ x }}"
            "{% if forloop.index == 3 %}{% break %}{% endif %}"
            "{% endfor %}"
        )
        data = {"y": 1, "z": 2}
        expect_variables = {"x": 3, "forloop.index": 6}
        expect_locals = {}
        expect_undefined = {}

        self._test(template, data, expect_variables, expect_locals, expect_undefined)

    def test_analyze_indices(self):
        """Test that we count variables that include indices."""
        template = Template("{{ x.y[0].foo }}")
        data = {"x": {"y": [{"foo": 5}]}}
        expect_variables = {"x.y[0].foo": 1}
        expect_locals = {}
        expect_undefined = {}

        self._test(template, data, expect_variables, expect_locals, expect_undefined)

    def test_analyze_nested_identifiers(self):
        """Test that we count variables that nest identifiers."""
        template = Template("{{ x[y].foo }}")
        data = {"x": [{"foo": 5}], "y": 0}
        expect_variables = {"x[0].foo": 1, "y": 1}
        expect_locals = {}
        expect_undefined = {}

        self._test(template, data, expect_variables, expect_locals, expect_undefined)

    def test_analyze_quoted_identifiers(self):
        """Test that we count variables that quote identifiers."""
        template = Template("{{ x['y z'].foo }}")
        data = {"x": {"y z": {"foo": 5}}}
        expect_variables = {'x["y z"].foo': 1}
        expect_locals = {}
        expect_undefined = {}

        self._test(template, data, expect_variables, expect_locals, expect_undefined)

    def test_count_increment_tags(self):
        """Test that we count variable names from increment tags."""
        template = Template("{% increment x %}")
        data = {}
        expect_variables = {}
        expect_locals = {"x": 1}
        expect_undefined = {}

        self._test(template, data, expect_variables, expect_locals, expect_undefined)

    def test_count_decrement_tags(self):
        """Test that we count variable names from decrement tags."""
        template = Template("{% decrement x %}")
        data = {}
        expect_variables = {}
        expect_locals = {"x": 1}
        expect_undefined = {}

        self._test(template, data, expect_variables, expect_locals, expect_undefined)

    def test_explicit_resolve(self):
        """Test that calls to `Context.resolve()` are counted."""

        @with_context
        def mock_filter(val, *, context: Context) -> str:
            context.resolve("x")
            return f"{val} mock"

        env = Environment()
        env.add_filter("mock", mock_filter)
        template = env.from_string("{{ 'foo' | mock }}")

        data = {"x": "foo"}
        expect_variables = {"x": 1}
        expect_locals = {}
        expect_undefined = {}
        expect_filters = {"mock": 1}

        self._test(
            template,
            data,
            expect_variables,
            expect_locals,
            expect_undefined,
            filters=expect_filters,
        )
