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
        description="last of a string",
        template=r"{{ s.last }}",
        expect="",
        globals={"s": "hello"},
    ),
]
