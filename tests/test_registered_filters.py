"""Test that all standard filters have been registered correctly."""

import datetime
import unittest
from typing import NamedTuple

from liquid import Environment
from liquid.extra import add_filters


class Case(NamedTuple):
    """Table-driven test helper."""

    description: str
    template: str
    context: dict
    expect: str


class FilterRegisterTestCase(unittest.TestCase):
    """Test that all standard filters have been registered correctly."""

    def test_filters(self) -> None:
        """Standard filter tests."""
        test_cases = [
            Case(
                description="append",
                template=r"{{ 'hello ' | append: foo }}",
                context={"foo": "there"},
                expect="hello there",
            ),
            Case(
                description="capitalize",
                template=r"{{ 'helLO' | capitalize }}",
                context={},
                expect="Hello",
            ),
            Case(
                description="downcase",
                template=r"{{ 'helLO' | downcase }}",
                context={},
                expect="hello",
            ),
            Case(
                description="escape",
                template=r"{{ foo | escape }}",
                context={"foo": "<p>hello</p>"},
                expect="&lt;p&gt;hello&lt;/p&gt;",
            ),
            Case(
                description="escape once",
                template=r"{{ foo | escape_once }}",
                context={"foo": "&lt;p&gt;hello&lt;/p&gt;"},
                expect="&lt;p&gt;hello&lt;/p&gt;",
            ),
            Case(
                description="lstrip",
                template=r"{{ foo | lstrip }}",
                context={"foo": " \t\r\n  hello\t"},
                expect="hello\t",
            ),
            Case(
                description="newline to br",
                template=r"{{ foo | newline_to_br }}",
                context={"foo": "- apples\n- oranges\n"},
                expect="- apples<br />\n- oranges<br />\n",
            ),
            Case(
                description="prepend",
                template=r"{{ foo | prepend: bar }}",
                context={"foo": "hello", "bar": "there"},
                expect="therehello",
            ),
            Case(
                description="remove",
                template=r"{{ foo | remove: bar }}",
                context={
                    "foo": "I strained to see the train through the rain",
                    "bar": "rain",
                },
                expect="I sted to see the t through the ",
            ),
            Case(
                description="remove first",
                template=r"{{ foo | remove_first: bar }}",
                context={
                    "foo": "I strained to see the train through the rain",
                    "bar": "rain",
                },
                expect="I sted to see the train through the rain",
            ),
            Case(
                description="replace",
                template=r"{{ foo | replace: bar, baz }}",
                context={
                    "foo": "Take my protein pills and put my helmet on",
                    "bar": "my",
                    "baz": "your",
                },
                expect="Take your protein pills and put your helmet on",
            ),
            Case(
                description="replace first",
                template=r"{{ foo | replace_first: bar, baz }}",
                context={
                    "foo": "Take my protein pills and put my helmet on",
                    "bar": "my",
                    "baz": "your",
                },
                expect="Take your protein pills and put my helmet on",
            ),
            Case(
                description="slice",
                template=r"{{ foo | slice: 1, 3 }}",
                context={"foo": "hello"},
                expect="ell",
            ),
            Case(
                description="split",
                template=r"{{ foo | split: ' ' | join: '#' }}",
                context={"foo": "Hi, how are you today?"},
                expect="Hi,#how#are#you#today?",
            ),
            Case(
                description="upcase",
                template=r"{{ foo | upcase }}",
                context={"foo": "hello"},
                expect="HELLO",
            ),
            Case(
                description="strip",
                template=r"{{ foo | strip }}",
                context={"foo": " \t\r\n  hello  \t\r\n "},
                expect="hello",
            ),
            Case(
                description="rstrip",
                template=r"{{ foo | rstrip }}",
                context={"foo": " \t\r\n  hello  \t\r\n "},
                expect=" \t\r\n  hello",
            ),
            Case(
                description="strip html",
                template=r"{{ foo | strip_html }}",
                context={"foo": "Have <em>you</em> read <b>Ulysses</b> &amp; &#20;?"},
                expect="Have you read Ulysses &amp; &#20;?",
            ),
            Case(
                description="strip newlines",
                template=r"{{ foo | strip_newlines }}",
                context={"foo": "hello there\nyou"},
                expect="hello thereyou",
            ),
            Case(
                description="truncate",
                template=r"{{ foo | truncate: 20 }}",
                context={"foo": "Ground control to Major Tom."},
                expect="Ground control to...",
            ),
            Case(
                description="truncate words",
                template=r"{{ foo | truncatewords: 3 }}",
                context={"foo": "Ground control to Major Tom."},
                expect="Ground control to...",
            ),
            Case(
                description="url encode",
                template=r"{{ foo | url_encode }}",
                context={"foo": "email address is bob@example.com!"},
                expect=r"email+address+is+bob%40example.com%21",
            ),
            Case(
                description="url decode",
                template=r"{{ foo | url_decode }}",
                context={"foo": r"email+address+is+bob%40example.com%21"},
                expect="email address is bob@example.com!",
            ),
            Case(
                description="size",
                template=r"{{ foo | size }}",
                context={"foo": [1, 2, 3]},
                expect="3",
            ),
            Case(
                description="default",
                template=r"{{ foo | default: 'foo' }}",
                context={"foo": None},
                expect="foo",
            ),
            Case(
                description="date",
                template=r"{{ foo | date: '%a, %b %d, %y' }}",
                context={"foo": datetime.datetime(2002, 1, 1, 11, 45, 13)},
                expect="Tue, Jan 01, 02",
            ),
            Case(
                description="abs",
                template=r"{{ foo | abs }}",
                context={"foo": -5},
                expect="5",
            ),
            Case(
                description="at most",
                template=r"{{ foo | at_most: 5 }}",
                context={"foo": 8},
                expect="5",
            ),
            Case(
                description="at least",
                template=r"{{ foo | at_least: 8 }}",
                context={"foo": 5},
                expect="8",
            ),
            Case(
                description="ceil",
                template=r"{{ foo | ceil }}",
                context={"foo": 5.4},
                expect="6",
            ),
            Case(
                description="floor",
                template=r"{{ foo | floor }}",
                context={"foo": 5.4},
                expect="5",
            ),
            Case(
                description="divided by",
                template=r"{{ foo | divided_by: 2.0 }}",
                context={"foo": 10},
                expect="5.0",
            ),
            Case(
                description="minus",
                template=r"{{ foo | minus: 2 }}",
                context={"foo": 10},
                expect="8",
            ),
            Case(
                description="plus",
                template=r"{{ foo | plus: 2 }}",
                context={"foo": 10},
                expect="12",
            ),
            Case(
                description="round",
                template=r"{{ foo | round }}",
                context={"foo": 5.6},
                expect="6",
            ),
            Case(
                description="times",
                template=r"{{ foo | times: 2 }}",
                context={"foo": 5},
                expect="10",
            ),
            Case(
                description="modulo",
                template=r"{{ foo | modulo: 7.0 }}",
                context={"foo": 10.1},
                expect="3.1",
            ),
            Case(
                description="join",
                template=r"{{ foo | join: '#' }}",
                context={"foo": ["a", "b"]},
                expect="a#b",
            ),
            Case(
                description="first",
                template=r"{{ foo | first }}",
                context={"foo": ["a", "b"]},
                expect="a",
            ),
            Case(
                description="last",
                template=r"{{ foo | last }}",
                context={"foo": ["a", "b"]},
                expect="b",
            ),
            Case(
                description="concat",
                template=r"{{ foo | concat: bar | join: '#' }}",
                context={"foo": ["a", "b"], "bar": ["c", "d"]},
                expect="a#b#c#d",
            ),
            Case(
                description="map",
                template=r"{{ foo | map: 'title' | join: '#' }}",
                context={"foo": [{"title": "foo"}, {"title": "bar"}, {"title": "baz"}]},
                expect="foo#bar#baz",
            ),
            Case(
                description="reverse",
                template=r"{{ foo | reverse | join: '#' }}",
                context={"foo": ["b", "a", "B", "A"]},
                expect="A#B#a#b",
            ),
            Case(
                description="sort",
                template=r"{{ foo | sort | join: '#' }}",
                context={"foo": ["b", "a", "C", "B", "A"]},
                expect="A#B#C#a#b",
            ),
            Case(
                description="sort natural",
                template=r"{{ foo | sort_natural | join: '#' }}",
                context={"foo": ["b", "a", "C", "B", "A"]},
                expect="a#A#b#B#C",
            ),
            Case(
                description="where",
                template=r"{{ foo | where: 'title' }}",
                context={"foo": [{"title": "foo"}, {"title": "bar"}, {"title": None}]},
                expect="{'title': 'foo'}{'title': 'bar'}",
            ),
            Case(
                description="uniq",
                template=r"{{ foo | uniq | join: '#' }}",
                context={"foo": ["a", "b", "b", "a"]},
                expect="a#b",
            ),
            Case(
                description="compact",
                template=r"{{ foo | compact | join: '#' }}",
                context={"foo": ["b", "a", None, "A"]},
                expect="b#a#A",
            ),
            Case(
                description="base64_encode",
                template=r"{{ 'one two three' | base64_encode }}",
                context={},
                expect="b25lIHR3byB0aHJlZQ==",
            ),
            Case(
                description="base64_decode",
                template=r"{{ 'b25lIHR3byB0aHJlZQ==' | base64_decode }}",
                context={},
                expect="one two three",
            ),
            Case(
                description="base64_url_safe_encode",
                template=(
                    r"{{ "
                    r"'abcdefghijklmnopqrstuvwxyz "
                    r"ABCDEFGHIJKLMNOPQRSTUVWXYZ "
                    r"1234567890 !@#$%^&*()-=_+/?.:;[]{}\|' "
                    r"| base64_url_safe_encode }}"
                ),
                context={},
                expect=(
                    "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXogQUJDREVGR0hJSktMTU5PUFFSU1"
                    "RVVldYWVogMTIzNDU2Nzg5MCAhQCMkJV4mKigpLT1fKy8_Ljo7W117fVx8"
                ),
            ),
            Case(
                description="base64_url_safe_decode",
                template=(
                    r"{{ "
                    r"'YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXogQUJDREVGR0hJSktMTU5PUFFSU1"
                    r"RVVldYWVogMTIzNDU2Nzg5MCAhQCMkJV4mKigpLT1fKy8_Ljo7W117fVx8' "
                    r"| base64_url_safe_decode }}"
                ),
                context={},
                expect=(
                    r"abcdefghijklmnopqrstuvwxyz "
                    r"ABCDEFGHIJKLMNOPQRSTUVWXYZ "
                    r"1234567890 !@#$%^&*()-=_+/?.:;[]{}\|"
                ),
            ),
        ]

        env = Environment()

        for case in test_cases:
            with self.subTest(msg=case.description):
                template = env.from_string(case.template)
                result = template.render(**case.context)
                self.assertEqual(result, case.expect)


class ExtraFilterRegistrationTestCase(unittest.TestCase):
    """Test that we can add all extra filters."""

    def test_extra_filters(self) -> None:
        """Extra filter tests."""
        test_cases = [
            Case(
                description="array index",
                template="{{ array | index: 'b' }}",
                context={"array": ["a", "b", "c"]},
                expect="1",
            ),
            Case(
                description="stylesheet tag",
                template="{{ url | stylesheet_tag }}",
                context={"url": "assets/style.css"},
                expect=(
                    '<link href="assets/style.css" rel="stylesheet" '
                    'type="text/css" media="all" />'
                ),
            ),
            Case(
                description="stylesheet tag",
                template="{{ url | script_tag }}",
                context={"url": "assets/app.js"},
                expect='<script src="assets/app.js" type="text/javascript"></script>',
            ),
            Case(
                description="JSON",
                template="{{ data | json }}",
                context={"data": {"foo": [1, 2, 3]}},
                expect='{"foo": [1, 2, 3]}',
            ),
        ]

        env = Environment()
        add_filters(env)

        for case in test_cases:
            with self.subTest(msg=case.description):
                template = env.from_string(case.template)
                result = template.render(**case.context)
                self.assertEqual(result, case.expect)
