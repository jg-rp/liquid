"""Test html filter functions."""
import unittest

from functools import partial
from inspect import isclass

from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import NamedTuple

try:
    import markupsafe  # pylint: disable=unused-import # noqa: F401

    MARKUPSAFE_AVAILABLE = True
except ImportError:
    MARKUPSAFE_AVAILABLE = False

from liquid.environment import Environment
from liquid.exceptions import Error

from liquid.extra.filters.html import script_tag
from liquid.extra.filters.html import stylesheet_tag

from liquid import Markup


class Case(NamedTuple):
    """Table-driven test helper."""

    description: str
    val: Any
    args: List[Any]
    kwargs: Dict[Any, Any]
    expect: Any


class HTMLFilterTestCase(unittest.TestCase):
    """Test HTML filter functions."""

    def setUp(self) -> None:
        self.env = Environment()

    def _test(self, func, test_cases: Iterable[Case]):
        if getattr(func, "with_environment", False):
            func = partial(func, environment=self.env)

        for case in test_cases:
            with self.subTest(msg=case.description):
                if isclass(case.expect) and issubclass(case.expect, Error):
                    with self.assertRaises(case.expect):
                        func(case.val, *case.args, **case.kwargs)
                else:
                    self.assertEqual(
                        func(case.val, *case.args, **case.kwargs), case.expect
                    )

    def test_stylesheet_tag(self):
        """Test `stylesheet_tag` filter function."""
        test_cases = [
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
                expect=(
                    '<link href="42" rel="stylesheet" type="text/css" media="all" />'
                ),
            ),
        ]

        self._test(stylesheet_tag, test_cases)

    @unittest.skipIf(not MARKUPSAFE_AVAILABLE, "this test requires markupsafe")
    def test_stylesheet_tag_auto_escape(self):
        """Test `stylesheet_tag` filter function when autoescape is enabled."""
        test_cases = [
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

        self.env.autoescape = True
        self._test(stylesheet_tag, test_cases)

    def test_script_tag(self):
        """Test `script_tag` filter function."""
        test_cases = [
            Case(
                description="relative url",
                val="assets/app.js",
                args=[],
                kwargs={},
                expect='<script src="assets/app.js" type="text/javascript"></script>',
            ),
            Case(
                description="remote url",
                val="https://example.com/static/assets/app.js",
                args=[],
                kwargs={},
                expect=(
                    "<script "
                    'src="https://example.com/static/assets/app.js" '
                    'type="text/javascript">'
                    "</script>"
                ),
            ),
            Case(
                description="not a string",
                val=42,
                args=[],
                kwargs={},
                expect='<script src="42" type="text/javascript"></script>',
            ),
        ]

        self._test(script_tag, test_cases)

    @unittest.skipIf(not MARKUPSAFE_AVAILABLE, "this test requires markupsafe")
    def test_script_tag_auto_escape(self):
        """Test `script_tag` filter function when autoescape is enabled."""
        test_cases = [
            Case(
                description="relative url",
                val="assets/assets/app.js",
                args=[],
                kwargs={},
                expect=(
                    '<script src="assets/assets/app.js" '
                    'type="text/javascript"></script>'
                ),
            ),
            Case(
                description="unsafe url from context",
                val="<b>assets/assets/app.js</b>",
                args=[],
                kwargs={},
                expect=(
                    '<script src="&lt;b&gt;assets/assets/app.js&lt;/b&gt;" '
                    'type="text/javascript"></script>'
                ),
            ),
            Case(
                description="safe url from context",
                val=Markup("<b>assets/assets/app.js</b>"),
                args=[],
                kwargs={},
                expect=(
                    '<script src="&lt;b&gt;assets/assets/app.js&lt;/b&gt;" '
                    'type="text/javascript"></script>'
                ),
            ),
        ]

        self.env.autoescape = True
        self._test(script_tag, test_cases)
