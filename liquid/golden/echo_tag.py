"""Golden tests cases for testing liquid's `echo` tag."""

import datetime
from liquid.golden.case import Case

cases = [
    Case(
        description="render a string literal",
        template=r"{% echo 'hello' %}",
        expect="hello",
    ),
    Case(
        description="render an integer literal",
        template=r"{% echo 123 %}",
        expect="123",
    ),
    Case(
        description="render a float literal",
        template=r"{% echo 1.23 %}",
        expect="1.23",
    ),
    Case(
        description="render a variable from the global namespace",
        template=r"{% echo product.title %}",
        expect="foo",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="render a variable from the local namespace",
        template=r"{% assign name = 'Brian' %}{% echo name %}",
        expect="Brian",
    ),
    Case(
        description="render an undefined variable",
        template=r"{% echo age %}",
        expect="",
    ),
    Case(
        description="render an undefined property",
        template=r"{% echo product.age %}",
        expect="",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="access an array item by index",
        template=r"{% echo product.tags[1] %}",
        expect="garden",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="access an array item by negative index",
        template=r"{% echo product.tags[-2] %}",
        expect="sports",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="access array item by index stored in a local variable",
        template=r"{% assign i = 1 %}{% echo product.tags[i] %}",
        expect="garden",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="render a global identifier with a filter",
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
        description="assign a variable the value of an existing variable",
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
        description="render the special built in variable 'now'",
        template=r"{% echo now | date: '%d/%m/%Y' %}",
        expect=datetime.datetime.now().strftime(r"%d/%m/%Y"),
        standard=False,
    ),
    Case(
        description="render the special built in variable 'today'",
        template=r"{% echo today | date: '%d/%m/%Y' %}",
        expect=datetime.date.today().strftime(r"%d/%m/%Y"),
        standard=False,
    ),
    Case(
        description="access an undefined variable by index",
        template=r"{% echo nosuchthing[0] %}",
        expect="",
    ),
    Case(
        description="nothing to echo",
        template=r"{% echo %}",
        expect="",
    ),
]
