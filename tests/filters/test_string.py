import unittest

from functools import partial
from inspect import isclass

from typing import NamedTuple
from typing import Any
from typing import List
from typing import Dict

from liquid.environment import Environment
from liquid.exceptions import FilterArgumentError
from liquid.exceptions import FilterValueError

# New style filters
from liquid.builtin.filters._string import capitalize
from liquid.builtin.filters._string import append
from liquid.builtin.filters._string import downcase
from liquid.builtin.filters._string import escape
from liquid.builtin.filters._string import escape_once
from liquid.builtin.filters._string import lstrip
from liquid.builtin.filters._string import newline_to_br
from liquid.builtin.filters._string import prepend
from liquid.builtin.filters._string import remove
from liquid.builtin.filters._string import remove_first
from liquid.builtin.filters._string import replace
from liquid.builtin.filters._string import replace_first
from liquid.builtin.filters._string import slice_
from liquid.builtin.filters._string import split
from liquid.builtin.filters._string import upcase
from liquid.builtin.filters._string import strip
from liquid.builtin.filters._string import rstrip
from liquid.builtin.filters._string import strip_html
from liquid.builtin.filters._string import strip_newlines
from liquid.builtin.filters._string import truncate
from liquid.builtin.filters._string import truncatewords
from liquid.builtin.filters._string import url_encode
from liquid.builtin.filters._string import url_decode
from liquid.builtin.filters._string import base64_encode
from liquid.builtin.filters._string import base64_decode
from liquid.builtin.filters._string import base64_url_safe_encode
from liquid.builtin.filters._string import base64_url_safe_decode

# Depreciated class-based filters
from liquid.builtin.filters.string import Capitalize
from liquid.builtin.filters.string import Append
from liquid.builtin.filters.string import Downcase
from liquid.builtin.filters.string import Escape
from liquid.builtin.filters.string import EscapeOnce
from liquid.builtin.filters.string import LStrip
from liquid.builtin.filters.string import NewlineToBR
from liquid.builtin.filters.string import Prepend
from liquid.builtin.filters.string import Remove
from liquid.builtin.filters.string import RemoveFirst
from liquid.builtin.filters.string import Replace
from liquid.builtin.filters.string import ReplaceFirst
from liquid.builtin.filters.string import Slice
from liquid.builtin.filters.string import Split
from liquid.builtin.filters.string import Upcase
from liquid.builtin.filters.string import Strip
from liquid.builtin.filters.string import RStrip
from liquid.builtin.filters.string import StripHTML
from liquid.builtin.filters.string import StripNewlines
from liquid.builtin.filters.string import Truncate
from liquid.builtin.filters.string import TruncateWords
from liquid.builtin.filters.string import URLEncode
from liquid.builtin.filters.string import URLDecode


class Case(NamedTuple):
    description: str
    val: Any
    args: List[Any]
    kwargs: Dict[Any, Any]
    expect: Any


