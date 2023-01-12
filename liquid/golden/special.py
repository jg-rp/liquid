"""Golden test cases for testing Liquid's special, built-in properties."""

from liquid.golden.case import Case

cases = [
    Case(
        description="first of an array",
        template=r"{{ a.first }}",
        expect="3",
        globals={"a": [3, 2, 1]},
    ),
    Case(
        description="last of an array",
        template=r"{{ a.last }}",
        expect="1",
        globals={"a": [3, 2, 1]},
    ),
    Case(
        description="size of an array",
        template=r"{{ a.size }}",
        expect="3",
        globals={"a": [3, 2, 1]},
    ),
    Case(
        description="size of a string",
        template=r"{{ s.size }}",
        expect="5",
        globals={"s": "hello"},
    ),
    Case(
        description="first of a string",
        template=r"{{ s.first }}",
        expect="",
        globals={"s": "hello"},
    ),
    Case(
        description="first of an object",
        template=r"{{ obj.first | join: '#' }}",
        expect="a#1",
        globals={"obj": {"a": 1, "b": 2}},
    ),
    Case(
        description="first of an empty object",
        template=r"{{ obj.first | join: '#' }}",
        expect="",
        globals={"obj": {}},
    ),
    Case(
        description="last of a string",
        template=r"{{ s.last }}",
        expect="",
        globals={"s": "hello"},
    ),
    Case(
        description="last of a object",
        template=r"{{ obj.last }}",
        expect="",
        globals={"obj": {"a": 1, "b": 2}},
    ),
    Case(
        description="size of an object with a size property",
        template=r"{{ obj.size }}",
        expect="99",
        globals={"obj": {"size": 99}},
    ),
    Case(
        description="first of an object with a first property",
        template=r"{{ obj.first }}",
        expect="99",
        globals={"obj": {"a": 1, "first": 99}},
    ),
    Case(
        description="last of an object with a last property",
        template=r"{{ obj.last }}",
        expect="99",
        globals={"obj": {"a": 1, "last": 99, "b": 42}},
    ),
    Case(
        description="size of undefined",
        template=r"{{ nosuchthing.last }}",
        expect="",
        globals={},
    ),
    Case(
        description="size of an int",
        template=r"{{ x.size }}",
        expect="",
        globals={"x": 1},
        standard=False,
    ),
]
