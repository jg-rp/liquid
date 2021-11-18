"""Golden tests cases for testing liquid's built-in `map` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="array of objects",
        template=r"{{ a | map: 'title' | join: '#' }}",
        expect="foo#bar#baz",
        globals={"a": [{"title": "foo"}, {"title": "bar"}, {"title": "baz"}]},
    ),
    Case(
        description="missing property",
        template=r"{{ a | map: 'title' | join: '#' }}",
        expect="foo#bar#",
        globals={"a": [{"title": "foo"}, {"title": "bar"}, {"heading": "baz"}]},
    ),
    Case(
        description="left value not an array",
        template=r"{{ a | map: 'title' | join: '#' }}",
        expect="",
        globals={"a": 123},
        error=True,
    ),
    Case(
        description="array containing a non object",
        template=r"{{ a | map: 'title' | join: '#' }}",
        expect="",
        globals={"a": [{"title": "foo"}, {"title": "bar"}, 5, []]},
        error=True,
    ),
    Case(
        description="undefined argument",
        template=r"{{ a | map: nosuchthing | join: '#' }}",
        expect="#",
        globals={"a": [{"title": "foo"}, {"title": "bar"}]},
    ),
]