class StringFilterTestCase(unittest.TestCase):
    """Test string filter functions."""

    def setUp(self) -> None:
        self.env = Environment()

    def _test(self, filter_cls, test_cases):
        """Helper method for running lists of `Case`s"""
        with self.assertWarns(DeprecationWarning):
            func = filter_cls(self.env)

        for case in test_cases:
            with self.subTest(msg=case.description):
                if isclass(case.expect) and issubclass(
                    case.expect, (FilterArgumentError, FilterValueError)
                ):
                    with self.assertRaises(case.expect):
                        func(case.val, *case.args, **case.kwargs)
                else:
                    self.assertEqual(
                        func(case.val, *case.args, **case.kwargs), case.expect
                    )

    def _test_newstyle_filter(self, func, test_cases):
        if getattr(func, "with_environment", False):
            func = partial(func, environment=self.env)

        for case in test_cases:
            with self.subTest(msg=case.description):
                if isclass(case.expect) and issubclass(
                    case.expect, (FilterArgumentError, FilterValueError)
                ):
                    with self.assertRaises(case.expect):
                        func(case.val, *case.args, **case.kwargs)
                else:
                    self.assertEqual(
                        func(case.val, *case.args, **case.kwargs), case.expect
                    )

    def test_capitalize(self):
        """Test capitalize filter function."""

        test_cases = [
            Case(
                description="lower case string",
                val="hello",
                args=[],
                kwargs={},
                expect="Hello",
            ),
            Case(
                description="already capitalized string",
                val="Hello",
                args=[],
                kwargs={},
                expect="Hello",
            ),
            Case(
                description="unexpected argument",
                val="hello",
                args=[2],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect="",
            ),
        ]

        self._test(Capitalize, test_cases)
        self._test_newstyle_filter(capitalize, test_cases)

    def test_append(self):
        """Test append filter function."""

        test_cases = [
            Case(
                description="concat",
                val="hello",
                args=["there"],
                kwargs={},
                expect="hellothere",
            ),
            Case(
                description="not a string",
                val=5,
                args=["there"],
                kwargs={},
                expect="5there",
            ),
            Case(
                description="argument not a string",
                val="hello",
                args=[5],
                kwargs={},
                expect="hello5",
            ),
            Case(
                description="missing argument",
                val="hello",
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="too many arguments",
                val="hello",
                args=["how", "are", "you"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=["hi"],
                kwargs={},
                expect="hi",
            ),
            Case(
                description="undefined argument",
                val="hi",
                args=[self.env.undefined("test")],
                kwargs={},
                expect="hi",
            ),
        ]

        self._test(Append, test_cases)
        self._test_newstyle_filter(append, test_cases)

    def test_downcase(self):
        """Test downcase filter function."""

        test_cases = [
            Case(
                description="make lower case",
                val="HELLO",
                args=[],
                kwargs={},
                expect="hello",
            ),
            Case(
                description="not a string",
                val=5,
                args=[],
                kwargs={},
                expect="5",
            ),
            Case(
                description="unexpected argument",
                val="HELLO",
                args=[5],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect="",
            ),
        ]

        self._test(Downcase, test_cases)
        self._test_newstyle_filter(downcase, test_cases)

    def test_escape(self):
        """Test escape filter function."""

        test_cases = [
            Case(
                description="make HTML-safe",
                val="<p>test</p>",
                args=[],
                kwargs={},
                expect="&lt;p&gt;test&lt;/p&gt;",
            ),
            Case(
                description="not a string",
                val=5,
                args=[],
                kwargs={},
                expect="5",
            ),
            Case(
                description="unexpected argument",
                val="HELLO",
                args=[5],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect="",
            ),
        ]

        self._test(Escape, test_cases)
        self._test_newstyle_filter(escape, test_cases)

    def test_escape_once(self):
        """Test escape_once filter function."""

        test_cases = [
            Case(
                description="make HTML-safe",
                val="&lt;p&gt;test&lt;/p&gt;",
                args=[],
                kwargs={},
                expect="&lt;p&gt;test&lt;/p&gt;",
            ),
            Case(
                description="make HTML-safe from mixed safe and markup.",
                val="&lt;p&gt;test&lt;/p&gt;<p>test</p>",
                args=[],
                kwargs={},
                expect="&lt;p&gt;test&lt;/p&gt;&lt;p&gt;test&lt;/p&gt;",
            ),
            Case(
                description="not a string",
                val=5,
                args=[],
                kwargs={},
                expect="5",
            ),
            Case(
                description="unexpected argument",
                val="HELLO",
                args=[5],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect="",
            ),
        ]

        self._test(EscapeOnce, test_cases)
        self._test_newstyle_filter(escape_once, test_cases)

    def test_lstrip(self):
        """Test lstrip filter function."""

        test_cases = [
            Case(
                description="left padded",
                val=" \t\r\n  hello",
                args=[],
                kwargs={},
                expect="hello",
            ),
            Case(
                description="right padded",
                val="hello \t\r\n  ",
                args=[],
                kwargs={},
                expect="hello \t\r\n  ",
            ),
            Case(
                description="left and right padded",
                val=" \t\r\n  hello  \t\r\n ",
                args=[],
                kwargs={},
                expect="hello  \t\r\n ",
            ),
            Case(
                description="not a string",
                val=5,
                args=[],
                kwargs={},
                expect="5",
            ),
            Case(
                description="unexpected argument",
                val="hello",
                args=[5],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect="",
            ),
        ]

        self._test(LStrip, test_cases)
        self._test_newstyle_filter(lstrip, test_cases)

    def test_newline_to_br(self):
        """Test newline_to_br filter function."""

        test_cases = [
            Case(
                description="string with newlines",
                val="- apples\n- oranges\n",
                args=[],
                kwargs={},
                expect="- apples<br />\n- oranges<br />\n",
            ),
            Case(
                description="not a string",
                val=5,
                args=[],
                kwargs={},
                expect="5",
            ),
            Case(
                description="unexpected argument",
                val="hello",
                args=[5],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="reference implementation test 1",
                val="a\nb\nc",
                args=[],
                kwargs={},
                expect="a<br />\nb<br />\nc",
            ),
            Case(
                description="reference implementation test 2",
                val="a\r\nb\nc",
                args=[],
                kwargs={},
                expect="a<br />\nb<br />\nc",
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect="",
            ),
        ]

        self._test(NewlineToBR, test_cases)
        self._test_newstyle_filter(newline_to_br, test_cases)

    def test_prepend(self):
        """Test prepend filter function."""

        test_cases = [
            Case(
                description="concat",
                val="hello",
                args=["there"],
                kwargs={},
                expect="therehello",
            ),
            Case(
                description="not a string",
                val=5,
                args=["there"],
                kwargs={},
                expect="there5",
            ),
            Case(
                description="argument not a string",
                val="hello",
                args=[5],
                kwargs={},
                expect="5hello",
            ),
            Case(
                description="missing argument",
                val="hello",
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="too many arguments",
                val="hello",
                args=["how", "are", "you"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=["hi"],
                kwargs={},
                expect="hi",
            ),
            Case(
                description="undefined argument",
                val="hi",
                args=[self.env.undefined("test")],
                kwargs={},
                expect="hi",
            ),
        ]

        self._test(Prepend, test_cases)
        self._test_newstyle_filter(prepend, test_cases)

    def test_remove(self):
        """Test remove filter function."""

        test_cases = [
            Case(
                description="remove substrings",
                val="I strained to see the train through the rain",
                args=["rain"],
                kwargs={},
                expect="I sted to see the t through the ",
            ),
            Case(
                description="not a string",
                val=5,
                args=["there"],
                kwargs={},
                expect="5",
            ),
            Case(
                description="argument not a string",
                val="hello",
                args=[5],
                kwargs={},
                expect="hello",
            ),
            Case(
                description="missing argument",
                val="hello",
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="too many arguments",
                val="hello",
                args=["how", "are", "you"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=["rain"],
                kwargs={},
                expect="",
            ),
            Case(
                description="undefined argument",
                val="I strained to see the train through the rain",
                args=[self.env.undefined("test")],
                kwargs={},
                expect="I strained to see the train through the rain",
            ),
        ]

        self._test(Remove, test_cases)
        self._test_newstyle_filter(remove, test_cases)

    def test_remove_first(self):
        """Test remove_first filter function."""

        test_cases = [
            Case(
                description="remove substrings",
                val="I strained to see the train through the rain",
                args=["rain"],
                kwargs={},
                expect="I sted to see the train through the rain",
            ),
            Case(
                description="not a string",
                val=5,
                args=["rain"],
                kwargs={},
                expect="5",
            ),
            Case(
                description="argument not a string",
                val="hello",
                args=[5],
                kwargs={},
                expect="hello",
            ),
            Case(
                description="missing argument",
                val="hello",
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="too many arguments",
                val="hello",
                args=["how", "are", "you"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=["rain"],
                kwargs={},
                expect="",
            ),
            Case(
                description="undefined argument",
                val="I strained to see the train through the rain",
                args=[self.env.undefined("test")],
                kwargs={},
                expect="I strained to see the train through the rain",
            ),
        ]

        self._test(RemoveFirst, test_cases)
        self._test_newstyle_filter(remove_first, test_cases)

    def test_replace(self):
        """Test replace filter function."""

        test_cases = [
            Case(
                description="replace substrings",
                val="Take my protein pills and put my helmet on",
                args=["my", "your"],
                kwargs={},
                expect="Take your protein pills and put your helmet on",
            ),
            Case(
                description="not a string",
                val=5,
                args=["rain", "foo"],
                kwargs={},
                expect="5",
            ),
            Case(
                description="argument not a string",
                val="hello",
                args=[5, "your"],
                kwargs={},
                expect="hello",
            ),
            Case(
                description="missing argument",
                val="hello",
                args=["my"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="missing arguments",
                val="hello",
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="too many arguments",
                val="hello",
                args=["how", "are", "you"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=["my", "your"],
                kwargs={},
                expect="",
            ),
            Case(
                description="undefined first argument",
                val="Take my protein pills and put my helmet on",
                args=[self.env.undefined("test"), "your"],
                kwargs={},
                expect="your",
            ),
            Case(
                description="undefined second argument",
                val="Take my protein pills and put my helmet on",
                args=["my", self.env.undefined("test")],
                kwargs={},
                expect="Take  protein pills and put  helmet on",
            ),
        ]

        self._test(Replace, test_cases)
        self._test_newstyle_filter(replace, test_cases)

    def test_replace_first(self):
        """Test replace_first filter function."""

        test_cases = [
            Case(
                description="replace substrings",
                val="Take my protein pills and put my helmet on",
                args=["my", "your"],
                kwargs={},
                expect="Take your protein pills and put my helmet on",
            ),
            Case(
                description="not a string",
                val=5,
                args=["rain", "foo"],
                kwargs={},
                expect="5",
            ),
            Case(
                description="argument not a string",
                val="hello5",
                args=[5, "your"],
                kwargs={},
                expect="helloyour",
            ),
            Case(
                description="missing argument",
                val="hello",
                args=["my"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="missing arguments",
                val="hello",
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="too many arguments",
                val="hello",
                args=["how", "are", "you"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=["my", "your"],
                kwargs={},
                expect="",
            ),
            Case(
                description="undefined first argument",
                val="Take my protein pills and put my helmet on",
                args=[self.env.undefined("test"), "your"],
                kwargs={},
                expect="your",
            ),
            Case(
                description="undefined second argument",
                val="Take my protein pills and put my helmet on",
                args=["my", self.env.undefined("test")],
                kwargs={},
                expect="Take  protein pills and put my helmet on",
            ),
        ]

        self._test(ReplaceFirst, test_cases)
        self._test_newstyle_filter(replace_first, test_cases)

    def test_slice(self):
        """Test slice filter function."""

        test_cases = [
            Case(
                description="zero",
                val="hello",
                args=[0],
                kwargs={},
                expect="h",
            ),
            Case(
                description="one",
                val="hello",
                args=[1],
                kwargs={},
                expect="e",
            ),
            Case(
                description="one length three",
                val="hello",
                args=[1, 3],
                kwargs={},
                expect="ell",
            ),
            Case(
                description="out of range",
                val="hello",
                args=[99],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="not a string",
                val=5,
                args=[1],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="first argument not an integer",
                val="hello",
                args=["foo"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="second argument not an integer",
                val="hello",
                args=[5, "foo"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="missing arguments",
                val="hello",
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="too many arguments",
                val="hello",
                args=[1, 2, 3],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="unexpected keyword arguments",
                val="hello",
                args=[1, 2],
                kwargs={"x": "y"},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[1, 3],
                kwargs={},
                expect="",
            ),
            Case(
                description="undefined first argument",
                val="hello",
                args=[self.env.undefined("test"), 3],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined second argument",
                val="hello",
                args=[1, self.env.undefined("test")],
                kwargs={},
                expect="e",
            ),
        ]

        self._test(Slice, test_cases)
        self._test_newstyle_filter(slice_, test_cases)

    def test_split(self):
        """Test split filter function."""

        test_cases = [
            Case(
                description="split string",
                val="Hi, how are you today?",
                args=[
                    " ",
                ],
                kwargs={},
                expect=["Hi,", "how", "are", "you", "today?"],
            ),
            Case(
                description="not a string",
                val=5,
                args=[" "],
                kwargs={},
                expect=["5"],
            ),
            Case(
                description="argument not a string",
                val="hello th1ere",
                args=[1],
                kwargs={},
                expect=["hello th", "ere"],
            ),
            Case(
                description="missing argument",
                val="hello there",
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="too many arguments",
                val="hello there",
                args=[" ", ","],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[" "],
                kwargs={},
                expect=[""],
            ),
            Case(
                description="undefined argument",
                val="Hi, how are you today?",
                args=[self.env.undefined("test")],
                kwargs={},
                expect=[
                    "H",
                    "i",
                    ",",
                    " ",
                    "h",
                    "o",
                    "w",
                    " ",
                    "a",
                    "r",
                    "e",
                    " ",
                    "y",
                    "o",
                    "u",
                    " ",
                    "t",
                    "o",
                    "d",
                    "a",
                    "y",
                    "?",
                ],
            ),
        ]

        self._test(Split, test_cases)
        self._test_newstyle_filter(split, test_cases)

    def test_upcase(self):
        """Test upcase filter function."""

        test_cases = [
            Case(
                description="make lower case",
                val="hello",
                args=[],
                kwargs={},
                expect="HELLO",
            ),
            Case(
                description="not a string",
                val=5,
                args=[],
                kwargs={},
                expect="5",
            ),
            Case(
                description="unexpected argument",
                val="hello",
                args=[5],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect="",
            ),
        ]

        self._test(Upcase, test_cases)
        self._test_newstyle_filter(upcase, test_cases)

    def test_strip(self):
        """Test strip filter function."""

        test_cases = [
            Case(
                description="left padded",
                val=" \t\r\n  hello",
                args=[],
                kwargs={},
                expect="hello",
            ),
            Case(
                description="right padded",
                val="hello \t\r\n  ",
                args=[],
                kwargs={},
                expect="hello",
            ),
            Case(
                description="left and right padded",
                val=" \t\r\n  hello  \t\r\n ",
                args=[],
                kwargs={},
                expect="hello",
            ),
            Case(
                description="not a string",
                val=5,
                args=[],
                kwargs={},
                expect="5",
            ),
            Case(
                description="unexpected argument",
                val="hello",
                args=[5],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect="",
            ),
        ]

        self._test(Strip, test_cases)
        self._test_newstyle_filter(strip, test_cases)

    def test_rstrip(self):
        """Test rstrip filter function."""

        test_cases = [
            Case(
                description="left padded",
                val=" \t\r\n  hello",
                args=[],
                kwargs={},
                expect=" \t\r\n  hello",
            ),
            Case(
                description="right padded",
                val="hello \t\r\n  ",
                args=[],
                kwargs={},
                expect="hello",
            ),
            Case(
                description="left and right padded",
                val=" \t\r\n  hello  \t\r\n ",
                args=[],
                kwargs={},
                expect=" \t\r\n  hello",
            ),
            Case(
                description="not a string",
                val=5,
                args=[],
                kwargs={},
                expect="5",
            ),
            Case(
                description="unexpected argument",
                val="hello",
                args=[5],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect="",
            ),
        ]

        self._test(RStrip, test_cases)
        self._test_newstyle_filter(rstrip, test_cases)

    def test_strip_html(self):
        """Test strip_html filter function."""

        test_cases = [
            Case(
                description="some HTML markup",
                val="Have <em>you</em> read <strong>Ulysses</strong> &amp; &#20;?",
                args=[],
                kwargs={},
                expect="Have you read Ulysses &amp; &#20;?",
            ),
            Case(
                description="some HTML markup with HTML comment",
                val=(
                    "<!-- Have --><em>you</em> read "
                    "<strong>Ulysses</strong> &amp; &#20;?"
                ),
                args=[],
                kwargs={},
                expect="you read Ulysses &amp; &#20;?",
            ),
            Case(
                description="not a string",
                val=5,
                args=[],
                kwargs={},
                expect="5",
            ),
            Case(
                description="unexpected argument",
                val="hello",
                args=[5],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect="",
            ),
        ]

        self._test(StripHTML, test_cases)
        self._test_newstyle_filter(strip_html, test_cases)

    def test_strip_newlines(self):
        """Test strip_newlines filter function."""

        test_cases = [
            Case(
                description="newline and other whitespace",
                val="hello there\nyou",
                args=[],
                kwargs={},
                expect="hello thereyou",
            ),
            Case(
                description="not a string",
                val=5,
                args=[],
                kwargs={},
                expect="5",
            ),
            Case(
                description="unexpected argument",
                val="hello",
                args=[5],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="reference implementation test 1",
                val="a\nb\nc",
                args=[],
                kwargs={},
                expect="abc",
            ),
            Case(
                description="reference implementation test 2",
                val="a\r\nb\nc",
                args=[],
                kwargs={},
                expect="abc",
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect="",
            ),
        ]

        self._test(StripNewlines, test_cases)
        self._test_newstyle_filter(strip_newlines, test_cases)

    def test_truncate(self):
        """Test truncate filter function."""

        test_cases = [
            Case(
                description="default end",
                val="Ground control to Major Tom.",
                args=[20],
                kwargs={},
                expect="Ground control to...",
            ),
            Case(
                description="custom end",
                val="Ground control to Major Tom.",
                args=[25, ", and so on"],
                kwargs={},
                expect="Ground control, and so on",
            ),
            Case(
                description="no end",
                val="Ground control to Major Tom.",
                args=[20, ""],
                kwargs={},
                expect="Ground control to Ma",
            ),
            Case(
                description="string is shorter than length",
                val="Ground control",
                args=[20],
                kwargs={},
                expect="Ground control",
            ),
            Case(
                description="not a string",
                val=5,
                args=[10],
                kwargs={},
                expect="5",
            ),
            Case(
                description="too many arguments",
                val="hello",
                args=[5, "foo", "bar"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[5],
                kwargs={},
                expect="",
            ),
            Case(
                description="undefined first argument",
                val="Ground control to Major Tom.",
                args=[self.env.undefined("test")],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined second argument",
                val="Ground control to Major Tom.",
                args=[20, self.env.undefined("test")],
                kwargs={},
                expect="Ground control to Ma",
            ),
        ]

        self._test(Truncate, test_cases)
        self._test_newstyle_filter(truncate, test_cases)

    def test_truncatewords(self):
        """Test truncatewords filter function."""

        test_cases = [
            Case(
                description="default end",
                val="Ground control to Major Tom.",
                args=[3],
                kwargs={},
                expect="Ground control to...",
            ),
            Case(
                description="custom end",
                val="Ground control to Major Tom.",
                args=[3, "--"],
                kwargs={},
                expect="Ground control to--",
            ),
            Case(
                description="no end",
                val="Ground control to Major Tom.",
                args=[3, ""],
                kwargs={},
                expect="Ground control to",
            ),
            Case(
                description="fewer words than word count",
                val="Ground control",
                args=[3],
                kwargs={},
                expect="Ground control",
            ),
            Case(
                description="not a string",
                val=5,
                args=[10],
                kwargs={},
                expect="5",
            ),
            Case(
                description="too many arguments",
                val="hello",
                args=[5, "foo", "bar"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="reference implementation test 1",
                val="测试测试测试测试",
                args=[5],
                kwargs={},
                expect="测试测试测试测试",
            ),
            Case(
                description="reference implementation test 2",
                val="one two three",
                args=[2, 1],
                kwargs={},
                expect="one two1",
            ),
            Case(
                description="reference implementation test 3",
                val="one  two\tthree\nfour",
                args=[3],
                kwargs={},
                expect="one two three...",
            ),
            Case(
                description="reference implementation test 4",
                val="one two three four",
                args=[2],
                kwargs={},
                expect="one two...",
            ),
            Case(
                description="reference implementation test 5",
                val="one two three four",
                args=[0],
                kwargs={},
                expect="one...",
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[5],
                kwargs={},
                expect="",
            ),
            Case(
                description="undefined first argument",
                val="one two three four",
                args=[self.env.undefined("test")],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined second argument",
                val="one two three four",
                args=[2, self.env.undefined("test")],
                kwargs={},
                expect="one two",
            ),
            Case(
                description="very long argument",
                val="",
                args=[100000000000000],
                kwargs={},
                expect="",
            ),
        ]

        self._test(TruncateWords, test_cases)
        self._test_newstyle_filter(truncatewords, test_cases)

    def test_url_encode_html(self):
        """Test url_encode filter function."""

        test_cases = [
            Case(
                description="some special URL characters",
                val="email address is bob@example.com!",
                args=[],
                kwargs={},
                expect="email+address+is+bob%40example.com%21",
            ),
            Case(
                description="not a string",
                val=5,
                args=[],
                kwargs={},
                expect="5",
            ),
            Case(
                description="unexpected argument",
                val="hello",
                args=[5],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect="",
            ),
        ]

        self._test(URLEncode, test_cases)
        self._test_newstyle_filter(url_encode, test_cases)

    def test_url_decode_html(self):
        """Test url_decode filter function."""

        test_cases = [
            Case(
                description="some special URL characters",
                val="email+address+is+bob%40example.com%21",
                args=[],
                kwargs={},
                expect="email address is bob@example.com!",
            ),
            Case(
                description="not a string",
                val=5,
                args=[],
                kwargs={},
                expect="5",
            ),
            Case(
                description="unexpected argument",
                val="hello",
                args=[5],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect="",
            ),
        ]

        self._test(URLDecode, test_cases)
        self._test_newstyle_filter(url_decode, test_cases)

    def test_base64_encode(self):
        """Test base64_encode filter function."""

        test_cases = [
            Case(
                description="from string",
                val="_#/.",
                args=[],
                kwargs={},
                expect="XyMvLg==",
            ),
            Case(
                description="from string with URL unsafe",
                val=(
                    r"abcdefghijklmnopqrstuvwxyz "
                    r"ABCDEFGHIJKLMNOPQRSTUVWXYZ "
                    r"1234567890 !@#$%^&*()-=_+/?.:;[]{}\|"
                ),
                args=[],
                kwargs={},
                expect=(
                    "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXogQUJDREVGR0hJSktMTU5PUFFSU1RVV"
                    "ldYWVogMTIzNDU2Nzg5MCAhQCMkJV4mKigpLT1fKy8/Ljo7W117fVx8"
                ),
            ),
            Case(
                description="not a string",
                val=5,
                args=[],
                kwargs={},
                expect="NQ==",
            ),
            Case(
                description="unexpected argument",
                val="hello",
                args=[5],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect="",
            ),
        ]

        self._test_newstyle_filter(base64_encode, test_cases)

    def test_base64_decode(self):
        """Test base64_decode filter function."""

        test_cases = [
            Case(
                description="from string",
                val="XyMvLg==",
                args=[],
                kwargs={},
                expect="_#/.",
            ),
            Case(
                description="from string with URL unsafe",
                val=(
                    "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXogQUJDREVGR0hJSktMTU5PUFFSU1RVV"
                    "ldYWVogMTIzNDU2Nzg5MCAhQCMkJV4mKigpLT1fKy8/Ljo7W117fVx8"
                ),
                args=[],
                kwargs={},
                expect=(
                    r"abcdefghijklmnopqrstuvwxyz "
                    r"ABCDEFGHIJKLMNOPQRSTUVWXYZ "
                    r"1234567890 !@#$%^&*()-=_+/?.:;[]{}\|"
                ),
            ),
            Case(
                description="not a string",
                val=5,
                args=[],
                kwargs={},
                expect=FilterValueError,
            ),
            Case(
                description="unexpected argument",
                val="hello",
                args=[5],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect="",
            ),
        ]

        self._test_newstyle_filter(base64_decode, test_cases)

    def test_base64_url_safe_encode(self):
        """Test base64_url_safe_encode filter function."""

        test_cases = [
            Case(
                description="from string",
                val="_#/.",
                args=[],
                kwargs={},
                expect="XyMvLg==",
            ),
            Case(
                description="from string with URL unsafe",
                val=(
                    r"abcdefghijklmnopqrstuvwxyz "
                    r"ABCDEFGHIJKLMNOPQRSTUVWXYZ "
                    r"1234567890 !@#$%^&*()-=_+/?.:;[]{}\|"
                ),
                args=[],
                kwargs={},
                expect=(
                    "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXogQUJDREVGR0hJSktMTU5PUFFSU1RVV"
                    "ldYWVogMTIzNDU2Nzg5MCAhQCMkJV4mKigpLT1fKy8_Ljo7W117fVx8"
                ),
            ),
            Case(
                description="not a string",
                val=5,
                args=[],
                kwargs={},
                expect="NQ==",
            ),
            Case(
                description="unexpected argument",
                val="hello",
                args=[5],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect="",
            ),
        ]

        self._test_newstyle_filter(base64_url_safe_encode, test_cases)

    def test_base64_url_safe_decode(self):
        """Test base64_url_safe_decode filter function."""

        test_cases = [
            Case(
                description="from string",
                val="XyMvLg==",
                args=[],
                kwargs={},
                expect="_#/.",
            ),
            Case(
                description="from string with URL unsafe",
                val=(
                    "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXogQUJDREVGR0hJSktMTU5PUFFSU1RVV"
                    "ldYWVogMTIzNDU2Nzg5MCAhQCMkJV4mKigpLT1fKy8_Ljo7W117fVx8"
                ),
                args=[],
                kwargs={},
                expect=(
                    r"abcdefghijklmnopqrstuvwxyz "
                    r"ABCDEFGHIJKLMNOPQRSTUVWXYZ "
                    r"1234567890 !@#$%^&*()-=_+/?.:;[]{}\|"
                ),
            ),
            Case(
                description="not a string",
                val=5,
                args=[],
                kwargs={},
                expect=FilterValueError,
            ),
            Case(
                description="unexpected argument",
                val="hello",
                args=[5],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect="",
            ),
        ]

        self._test_newstyle_filter(base64_url_safe_decode, test_cases)
