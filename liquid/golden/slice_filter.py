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
        description="first argument is a string",
        template=r'{{ "hello" | slice: "2" }}',
        expect="l",
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
        description="second argument is a string",
        template=r'{{ "hello" | slice: 3, "2" }}',
        expect="lo",
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
        description="first argument is a float",
        template=r"{{ 'Liquid' | slice: 2.2 }}",
        expect="",
        error=True,
    ),
    Case(
        description="second argument is a float",
        template=r"{{ 'Liquid' | slice: 1, 2.2 }}",
        expect="",
        error=True,
    ),
    Case(
        description="negative first argument",
        template=r"{{ 'Liquid' | slice: -2 }}",
        expect="i",
    ),
    Case(
        description="negative first argument and positive length",
        template=r"{{ 'Liquid' | slice: -2, 2 }}",
        expect="id",
    ),
    Case(
        description="negative first argument and negative length",
        template=r"{{ 'Liquid' | slice: -2, -1 }}",
        expect="",
    ),
    Case(
        description="negative first argument and length out of range",
        template=r"{{ 'Liquid' | slice: -2, 99 }}",
        expect="id",
    ),
]
