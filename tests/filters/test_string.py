"""Test cases for string filters."""
# pylint: disable=too-many-public-methods,too-many-lines,missing-class-docstring
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
from liquid.exceptions import FilterError

from liquid.builtin.filters.string import capitalize
from liquid.builtin.filters.string import append
from liquid.builtin.filters.string import downcase
from liquid.builtin.filters.string import escape
from liquid.builtin.filters.string import escape_once
from liquid.builtin.filters.string import lstrip
from liquid.builtin.filters.string import newline_to_br
from liquid.builtin.filters.string import prepend
from liquid.builtin.filters.string import remove
from liquid.builtin.filters.string import remove_first
from liquid.builtin.filters.string import replace
from liquid.builtin.filters.string import replace_first
from liquid.builtin.filters.string import replace_last
from liquid.builtin.filters.string import slice_
from liquid.builtin.filters.string import split
from liquid.builtin.filters.string import upcase
from liquid.builtin.filters.string import strip
from liquid.builtin.filters.string import rstrip
from liquid.builtin.filters.string import strip_html
from liquid.builtin.filters.string import strip_newlines
from liquid.builtin.filters.string import truncate
from liquid.builtin.filters.string import truncatewords
from liquid.builtin.filters.string import url_encode
from liquid.builtin.filters.string import url_decode
from liquid.builtin.filters.string import base64_encode
from liquid.builtin.filters.string import base64_decode
from liquid.builtin.filters.string import base64_url_safe_encode
from liquid.builtin.filters.string import base64_url_safe_decode


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

    def _test(self, func, test_cases):
        if getattr(func, "with_environment", False):
            func = partial(func, environment=self.env)

        for case in test_cases:
            with self.subTest(msg=case.description):
                if isclass(case.expect) and issubclass(
                    case.expect, (FilterArgumentError, FilterValueError, FilterError)
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

        self._test(capitalize, test_cases)

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

        self._test(append, test_cases)

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

        self._test(downcase, test_cases)

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

        self._test(escape, test_cases)

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

        self._test(escape_once, test_cases)

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

        self._test(lstrip, test_cases)

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

        self._test(newline_to_br, test_cases)

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

        self._test(prepend, test_cases)

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

        self._test(remove, test_cases)

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

        self._test(remove_first, test_cases)

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
                args=["ll"],
                kwargs={},
                expect="heo",
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
                val="Take my protein",
                args=[self.env.undefined("test"), "#"],
                kwargs={},
                expect="#T#a#k#e# #m#y# #p#r#o#t#e#i#n#",
            ),
            Case(
                description="undefined second argument",
                val="Take my protein pills and put my helmet on",
                args=["my", self.env.undefined("test")],
                kwargs={},
                expect="Take  protein pills and put  helmet on",
            ),
        ]

        self._test(replace, test_cases)

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
                args=["ll"],
                kwargs={},
                expect="heo",
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
                expect="yourTake my protein pills and put my helmet on",
            ),
            Case(
                description="undefined second argument",
                val="Take my protein pills and put my helmet on",
                args=["my", self.env.undefined("test")],
                kwargs={},
                expect="Take  protein pills and put my helmet on",
            ),
        ]

        self._test(replace_first, test_cases)

    def test_replace_last(self):
        """Test replace_last filter function."""
        test_cases = [
            Case(
                description="not a string",
                val=5,
                args=["rain", "foo"],
                kwargs={},
                expect="5",
            ),
            Case(
                description="replace substrings",
                val="Take my protein pills and put my helmet on",
                args=["my", "your"],
                kwargs={},
                expect="Take my protein pills and put your helmet on",
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
                args=["ll"],
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
                expect="Take my protein pills and put my helmet onyour",
            ),
            Case(
                description="undefined second argument",
                val="Take my protein pills and put my helmet on",
                args=["my", self.env.undefined("test")],
                kwargs={},
                expect="Take my protein pills and put  helmet on",
            ),
        ]

        self._test(replace_last, test_cases)

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
                expect="",
            ),
            Case(
                description="not a string",
                val=5,
                args=[0],
                kwargs={},
                expect="5",
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
            Case(
                description="big negative second argument",
                val="foobar",
                args=[0, -(1 << 64)],
                kwargs={},
                expect="",
            ),
            Case(
                description="big positive second argument",
                val="foobar",
                args=[0, 1 << 63],
                kwargs={},
                expect="foobar",
            ),
            Case(
                description="big positive first argument",
                val="foobar",
                args=[1 << 63, 6],
                kwargs={},
                expect="",
            ),
            Case(
                description="big negative first argument",
                val="foobar",
                args=[-(1 << 63), 6],
                kwargs={},
                expect="",
            ),
            Case(
                description="array input",
                val=["f", "o", "o", "b", "a", "r"],
                args=[1, 3],
                kwargs={},
                expect=["o", "o", "b"],
            ),
        ]

        self._test(slice_, test_cases)

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

        self._test(split, test_cases)

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

        self._test(upcase, test_cases)

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

        self._test(strip, test_cases)

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

        self._test(rstrip, test_cases)

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

        self._test(strip_html, test_cases)

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

        self._test(strip_newlines, test_cases)

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
            Case(
                description="default length is 50",
                val="Ground control to Major Tom. Ground control to Major Tom.",
                args=[],
                kwargs={},
                expect="Ground control to Major Tom. Ground control to ...",
            ),
            Case(
                description="big positive argument",
                val="foobar",
                args=[1 << 63],
                kwargs={},
                expect="foobar",
            ),
            Case(
                description="big negative argument",
                val="foobar",
                args=[-(1 << 63)],
                kwargs={},
                expect="...",
            ),
        ]

        self._test(truncate, test_cases)

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
            Case(
                description="default number of words is 15",
                val="a b c d e f g h i j k l m n o p q",
                args=[],
                kwargs={},
                expect="a b c d e f g h i j k l m n o...",
            ),
            Case(
                description="big positive argument",
                val="one two three four",
                args=[1 << 31],
                kwargs={},
                expect="one two three four",
            ),
            Case(
                description="big negative argument",
                val="one two three four",
                args=[-(1 << 31)],
                kwargs={},
                expect="one...",
            ),
        ]

        self._test(truncatewords, test_cases)

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

        self._test(url_encode, test_cases)

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

        self._test(url_decode, test_cases)

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

        self._test(base64_encode, test_cases)

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
                expect=FilterError,
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

        self._test(base64_decode, test_cases)

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

        self._test(base64_url_safe_encode, test_cases)

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
                expect=FilterError,
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

        self._test(base64_url_safe_decode, test_cases)
