"""Golden tests cases for testing liquid's built-in `slice` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="zero",
        template=r'{{ "hello" | slice: 0 }}',
        expect="h",
    ),
    Case(
        description="one",
        template=r'{{ "hello" | slice: 1 }}',
        expect="e",
    ),
    Case(
        description="one length three",
        template=r'{{ "hello" | slice: 1, 3 }}',
        expect="ell",
    ),
    Case(
        description="out of range",
        template=r'{{ "hello" | slice: 99 }}',
        expect="",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | slice: 1 }}",
        expect="",
    ),
    Case(
        description="first argument not an integer",
        template=r'{{ "hello" | slice: "foo" }}',
        expect="",
        error=True,
    ),
    Case(
        description="second argument not an integer",
        template=r'{{ "hello" | slice: 5, "foo" }}',
        expect="",
        error=True,
    ),
    Case(
        description="missing arguments",
        template=r'{{ "hello" | slice }}',
        expect="",
        error=True,
    ),
    Case(
        description="too many arguments",
        template=r'{{ "hello" | slice: 1, 2, 3 }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | slice: 1, 3 }}",
        expect="",
    ),
    Case(
        description="undefined first argument",
        template=r'{{ "hello" | slice: nosuchthing, 3 }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined second argument",
        template=r'{{ "hello" | slice: 1, nosuchthing }}',
        expect="e",
    ),
    Case(
        description="slice an array of numbers",
        template=r"{{ a | slice: 2, 3 | join: '#' }}",
        expect="3#4#5",
        globals={"a": [1, 2, 3, 4, 5]},
    ),
    Case(
        description="slice a hash",
        template=r"{{ a | slice: 2, 1 | join: '#' }}",
        expect="a",
        globals={"a": {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}},
    ),
]
