"""Liquid render tests."""

import asyncio
import datetime
import unittest

from dataclasses import dataclass
from dataclasses import field

from typing import Mapping
from typing import Any

from liquid.environment import Environment
from liquid.template import AwareBoundTemplate
from liquid.mode import Mode
from liquid.loaders import DictLoader
from liquid.builtin.drops import IterableDrop


class MockIterableDrop(IterableDrop):
    """Mock implementation of an iterable drop."""

    def __init__(self):
        self.items = [
            {"foo": 1, "bar": 2},
            {"foo": 2, "bar": 1},
            {"foo": 3, "bar": 3},
        ]

        self.it = iter(self)

    def __contains__(self, item):
        return False

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __str__(self):
        return "MockIterableDrop"

    def step(self, item):
        return next(self.it)


TEMPLATE_DROP_ATTRS = (
    r"{{ template }} "
    r"{{ template.directory }} "
    r"{{ template.name }} "
    r"{{ template.suffix }}"
)


@dataclass
class Case:
    """Test case dataclass to help with table driven tests."""

    description: str
    template: str
    expect: str
    globals: Mapping[str, Any] = field(default_factory=dict)
    partials: Mapping[str, Any] = field(default_factory=dict)


class RenderTestCases(unittest.TestCase):
    """Test cases for testing template renders."""

    def _test(self, test_cases, template_class=AwareBoundTemplate):
        """Run all tests in `test_cases` in sync and async modes."""
        self._test_sync(test_cases, template_class)
        self._test_async(test_cases, template_class)

    def _test_sync(self, test_cases, template_class=AwareBoundTemplate):
        """Helper method for testing lists of test cases."""
        for case in test_cases:
            env = Environment(loader=DictLoader(case.partials))
            env.template_class = template_class

            template = env.from_string(case.template, globals=case.globals)

            with self.subTest(msg=case.description):
                result = template.render()
                self.assertEqual(result, case.expect)

    def _test_async(self, test_cases, template_class=AwareBoundTemplate):
        """Helper method for table driven testing of asynchronous rendering."""

        async def coro(template):
            return await template.render_async()

        for case in test_cases:
            env = Environment(loader=DictLoader(case.partials))
            env.template_class = template_class

            template = env.from_string(case.template, globals=case.globals)

            with self.subTest(msg=case.description, asynchronous=True):
                result = asyncio.run(coro(template))
                self.assertEqual(result, case.expect)

    def test_literal(self):
        """Test that we can render template literals."""

        self._test(
            [
                Case(
                    description="a literal string",
                    template="a literal string",
                    expect="a literal string",
                ),
                Case(
                    description="some css",
                    template=" div { font-weight: bold; } ",
                    expect=" div { font-weight: bold; } ",
                ),
            ]
        )

    def test_whitespace_control(self):
        """Test that we can control whitespace."""

        self._test(
            [
                Case(
                    description="mixed whitespace control",
                    template="".join(
                        [
                            "\n{% if customer -%}\n",
                            "Welcome back, {{ customer.first_name -}} !\n",
                            "{%- endif -%}",
                        ]
                    ),
                    expect="\nWelcome back, Holly!",
                    globals={"customer": {"first_name": "Holly"}},
                ),
                Case(
                    description="carriage return instead of newline",
                    template="".join(
                        [
                            "\r{% if customer -%}\r",
                            "Welcome back, {{ customer.first_name -}} !\r",
                            "{%- endif -%}",
                        ]
                    ),
                    expect="\rWelcome back, Holly!",
                    globals={"customer": {"first_name": "Holly"}},
                ),
            ]
        )

    def test_output_statement(self):
        """Test that we can render output statements."""

        self._test(
            [
                Case(
                    description="string literal",
                    template=r"{{ 'hello' }}",
                    expect="hello",
                ),
                Case(
                    description="integer literal",
                    template=r"{{ 123 }}",
                    expect="123",
                ),
                Case(
                    description="negative integer literal",
                    template=r"{{ -123 }}",
                    expect="-123",
                ),
                Case(
                    description="float literal",
                    template=r"{{ 1.23 }}",
                    expect="1.23",
                ),
                Case(
                    description="global identifier",
                    template=r"{{ product.title }}",
                    expect="foo",
                    globals={"product": {"title": "foo"}},
                ),
                Case(
                    description="local identifier",
                    template=r"{% assign name = 'Brian' %}{{ name }}",
                    expect="Brian",
                ),
                Case(
                    description="global identifier does not exist",
                    template=r"{{ age }}",
                    expect="",
                ),
                Case(
                    description="local identifier does not exist",
                    template=r"{{ age }}",
                    expect="",
                ),
                Case(
                    description="array item by index",
                    template=r"{{ product.tags[1] }}",
                    expect="garden",
                    globals={"product": {"tags": ["sports", "garden"]}},
                ),
                Case(
                    description="array item by index from identifier",
                    template="{% assign i = 1 %}{{ product.tags[i] }}",
                    expect="garden",
                    globals={"product": {"tags": ["sports", "garden"]}},
                ),
                Case(
                    description="global identifier with a filter",
                    template=r"{{ product.title | upcase }}",
                    expect="FOO",
                    globals={"product": {"title": "foo"}},
                ),
                Case(
                    description="dump an array from the global context",
                    template=r"{{ product.tags }}",
                    expect="sportsgarden",
                    globals={"product": {"tags": ["sports", "garden"]}},
                ),
                Case(
                    description="assign by value",
                    template=(
                        r"{% capture some %}hello{% endcapture %}"
                        r"{% assign other = some %}"
                        r"{% assign some = 'foo' %}"
                        r"{{ some }}-{{ other }}"
                    ),
                    expect="foo-hello",
                ),
                Case(
                    description="traverse variables with bracketed identifiers",
                    template=r"{{ site.data.menu[include.menu][include.locale] }}",
                    expect="it works!",
                    globals={
                        "site": {"data": {"menu": {"foo": {"bar": "it works!"}}}},
                        "include": {"menu": "foo", "locale": "bar"},
                    },
                ),
                Case(
                    description="special built in variable 'now'",
                    template=r"{{ now | date: '%d/%m/%Y' }}",
                    expect=datetime.datetime.now().strftime(r"%d/%m/%Y"),
                ),
                Case(
                    description="special built in variable 'today'",
                    template=r"{{ today | date: '%d/%m/%Y' }}",
                    expect=datetime.date.today().strftime(r"%d/%m/%Y"),
                ),
                Case(
                    description="default filter on false literal",
                    template=r"{{ false | default: 'bar' }}",
                    expect="bar",
                ),
                Case(
                    description="default filter allow false",
                    template=r"{{ false | default: 'bar', allow_false: true }}",
                    expect="false",
                ),
                Case(
                    description="default filter don't allow false",
                    template=r"{{ false | default: 'bar', allow_false: false }}",
                    expect="bar",
                ),
                Case(
                    description="unexpected `join` filter left value passes through",
                    template=r"{{ 12 | join: '#' }}",
                    expect="12",
                ),
                Case(
                    description="join a string",
                    template=r"{{ 'a,b' | join: '#' }}",
                    expect="a,b",
                ),
                Case(
                    description="literal output start sequence",
                    template=r"{{ '{{' }}",
                    expect=r"{{",
                ),
            ]
        )

    def test_echo_tag(self):
        """Test that we can render `echo` tags."""

        self._test(
            [
                Case(
                    description="string literal",
                    template=r"{% echo 'hello' %}",
                    expect="hello",
                ),
                Case(
                    description="integer literal",
                    template=r"{% echo 123 %}",
                    expect="123",
                ),
                Case(
                    description="float literal",
                    template=r"{% echo 1.23 %}",
                    expect="1.23",
                ),
                Case(
                    description="global identifier",
                    template=r"{% echo product.title %}",
                    expect="foo",
                    globals={"product": {"title": "foo"}},
                ),
                Case(
                    description="local identifier",
                    template=r"{% assign name = 'Brian' %}{% echo name %}",
                    expect="Brian",
                ),
                Case(
                    description="global identifier does not exist",
                    template=r"{% echo age %}",
                    expect="",
                ),
                Case(
                    description="local identifier does not exist",
                    template=r"{% echo age %}",
                    expect="",
                ),
                Case(
                    description="array item by index",
                    template=r"{% echo product.tags[1] %}",
                    expect="garden",
                    globals={"product": {"tags": ["sports", "garden"]}},
                ),
                Case(
                    description="array item by index from identifier",
                    template=r"{% assign i = 1 %}{% echo product.tags[i] %}",
                    expect="garden",
                    globals={"product": {"tags": ["sports", "garden"]}},
                ),
                Case(
                    description="global identifier with a filter",
                    template=r"{% echo product.title | upcase %}",
                    expect="FOO",
                    globals={"product": {"title": "foo"}},
                ),
                Case(
                    description="dump an array from the global context",
                    template=r"{% echo product.tags %}",
                    expect="sportsgarden",
                    globals={"product": {"tags": ["sports", "garden"]}},
                ),
                Case(
                    description="assign by value",
                    template=(
                        r"{% capture some %}hello{% endcapture %}"
                        r"{% assign other = some %}"
                        r"{% assign some = 'foo' %}"
                        r"{% echo some %}-{% echo other %}"
                    ),
                    expect="foo-hello",
                ),
                Case(
                    description="traverse variables with bracketed identifiers",
                    template=r"{% echo site.data.menu[include.menu][include.locale] %}",
                    expect="it works!",
                    globals={
                        "site": {"data": {"menu": {"foo": {"bar": "it works!"}}}},
                        "include": {"menu": "foo", "locale": "bar"},
                    },
                ),
                Case(
                    description="special built in variable 'now'",
                    template=r"{% echo now | date: '%d/%m/%Y' %}",
                    expect=datetime.datetime.now().strftime(r"%d/%m/%Y"),
                ),
                Case(
                    description="special built in variable 'today'",
                    template=r"{% echo today | date: '%d/%m/%Y' %}",
                    expect=datetime.date.today().strftime(r"%d/%m/%Y"),
                ),
                Case(
                    description="index of undefined",
                    template=r"{{ nosuchthing[0] }}",
                    expect="",
                ),
            ]
        )

    def test_assign_tag(self):
        """Test that we can render assigned variables."""
        self._test(
            [
                Case(
                    description="assing a filtered literal",
                    template="{% assign foo = 'foo' | upcase %}{{ foo }}",
                    expect="FOO",
                ),
            ]
        )

    def test_if_tag(self):
        """Test that we can render `if` tags."""
        test_cases = [
            Case(
                description="condition with literal consequence",
                template=r"{% if product.title == 'foo' %}bar{% endif %}",
                expect="bar",
                globals={"product": {"title": "foo"}},
            ),
            Case(
                description="condition with literal consequence and literal alternative",
                template=r"{% if product.title == 'hello' %}bar{% else %}baz{% endif %}",
                expect="baz",
                globals={"product": {"title": "foo"}},
            ),
            Case(
                description="condition with conditional alternative",
                template=(
                    r"{% if product.title == 'hello' %}"
                    r"foo"
                    r"{% elsif product.title == 'foo' %}"
                    r"bar"
                    r"{% endif %}"
                ),
                expect="bar",
                globals={"product": {"title": "foo"}},
            ),
            Case(
                description="condition with conditional alternative and final alternative",
                template=(
                    r"{% if product.title == 'hello' %}"
                    r"foo"
                    r"{% elsif product.title == 'goodbye' %}"
                    r"bar"
                    r"{% else %}"
                    r"baz"
                    r"{% endif %}"
                ),
                expect="baz",
                globals={"product": {"title": "foo"}},
            ),
            Case(
                description="truthy-ness of a dictionary",
                template=r"{% if product %}bar{% else %}foo{% endif %}",
                expect="bar",
                globals={"product": {"title": "foo"}},
            ),
            Case(
                description="falsey-ness of a literal nil",
                template=r"{% if nil %}bar{% else %}foo{% endif %}",
                expect="foo",
            ),
            Case(
                description="falsey-ness of a non existant name",
                template=r"{% if nosuchthing %}bar{% else %}foo{% endif %}",
                expect="foo",
            ),
            Case(
                description="nested condition in the consequence block",
                template=r"{% if product %}{% if title == 'Hello' %}baz{% endif %}{% endif %}",
                expect="baz",
                globals={
                    "product": {"title": "foo"},
                    "title": "Hello",
                },
            ),
            Case(
                description="nested condition, alternative in the consequence block",
                template=(
                    r"{% if product %}"
                    r"{% if title == 'goodbye' %}"
                    r"baz"
                    r"{% else %}"
                    r"hello"
                    r"{% endif %}"
                    r"{% endif %}"
                ),
                expect="hello",
                globals={"product": {"title": "foo"}, "title": "Hello"},
            ),
            Case(
                description="false",
                template=r"{% if false %}{% endif %}",
                expect="",
            ),
            Case(
                description="contains condition",
                template=r"{% if product.tags contains 'garden' %}baz{% endif %}",
                expect="baz",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            Case(
                description="not equal condition",
                template=r"{% if product.title != 'foo' %}baz{% endif %}",
                expect="",
                globals={"product": {"title": "foo"}},
            ),
            Case(
                description="alternate not equal condition",
                template=r"{% if product.title <> 'foo' %}baz{% endif %}",
                expect="",
                globals={"product": {"title": "foo"}},
            ),
            Case(
                description="blank empty 'if'",
                template=r"{% if true %}  {% elsif false %} {% else %} {% endif %}",
                expect="",
            ),
            Case(
                description="blank nested block",
                template=r"{% if true %} {% comment %} this is blank {% endcomment %} {% endif %}",
                expect="",
            ),
            Case(
                description="compare to blank",
                template=r"{% if username == blank %}username is blank{% endif %}",
                expect="username is blank",
                globals={"username": ""},
            ),
        ]

        self._test(test_cases)

    def test_comment_tag(self):
        """Test that we can render comment tags."""

        self._test(
            [
                Case(
                    description="simple comment",
                    template=r"{% comment %}foo{% endcomment %}",
                    expect="",
                ),
                Case(
                    description="comment with tags",
                    template=(
                        r"{% comment %}"
                        r"{% if true %}"
                        r"{{ title }}"
                        r"{% endif %}"
                        r"{% endcomment %}"
                    ),
                    expect="",
                ),
            ]
        )

    def test_unless_tag(self):
        """Test that we can render `unless` tags."""

        test_cases = [
            Case(
                description="false",
                template=r"{% unless false %}foo{% endunless %}",
                expect="foo",
            ),
            Case(
                description="true",
                template=r"{% unless true %}foo{% endunless %}",
                expect="",
            ),
            Case(
                description="blank empty block",
                template=r"{% unless false %}  {% endunless %}",
                expect="",
            ),
        ]

        self._test(test_cases)

    def test_capture_tag(self):
        """Test that we can render `capture` tags."""

        test_cases = [
            Case(
                description="literal and global variable",
                template=(
                    r"{% capture greeting %}"
                    r"Hello, {{ customer.first_name }}."
                    r"{% endcapture %}"
                    r"{{ greeting }}"
                ),
                expect="Hello, Holly.",
                globals={"customer": {"first_name": "Holly"}},
            ),
            Case(
                description="hyphen in variable name",
                template=(
                    r"{% capture this-thing %}"
                    r"Hello, {{ customer.first_name }}."
                    r"{% endcapture %}"
                    r"{{ this-thing }}"
                ),
                expect="Hello, Holly.",
                globals={"customer": {"first_name": "Holly"}},
            ),
            Case(
                description="assign from capture",
                template=(
                    r"{% capture some %}"
                    r"hello"
                    r"{% endcapture %}"
                    r"{% assign other = some %}"
                    r"{{ some }}-{{ other }}"
                ),
                expect="hello-hello",
            ),
        ]

        self._test(test_cases)

    def test_case_tag(self):
        """Test that we can render `case` tags."""

        test_cases = [
            Case(
                description="simple case",
                template=(
                    r"{% case title %}"
                    r"{% when 'foo' %}foo"
                    r"{% when 'Hello' %}bar"
                    r"{% endcase %}"
                ),
                expect="bar",
                globals={"title": "Hello"},
            ),
            Case(
                description="identifier 'when' expression ",
                template=(
                    r"{% case title %}"
                    r"{% when other %}foo"
                    r"{% when 'Hello' %}bar"
                    r"{% endcase %}"
                ),
                expect="foo",
                globals={"title": "Hello", "other": "Hello"},
            ),
            Case(
                description="out of scope identifier 'when' expression ",
                template=(
                    r"{% case title %}"
                    r"{% when nosuchthing %}foo"
                    r"{% when 'Hello' %}bar"
                    r"{% endcase %}"
                ),
                expect="bar",
                globals={"title": "Hello"},
            ),
            Case(
                description="name not in scope",
                template=(
                    r"{% case nosuchthing %}"
                    r"{% when 'foo' %}foo"
                    r"{% when 'bar' %}bar"
                    r"{% endcase %}"
                ),
                expect="",
            ),
            Case(
                description="no match and no default",
                template=(
                    r"{% case title %}"
                    r"{% when 'foo' %}foo"
                    r"{% when 'bar' %}bar"
                    r"{% endcase %}"
                ),
                expect="",
                globals={"title": "Hello"},
            ),
            Case(
                description="with default",
                template=(
                    r"{% case title %}"
                    r"{% when 'foo' %}foo"
                    r"{% else %}bar"
                    r"{% endcase %}"
                ),
                expect="bar",
                globals={"title": "Hello"},
            ),
            Case(
                description="no whens",
                template=r"{% case title %}{% else %}bar{% endcase %}",
                expect="bar",
                globals={"title": "Hello"},
            ),
            Case(
                description="no whens or default",
                template=r"{% case title %}{% endcase %}",
                expect="",
                globals={"title": "Hello"},
            ),
            Case(
                description="whitespace",
                template=(
                    "{% case title %}  \n\t"
                    "{% when 'foo' %}foo\n"
                    "{% when 'Hello' %}bar"
                    "{% endcase %}"
                ),
                expect="bar",
                globals={"title": "Hello"},
            ),
        ]

        self._test(test_cases)

    def test_cycle_tag(self):
        """Test that we can render `cycle` tags."""

        test_cases = [
            Case(
                description="no identifier",
                template=(
                    r"{% cycle 'some', 'other' %}"
                    r"{% cycle 'some', 'other' %}"
                    r"{% cycle 'some', 'other' %}"
                ),
                expect="someothersome",
            ),
            Case(
                description="with identifier",
                template=(
                    r"{% cycle 'foo': 'some', 'other' %}"
                    r"{% cycle 'some', 'other' %}"
                    r"{% cycle 'foo': 'some', 'other' %}"
                ),
                expect="somesomeother",
            ),
            Case(
                description="different items",
                template=(
                    r"{% cycle '1', '2', '3' %}"
                    r"{% cycle '1', '2' %}"
                    r"{% cycle '1', '2', '3' %}"
                ),
                expect="112",
            ),
            Case(
                description="integers",
                template=(r"{% cycle 1, 2, 3 %}{% cycle 1, 2, 3 %}{% cycle 1, 2, 3 %}"),
                expect="123",
            ),
        ]

        self._test(test_cases)

    def test_decrement_tag(self):
        """Test that we can render `decrement` tags."""

        test_cases = [
            Case(
                description="named counter",
                template=r"{% decrement foo %}{{ foo }} {% decrement foo %}{{ foo }}",
                expect="-1 -2",
            ),
            Case(
                description="increment and decrement named counter",
                template=r"{% decrement foo %} {% decrement foo %} {% increment foo %}",
                expect="-1 -2 -1",
            ),
        ]

        self._test(test_cases)

    def test_increment_tag(self):
        """Test that we can render `increment` tags."""

        test_cases = [
            Case(
                description="named counter",
                template=r"{% increment foo %} {% increment foo %} {% increment foo %}",
                expect="0 1 2",
            ),
            Case(
                description="multiple named counters",
                template=(
                    r"{% increment foo %} "
                    r"{% increment bar %} "
                    r"{% increment foo %} "
                    r"{% increment bar %}"
                ),
                expect="0 0 1 1",
            ),
            Case(
                description="assign and increment",
                template=(
                    r"{% assign foo = 5 %}"
                    r"{{ foo }} "
                    r"{% increment foo %} "
                    r"{% increment foo %} "
                    r"{{ foo }}"
                ),
                expect="5 0 1 5",
            ),
        ]

        self._test(test_cases)

    def test_for_tag(self):
        """Test that we can render `for` tags."""

        test_cases = [
            Case(
                description="simple range loop",
                template=r"{% for i in (0..3) %}{{ i }} {% endfor %}",
                expect="0 1 2 3 ",
            ),
            Case(
                description="range loop using identifier",
                template=(
                    r"{% for i in (0..product.end_range) %}"
                    r"{{ i }} - {{ product.tags[i] }} "
                    r"{% endfor %}"
                ),
                expect="0 - sports 1 - garden ",
                globals={"product": {"tags": ["sports", "garden"], "end_range": 1}},
            ),
            Case(
                description="simple array loop",
                template=r"{% for tag in product.tags %}{{ tag }} {% endfor %}",
                expect="sports garden ",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            Case(
                description="simple hash loop",
                template=r"{% for c in collection %}{{ c[0] }} {{ c[1] }} {% endfor %}",
                expect="title foo description bar ",
                globals={"collection": {"title": "foo", "description": "bar"}},
            ),
            Case(
                description="empty array with default",
                template=(
                    r"{% for img in emptythings.array %}"
                    r"{{ img.url }} "
                    r"{% else %}"
                    r"no images"
                    r"{% endfor %}"
                ),
                expect="no images",
                globals={"emptythings": {"array": [], "map": {}, "string": ""}},
            ),
            Case(
                description="break",
                template=(
                    r"{% for tag in product.tags %}"
                    r"{% if tag == 'sports' %}"
                    r"{% break %}"
                    r"{% else %}"
                    r"{{ tag }} "
                    r"{% endif %}"
                    r"{% else %}"
                    r"no images"
                    r"{% endfor %}"
                ),
                expect="",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            Case(
                description="continue",
                template=(
                    r"{% for tag in product.tags %}"
                    r"{% if tag == 'sports' %}"
                    r"{% continue %}"
                    r"{% else %}"
                    r"{{ tag }} "
                    r"{% endif %}"
                    r"{% else %}"
                    r"no images"
                    r"{% endfor %}"
                ),
                expect="garden ",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            Case(
                description="limit",
                template=r"{% for tag in product.tags limit:1 %}{{ tag }} {% endfor %}",
                expect="sports ",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            Case(
                description="offset",
                template=r"{% for tag in product.tags offset:1 %}{{ tag }} {% endfor %}",
                expect="garden ",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            Case(
                description="forloop length",
                template=r"{% for tag in product.tags %}{{ forloop.length }} {% endfor %}",
                expect="2 2 ",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            Case(
                description="forloop length with limit",
                template=r"{% for tag in product.tags limit:3 %}{{ forloop.length }} {% endfor %}",
                expect="3 3 3 ",
                globals={
                    "product": {
                        "tags": [
                            "sports",
                            "garden",
                            "sports",
                            "garden",
                            "sports",
                            "garden",
                        ]
                    }
                },
            ),
            Case(
                description="forloop length with offset",
                template=r"{% for tag in product.tags offset:3 %}{{ forloop.length }} {% endfor %}",
                expect="3 3 3 ",
                globals={
                    "product": {
                        "tags": [
                            "sports",
                            "garden",
                            "sports",
                            "garden",
                            "sports",
                            "garden",
                        ]
                    }
                },
            ),
            Case(
                description="forloop goes out of scope",
                template=(
                    r"{% for tag in product.tags %}"
                    r"{{ forloop.length }} "
                    r"{% endfor %}"
                    r"{{ forloop.length }}"
                ),
                expect="2 2 ",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            Case(
                description="forloop.first",
                template=r"{% for tag in product.tags %}{{ forloop.first }} {% endfor %}",
                expect="true false ",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            Case(
                description="forloop.last",
                template=r"{% for tag in product.tags %}{{ forloop.last }} {% endfor %}",
                expect="false true ",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            Case(
                description="forloop.index",
                template=r"{% for tag in product.tags %}{{ forloop.index }} {% endfor %}",
                expect="1 2 ",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            Case(
                description="forloop.index0",
                template=r"{% for tag in product.tags %}{{ forloop.index0 }} {% endfor %}",
                expect="0 1 ",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            Case(
                description="forloop.rindex",
                template=r"{% for tag in product.tags %}{{ forloop.rindex }} {% endfor %}",
                expect="2 1 ",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            Case(
                description="forloop.rindex0",
                template=r"{% for tag in product.tags %}{{ forloop.rindex0 }} {% endfor %}",
                expect="1 0 ",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            Case(
                description="forloop no such attribute",
                template=r"{% for tag in product.tags %}{{ forloop.nosuchthing }}{% endfor %}",
                expect="",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            Case(
                description="iterate an empty array",
                template=r"{% for item in emptythings.array %}{{ item }}{% endfor %}",
                expect="",
                globals={"emptythings": {"array": [], "map": {}, "string": ""}},
            ),
            Case(
                description="iterate an empty array with default",
                template=r"{% for item in emptythings.array %}{{ item }}{% else %}foo{% endfor %}",
                expect="foo",
                globals={"emptythings": {"array": [], "map": {}, "string": ""}},
            ),
            Case(
                description="lookup a filter from an outer context",
                template=r"{% for tag in product.tags %}{{ tag | upcase }} {% endfor %}",
                expect="SPORTS GARDEN ",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            Case(
                description="assign inside loop",
                template=r"{% for tag in product.tags %}{% assign x = tag %}{% endfor %}{{ x }}",
                expect="garden",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            Case(
                description="blank empty loops",
                template=r"{% for i in (0..10) %}  {% endfor %}",
                expect="",
            ),
            Case(
                description=(
                    "loop over nested and chained object from context "
                    "with trailing identifier"
                ),
                template=r"{% for link in linklists[section.settings.menu].links %}{{ link }} {% endfor %}",
                expect="1 2 ",
                globals={
                    "linklists": {"main": {"links": ["1", "2"]}},
                    "section": {"settings": {"menu": "main"}},
                },
            ),
            Case(
                description="loop over undefined",
                template=r"{% for tag in nosuchthing %}{{ tag }}{% endfor %}",
                expect="",
                globals={},
            ),
            Case(
                description="continue a loop",
                template=(
                    r"{% for item in array limit: 3 %}"
                    r"{{ item }} "
                    r"{% endfor %}"
                    r"{% for item in array offset: continue %}"
                    r"{{ item }} "
                    r"{% endfor %}"
                ),
                expect="1 2 3 4 5 6 ",
                globals={"array": [1, 2, 3, 4, 5, 6]},
            ),
            Case(
                description="continue a loop over a changing array",
                template=(
                    r"{% assign foo = '1,2,3,4,5,6' | split: ',' %}"
                    r"{% for item in foo limit: 3 %}"
                    r"{{ item }} "
                    r"{% endfor %}"
                    r"{% assign foo = 'u,v,w,x,y,z' | split: ',' %}"
                    r"{% for item in foo offset: continue %}"
                    r"{{ item }} "
                    r"{% endfor %}"
                ),
                expect="1 2 3 x y z ",
                globals={},
            ),
            Case(
                description="continue with changing loop var",
                template=(
                    r"{% for foo in array limit: 3 %}"
                    r"{{ foo }} "
                    r"{% endfor %}"
                    r"{% for bar in array offset: continue %}"
                    r"{{ bar }} "
                    r"{% endfor %}"
                ),
                expect="1 2 3 1 2 3 4 5 6 ",
                globals={"array": [1, 2, 3, 4, 5, 6]},
            ),
            Case(
                description="nothing to continue from",
                template=(
                    r"{% for item in array %}"
                    r"{{ item }} "
                    r"{% endfor %}"
                    r"{% for item in array offset: continue %}"
                    r"{{ item }} "
                    r"{% endfor %}"
                ),
                expect="1 2 3 4 5 6 ",
                globals={"array": [1, 2, 3, 4, 5, 6]},
            ),
            Case(
                description="continue from a limit that is greater than length",
                template=(
                    r"{% for item in array limit: 99 %}"
                    r"{{ item }} "
                    r"{% endfor %}"
                    r"{% for item in array offset: continue %}"
                    r"{{ item }} "
                    r"{% endfor %}"
                ),
                expect="1 2 3 4 5 6 ",
                globals={"array": [1, 2, 3, 4, 5, 6]},
            ),
            Case(
                description="continue from a range expression",
                template=(
                    r"{% for item in (1..6) limit: 3 %}"
                    r"{{ item }} "
                    r"{% endfor %}"
                    r"{% for item in (1..6) offset: continue %}"
                    r"{{ item }} "
                    r"{% endfor %}"
                ),
                expect="1 2 3 4 5 6 ",
                globals={"array": [1, 2, 3, 4, 5, 6]},
            ),
        ]

        self._test(test_cases)

    def test_raw_tag(self):
        """Test that we can render `raw` tags."""

        test_cases = [
            Case(
                description="literal",
                template=r"{% raw %}foo{% endraw %}",
                expect="foo",
            ),
            Case(
                description="statement",
                template=r"{% raw %}{{ foo }}{% endraw %}",
                expect=r"{{ foo }}",
            ),
            Case(
                description="tag",
                template=r"{% raw %}{% assign x = 1 %}{% endraw %}",
                expect=r"{% assign x = 1 %}",
            ),
            Case(
                description="partial tag",
                template=r"{% raw %} %} {% }} {{ {% endraw %}",
                expect=r" %} {% }} {{ ",
            ),
            Case(
                description="continue after raw",
                template=r"{% raw %} {% some raw content %} {% endraw %}a literal",
                expect=r" {% some raw content %} a literal",
            ),
        ]

        self._test(test_cases)

    def test_tablerow_tag(self):
        """Test that we can render `tablerow` tags."""

        test_cases = [
            Case(
                description="one row",
                template=(
                    r"{% tablerow tag in collection.tags %}"
                    r"{{ tag }}"
                    r"{% endtablerow %}"
                ),
                expect=(
                    '<tr class="row1">'
                    '<td class="col1">tag1</td>'
                    '<td class="col2">tag2</td>'
                    '<td class="col3">tag3</td>'
                    '<td class="col4">tag4</td>'
                    "</tr>"
                ),
                globals={
                    "collection": {
                        "tags": [
                            "tag1",
                            "tag2",
                            "tag3",
                            "tag4",
                        ]
                    }
                },
            ),
            Case(
                description="one row with limit",
                template=(
                    r"{% tablerow tag in collection.tags limit: 2 %}"
                    r"{{ tag }}"
                    r"{% endtablerow %}"
                ),
                expect=(
                    '<tr class="row1">'
                    '<td class="col1">tag1</td>'
                    '<td class="col2">tag2</td>'
                    "</tr>"
                ),
                globals={
                    "collection": {
                        "tags": [
                            "tag1",
                            "tag2",
                            "tag3",
                            "tag4",
                        ]
                    }
                },
            ),
            Case(
                description="one row with offset",
                template=(
                    r"{% tablerow tag in collection.tags offset: 2 %}"
                    r"{{ tag }}"
                    r"{% endtablerow %}"
                ),
                expect=(
                    '<tr class="row1">'
                    '<td class="col1">tag3</td>'
                    '<td class="col2">tag4</td>'
                    "</tr>"
                ),
                globals={
                    "collection": {
                        "tags": [
                            "tag1",
                            "tag2",
                            "tag3",
                            "tag4",
                        ]
                    }
                },
            ),
            Case(
                description="two columns",
                template=(
                    r"{% tablerow tag in collection.tags cols:2 %}"
                    r"{{ tag }}"
                    r"{% endtablerow %}"
                ),
                expect=(
                    '<tr class="row1">'
                    '<td class="col1">tag1</td>'
                    '<td class="col2">tag2</td>'
                    "</tr>"
                    '<tr class="row2">'
                    '<td class="col1">tag3</td>'
                    '<td class="col2">tag4</td>'
                    "</tr>"
                ),
                globals={
                    "collection": {
                        "tags": [
                            "tag1",
                            "tag2",
                            "tag3",
                            "tag4",
                        ]
                    }
                },
            ),
            Case(
                description="two column range",
                template=(
                    r"{% tablerow i in (1..4) cols:2 %}"
                    r"{{ i }} {{ tablerowloop.col_first }}"
                    r"{% endtablerow %}"
                ),
                expect=(
                    '<tr class="row1">'
                    '<td class="col1">1 true</td>'
                    '<td class="col2">2 false</td>'
                    "</tr>"
                    '<tr class="row2">'
                    '<td class="col1">3 true</td>'
                    '<td class="col2">4 false</td>'
                    "</tr>"
                ),
            ),
            Case(
                description="two column odd range",
                template=(
                    r"{% tablerow i in (1..5) cols:2 %}"
                    r"{{ i }} {{ tablerowloop.col_first }}"
                    r"{% endtablerow %}"
                ),
                expect=(
                    '<tr class="row1">'
                    '<td class="col1">1 true</td>'
                    '<td class="col2">2 false</td>'
                    "</tr>"
                    '<tr class="row2">'
                    '<td class="col1">3 true</td>'
                    '<td class="col2">4 false</td>'
                    "</tr>"
                    '<tr class="row3">'
                    '<td class="col1">5 true</td>'
                    "</tr>"
                ),
            ),
        ]

        self._test(test_cases)

    def test_liquid_tag(self):
        """Test that we can render `liquid` tags."""

        test_cases = [
            Case(
                description="multiple tags",
                template="\n".join(
                    [
                        r"{% liquid",
                        r"if product.title",
                        r"   echo product.title | upcase",
                        r"else",
                        r"   echo 'product-1' | upcase ",
                        r"endif",
                        r"",
                        r"for i in (0..5)",
                        r"   echo i",
                        r"endfor %}",
                    ]
                ),
                expect="FOO012345",
                globals={"product": {"title": "foo"}},
            ),
        ]

        self._test(test_cases)

    def test_illegal(self):
        """Test that we can render an `illegal` token in LAX mode."""
        env = Environment(tolerance=Mode.LAX)
        template = env.from_string(r"{% nosuchthing %}")
        result = template.render()
        self.assertEqual(result, "")

    def test_include_tag(self):
        """Test that we can render `include` tags."""

        test_cases = [
            Case(
                description="string literal name",
                template=r"{% include 'product-hero' %}{{ partial }}",
                expect="foo\n- sports\n- garden\ntruefalse",
                globals={"product": {"title": "foo", "tags": ["sports", "garden"]}},
                partials={
                    "product-hero": (
                        r"{{ product.title }}"
                        "\n"
                        r"{% for tag in product.tags %}"
                        r"- {{ tag }}"
                        "\n"
                        r"{% endfor %}"
                        r"{{ partial }}"
                    ),
                },
            ),
            Case(
                description="name from identifier",
                template=r"{% include snippet %}",
                expect="foo\n- sports\n- garden\ntrue",
                globals={
                    "snippet": "product-hero",
                    "product": {"title": "foo", "tags": ["sports", "garden"]},
                },
                partials={
                    "product-hero": (
                        r"{{ product.title }}"
                        "\n"
                        r"{% for tag in product.tags %}"
                        r"- {{ tag }}"
                        "\n"
                        r"{% endfor %}"
                        r"{{ partial }}"
                    ),
                },
            ),
            Case(
                description="bound variable",
                template=r"{% include 'product-title' with collection.products[1] %}",
                expect="car",
                globals={
                    "collection": {
                        "products": [{"title": "bike"}, {"title": "car"}],
                    }
                },
                partials={
                    "product-title": r"{{ product-title.title }}",
                },
            ),
            Case(
                description="bound variable does not exist",
                template=r"{% include 'product-title' with no.such.thing %}",
                expect="",
                partials={
                    "product-title": r"{{ product-title.title }}",
                },
            ),
            Case(
                description="bound array variable",
                template=r"{% include 'prod' for collection.products %}",
                expect="bikecar",
                globals={
                    "collection": {
                        "products": [{"title": "bike"}, {"title": "car"}],
                    }
                },
                partials={"prod": r"{{ prod.title }}"},
            ),
            Case(
                description="bound variable with alias",
                template=r"{% include 'product-alias' with collection.products[1] as product %}",
                expect="car",
                globals={
                    "collection": {
                        "products": [{"title": "bike"}, {"title": "car"}],
                    }
                },
                partials={"product-alias": r"{{ product.title }}"},
            ),
            Case(
                description="some keyword arguments",
                template=r"{% include 'product-args', foo: 'hello', bar: 'there' %}",
                expect="hello there",
                partials={"product-args": r"{{ foo }} {{ bar }}"},
            ),
            Case(
                description="some keyword arguments without leading comma",
                template=r"{% include 'product-args' foo: 'hello', bar: 'there' %}",
                expect="hello there",
                partials={"product-args": r"{{ foo }} {{ bar }}"},
            ),
            Case(
                description="template drop",
                template=r"{% include 'some/template-attrs.alt.txt' %}",
                expect="template-attrs.alt some template-attrs alt",
                partials={"some/template-attrs.alt.txt": TEMPLATE_DROP_ATTRS},
            ),
            Case(
                description="template drop no parent",
                template=r"{% include 'template-attrs.alt.txt' %}",
                expect="template-attrs.alt  template-attrs alt",
                partials={"template-attrs.alt.txt": TEMPLATE_DROP_ATTRS},
            ),
            Case(
                description="template drop no suffix",
                template=r"{% include 'some/template-attrs.txt' %}",
                expect="template-attrs some template-attrs ",
                partials={"some/template-attrs.txt": TEMPLATE_DROP_ATTRS},
            ),
            Case(
                description="template drop no suffix or extension",
                template=r"{% include 'some/template-attrs' %}",
                expect="template-attrs some template-attrs ",
                partials={"some/template-attrs": TEMPLATE_DROP_ATTRS},
            ),
            Case(
                description="use globals from outer scope",
                template=r"{% include 'outer-scope' %}",
                expect="Hello, Holly",
                globals={"customer": {"first_name": "Holly"}},
                partials={"outer-scope": r"Hello, {{ customer.first_name }}"},
            ),
            Case(
                description="assign persists in outer scope",
                template=r"{% include 'assign-outer-scope' %} {{ last_name }}",
                expect="Hello, Holly Smith",
                globals={"customer": {"first_name": "Holly"}},
                partials={
                    "assign-outer-scope": (
                        r"Hello, {{ customer.first_name }}"
                        r"{% assign last_name = 'Smith' %}"
                    ),
                },
            ),
            Case(
                description="counter from outer scope",
                template=(
                    r"{% increment foo %} "
                    r"{% include 'increment-outer-scope' %} "
                    r"{% increment foo %}"
                ),
                expect="0 1 2",
                partials={"increment-outer-scope": r"{% increment foo %}"},
            ),
            Case(
                description="break from include",
                template=r"{% for tag in product.tags %}{% include 'tag-break' %}{% endfor %}",
                expect="SPORTS",
                globals={"product": {"tags": ["sports", "garden"]}},
                partials={"tag-break": r"{{ tag | upcase }}{% break %}"},
            ),
            Case(
                description="break from nested include",
                template=r"{% for tag in product.tags %}{% include 'tag' %}{% endfor %}",
                expect="SPORTS break!",
                globals={"product": {"tags": ["sports", "garden"]}},
                partials={
                    "tag": r"{{ tag | upcase }}{% include 'break' %}",
                    "break": r" break!{% break %}",
                },
            ),
        ]

        self._test(test_cases)

    def test_render_tag(self):
        """Test that we can render `render` tags."""

        test_cases = [
            Case(
                description="string literal name",
                template=r"{% render 'product-hero' %}{{ partial }}",
                expect="foo\n- sports - garden \ntruefalse",
                globals={"product": {"title": "foo", "tags": ["sports", "garden"]}},
                partials={
                    "product-hero": "\n".join(
                        [
                            r"{{ product.title }}",
                            r"{% for tag in product.tags %}- {{ tag }} {% endfor %}",
                            r"{{ partial }}",
                        ]
                    ),
                },
            ),
            Case(
                description="bound variable",
                template=r"{% render 'product-title' with collection.products[1] %}",
                expect="car",
                globals={
                    "collection": {"products": [{"title": "bike"}, {"title": "car"}]}
                },
                partials={"product-title": r"{{ product-title.title }}"},
            ),
            Case(
                description="bound variable does not exist",
                template=r"{% render 'product-title' with no.such.thing %}",
                expect="",
                globals={},
                partials={"product-title": r"{{ product-title.title }}"},
            ),
            Case(
                description="bound array variable",
                template=r"{% render 'prod' for collection.products %}",
                expect="bikecar",
                globals={
                    "collection": {"products": [{"title": "bike"}, {"title": "car"}]}
                },
                partials={"prod": r"{{ prod.title }}"},
            ),
            Case(
                description="bound variable with alias",
                template=r"{% render 'product-alias' with collection.products[1] as product %}",
                expect="car",
                globals={
                    "collection": {"products": [{"title": "bike"}, {"title": "car"}]}
                },
                partials={
                    "product-alias": r"{{ product.title }}",
                },
            ),
            Case(
                description="some keyword arguments",
                template=r"{% render 'product-args', foo: 'hello', bar: 'there' %}",
                expect="hello there",
                globals={},
                partials={
                    "product-args": r"{{ foo }} {{ bar }}",
                },
            ),
            Case(
                description="some keyword arguments no leading coma",
                template=r"{% render 'product-args' foo: 'hello', bar: 'there' %}",
                expect="hello there",
                globals={},
                partials={"product-args": r"{{ foo }} {{ bar }}"},
            ),
            Case(
                description="template drop",
                template=r"{% render 'some/template-attrs.alt.txt' %}",
                expect="template-attrs.alt some template-attrs alt",
                globals={},
                partials={"some/template-attrs.alt.txt": TEMPLATE_DROP_ATTRS},
            ),
            Case(
                description="template drop no parent",
                template=r"{% render 'template-attrs.alt.txt' %}",
                expect="template-attrs.alt  template-attrs alt",
                globals={},
                partials={"template-attrs.alt.txt": TEMPLATE_DROP_ATTRS},
            ),
            Case(
                description="template drop no suffix",
                template=r"{% render 'some/template-attrs.txt' %}",
                expect="template-attrs some template-attrs ",
                globals={},
                partials={"some/template-attrs.txt": TEMPLATE_DROP_ATTRS},
            ),
            Case(
                description="template drop no suffix or extension",
                template=r"{% render 'some/template-attrs' %}",
                expect="template-attrs some template-attrs ",
                globals={},
                partials={"some/template-attrs": TEMPLATE_DROP_ATTRS},
            ),
            Case(
                description="parent variables go out of scope",
                template=(
                    r"{% assign greeting = 'good morning' %}"
                    r"{{ greeting }} "
                    r"{% render 'outer-scope' %}"
                    r"{{ greeting }}"
                ),
                expect="good morning good morning",
                partials={"outer-scope": r"{{ greeting }}"},
            ),
            Case(
                description="for loop variables go out of scope",
                template=(
                    r"{% for i in (1..3) %}"
                    r"{{ i }}"
                    r"{% render 'loop-scope' %}"
                    r"{{ i }}"
                    r"{% endfor %}"
                    r"{{ i }}"
                ),
                expect="112233",
                partials={"loop-scope": r"{{ i }}"},
            ),
            Case(
                description="assigned variables to not leek into outer scope",
                template=r"{% render 'assign-outer-scope' %} {{ last_name }}",
                expect="Hello, Holly ",
                globals={"customer": {"first_name": "Holly"}},
                partials={
                    "assign-outer-scope": (
                        r"Hello, {{ customer.first_name }}"
                        r"{% assign last_name = 'Smith' %}"
                    )
                },
            ),
            Case(
                description="increment is isolated between renders",
                template=(
                    r"{% increment foo %} "
                    r"{% render 'increment' %} "
                    r"{% increment foo %}"
                ),
                expect="0 0 1",
                partials={"increment": r"{% increment foo %}"},
            ),
            Case(
                description="decrement is isolated between renders",
                template=(
                    r"{% decrement foo %} "
                    r"{% render 'decrement' %} "
                    r"{% decrement foo %}"
                ),
                expect="-1 -1 -2",
                partials={"decrement": r"{% decrement foo %}"},
            ),
            Case(
                description="forloop helper",
                template=r"{% render 'product' for collection.products %}",
                expect="Product: bike first index:1 Product: car last index:2 ",
                globals={
                    "collection": {"products": [{"title": "bike"}, {"title": "car"}]}
                },
                partials={
                    "product": (
                        r"Product: {{ product.title }} "
                        r"{% if forloop.first %}first{% endif %}"
                        r"{% if forloop.last %}last{% endif %}"
                        r" index:{{ forloop.index }} "
                    ),
                },
            ),
            Case(
                description="for drop",
                template=r"{% render 'loop-for' for loop as value %}",
                expect="123",
                globals={"loop": MockIterableDrop()},
                partials={
                    "loop-for": r"{{ value.foo }}",
                },
            ),
            Case(
                description="with drop",
                template=r"{% render 'loop-with' with loop as value %}",
                expect="MockIterableDrop",
                globals={"loop": MockIterableDrop()},
                partials={"loop-with": r"{{ value }}"},
            ),
        ]

        self._test(test_cases)

    def test_ifchanged_tag(self):
        """Test that we can render `ifchanged` tags."""

        test_cases = [
            Case(
                description="changed from initial state",
                template=r"{% ifchanged %}hello{% endifchanged %}",
                expect="hello",
            ),
            Case(
                description="not changed from initial state",
                template=r"{% ifchanged %}{% endifchanged %}",
                expect="",
            ),
            Case(
                description="no change from assign",
                template=(
                    r"{% assign foo = 'hello' %}"
                    r"{% ifchanged %}{{ foo }}{% endifchanged %}"
                    r"{% ifchanged %}{{ foo }}{% endifchanged %}"
                ),
                expect="hello",
            ),
            Case(
                description="no change from assign",
                template=(
                    r"{% assign foo = 'hello' %}"
                    r"{% ifchanged %}{{ foo }}{% endifchanged %}"
                    r"{% ifchanged %}{{ foo }}{% endifchanged %}"
                    r"{% assign foo = 'goodbye' %}"
                    r"{% ifchanged %}{{ foo }}{% endifchanged %}"
                ),
                expect="hellogoodbye",
            ),
            Case(
                description="within for loop",
                template=(
                    r'{% assign list = "1,3,2,1,3,1,2" | split: "," | sort %}'
                    r"{% for item in list -%}"
                    r"{%- ifchanged %} {{ item }}{% endifchanged -%}"
                    r"{%- endfor %}"
                ),
                expect=" 1 2 3",
            ),
        ]

        self._test(test_cases)
