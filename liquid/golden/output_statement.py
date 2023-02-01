"""Golden tests cases for testing liquid output statements."""

import datetime
from liquid.golden.case import Case

cases = [
    Case(
        description="render a string literal",
        template=r"{{ 'hello' }}",
        expect="hello",
    ),
    Case(
        description="render an integer literal",
        template=r"{{ 123 }}",
        expect="123",
    ),
    Case(
        description="render a negative integer literal",
        template=r"{{ -123 }}",
        expect="-123",
    ),
    Case(
        description="render a float literal",
        template=r"{{ 1.23 }}",
        expect="1.23",
    ),
    Case(
        description="render nil",
        template=r"{{ nil }}",
        expect="",
    ),
    Case(
        description="render a variable from the global namespace",
        template=r"{{ product.title }}",
        expect="foo",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="render a variable from the local namespace",
        template=r"{% assign name = 'Brian' %}{{ name }}",
        expect="Brian",
    ),
    Case(
        description="render an undefined variable",
        template=r"{{ age }}",
        expect="",
    ),
    Case(
        description="render an undefined property",
        template=r"{{ product.age }}",
        expect="",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="access an array item by index",
        template=r"{{ product.tags[1] }}",
        expect="garden",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="access an array item by negative index",
        template=r"{{ product.tags[-2] }}",
        expect="sports",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="access array item by index stored in a local variable",
        template="{% assign i = 1 %}{{ product.tags[i] }}",
        expect="garden",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="render a global variable with a filter",
        template=r"{{ product.title | upcase }}",
        expect="FOO",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="dump an array from the global context",
        template=r"{{ product.tags | join: '#' }}",
        expect="sports#garden",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="assign a variable the value of an existing variable",
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
        description="render the special built in variable 'now'",
        template=r"{{ now | date: '%d/%m/%Y' }}",
        expect=datetime.datetime.now().strftime(r"%d/%m/%Y"),
        standard=False,
    ),
    Case(
        description="render the special built in variable 'today'",
        template=r"{{ today | date: '%d/%m/%Y' }}",
        expect=datetime.date.today().strftime(r"%d/%m/%Y"),
        standard=False,
    ),
    Case(
        description="render a default given a literal false",
        template=r"{{ false | default: 'bar' }}",
        expect="bar",
    ),
    Case(
        description=(
            "render a default given a literal false " "with 'allow false' equal to true"
        ),
        template=r"{{ false | default: 'bar', allow_false: true }}",
        expect="false",
    ),
    Case(
        description=(
            "render a default given a literal false "
            "with 'allow false' equal to false"
        ),
        template=r"{{ false | default: 'bar', allow_false: false }}",
        expect="bar",
    ),
    Case(
        description=("unexpected left value for the `join` filter passes through"),
        template=r"{{ 12 | join: '#' }}",
        expect="12",
    ),
    Case(
        description="render an output start sequence as a string literal",
        template=r"{{ '{{' }}",
        expect=r"{{",
    ),
    Case(
        description="access an undefined variable by index",
        template=r"{{ nosuchthing[0] }}",
        expect="",
    ),
    Case(
        description="render a range object",
        template=r"{{ (1..5) | join: '#' }}",
        expect="1#2#3#4#5",
    ),
    Case(
        description="render a range object that uses a float",
        template=r"{{ (1.4..5) | join: '#' }}",
        expect="1#2#3#4#5",
    ),
    Case(
        description="render a range object that uses an identifier",
        template=r"{{ (foo..5) | join: '#' }}",
        expect="2#3#4#5",
        globals={"foo": 2},
    ),
    Case(
        description="reverse a range",
        template=r"{{ (foo..5) | reverse | join: '#' }}",
        expect="5#4#3#2",
        globals={"foo": 2},
    ),
    Case(
        description="chained bracketed identifier index",
        template=r"{{ products[0].title }}",
        expect="shoe",
        globals={"products": [{"title": "shoe"}, {"title": "hat"}]},
    ),
    Case(
        description="chained bracketed identifier index no dot",
        template=r"{{ products[0]title }}",
        expect="shoe",
        globals={"products": [{"title": "shoe"}, {"title": "hat"}]},
    ),
    Case(
        description="chained identifier dot separated index",
        template=r"{{ products.0.title }}",
        expect="",
        globals={"products": [{"title": "shoe"}, {"title": "hat"}]},
        strict=True,
        error=True,
    ),
    Case(
        description="bracketed variable resolves to a string",
        template=r"{{ foo[something] }}",
        expect="goodbye",
        globals={"foo": {"hello": "goodbye"}, "something": "hello"},
    ),
    Case(
        description=(
            "bracketed variable resolves to a string without leading identifier"
        ),
        template=r"{{ [something] }}",
        expect="goodbye",
        globals={"something": "hello", "hello": "goodbye"},
    ),
    Case(
        description="nested bracketed variable resolving to a string",
        template=r"{{ [list[settings.zero]] }}",
        expect="bar",
        globals={"list": ["foo"], "settings": {"zero": 0}, "foo": "bar"},
    ),
]
