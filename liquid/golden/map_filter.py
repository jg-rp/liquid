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
    Case(
        description="nested arrays get flattened",
        template=r"{{ a | map: 'title' | join: '#' }}",
        expect="foo#bar#baz",
        globals={"a": [{"title": "foo"}, [{"title": "bar"}, {"title": "baz"}]]},
    ),
    Case(
        description="input is a hash",
        template=r"{{ a | map: 'title' | join: '#' }}",
        expect="foo",
        globals={"a": {"title": "foo", "some": "thing"}},
    ),
    Case(
        description="dotted property, string match",
        template=r"{{ a | map: 'user.title' | join: '#' }}",
        expect="foo#bar#baz",
        globals={
            "a": [{"user.title": "foo"}, {"user.title": "bar"}, {"user.title": "baz"}]
        },
    ),
    Case(
        description="dotted property, string match, missing property",
        template=r"{{ a | map: 'user.title' | join: '#' }}",
        expect="foo##baz",
        globals={
            "a": [
                {"user.title": "foo"},
                {"user.firstname": "bar"},
                {"user.title": "baz"},
            ]
        },
    ),
    Case(
        description="dotted property, path match",
        template=r"{{ a | map: 'user.title' | join: '#' }}",
        expect="foo#bar#baz",
        globals={
            "a": [
                {"user": {"title": "foo"}},
                {"user": {"title": "bar"}},
                {"user": {"title": "baz"}},
            ]
        },
    ),
    Case(
        description="dotted property, path and string match",
        template=r"{{ a | map: 'user.title' | join: '#' }}",
        expect="foo#bar#baz",
        globals={
            "a": [
                {"user.title": "foo"},
                {"user": {"title": "bar"}},
                {"user": {"title": "baz"}},
            ]
        },
    ),
    Case(
        description="dotted property, path match, missing property",
        template=r"{{ a | map: 'user.title' | join: '#' }}",
        expect="foo##baz",
        globals={
            "a": [
                {"user": {"title": "foo"}},
                {"user": {"firstname": "bar"}},
                {"user": {"title": "baz"}},
            ]
        },
    ),
    Case(
        description="property with bracketed index",
        template=r"{{ a | map: 'user[1]' | join: '#' }}",
        expect="##",
        globals={
            "a": [
                {"user": [1, 2, 3]},
                {"user": [4, 5, 6]},
                {"user": [7, 8, 9]},
            ]
        },
    ),
]
