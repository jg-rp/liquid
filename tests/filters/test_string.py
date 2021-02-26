import unittest
from inspect import isclass
from typing import NamedTuple, Any, List, Dict

from liquid.environment import Environment
from liquid.exceptions import FilterArgumentError

from liquid.builtin.filters.string import (
    Capitalize,
    Append,
    Downcase,
    Escape,
    EscapeOnce,
    LStrip,
    NewlineToBR,
    Prepend,
    Remove,
    RemoveFirst,
    Replace,
    ReplaceFirst,
    Slice,
    Split,
    Upcase,
    Strip,
    RStrip,
    StripHTML,
    StripNewlines,
    Truncate,
    TruncateWords,
    URLEncode,
    URLDecode,
)


class Case(NamedTuple):
    description: str
    val: Any
    args: List[Any]
    kwargs: Dict[Any, Any]
    expect: Any


class StringFilterTestCase(unittest.TestCase):
    """Test string filter functions."""

    def _test(self, filter_cls, test_cases):
        """Helper method for running lists of `Case`s"""
        env = Environment()
        func = filter_cls(env)

        for case in test_cases:
            with self.subTest(msg=case.description):
                if isclass(case.expect) and issubclass(
                    case.expect, FilterArgumentError
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
        ]

        self._test(Capitalize, test_cases)

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
        ]

        self._test(Append, test_cases)

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
        ]

        self._test(Downcase, test_cases)

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
        ]

        self._test(Escape, test_cases)

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
        ]

        self._test(EscapeOnce, test_cases)

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
        ]

        self._test(LStrip, test_cases)

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
        ]

        self._test(NewlineToBR, test_cases)

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
        ]

        self._test(Prepend, test_cases)

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
        ]

        self._test(Remove, test_cases)

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
        ]

        self._test(RemoveFirst, test_cases)

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
        ]

        self._test(Replace, test_cases)

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
        ]

        self._test(ReplaceFirst, test_cases)

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
        ]

        self._test(Slice, test_cases)

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
        ]

        self._test(Split, test_cases)

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
        ]

        self._test(Upcase, test_cases)

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
        ]

        self._test(Strip, test_cases)

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
        ]

        self._test(RStrip, test_cases)

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
        ]

        self._test(StripHTML, test_cases)

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
        ]

        self._test(StripNewlines, test_cases)

    def test_truncate_newlines(self):
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
                expect=FilterArgumentError,
            ),
            Case(
                description="too many arguments",
                val="hello",
                args=[5, "foo", "bar"],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self._test(Truncate, test_cases)

    def test_truncatewords_newlines(self):
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
                expect=FilterArgumentError,
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
        ]

        self._test(TruncateWords, test_cases)

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
        ]

        self._test(URLEncode, test_cases)

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
        ]

        self._test(URLDecode, test_cases)
