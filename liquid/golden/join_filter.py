"""Golden tests cases for testing liquid's built-in `join` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="range literal join filter left value",
        template=r"{{ (1..3) | join: '#' }}",
        expect="1#2#3",
    ),
    Case(
        description="joining a string is a noop",
        template=r"{{ 'a,b' | join: '#' }}",
        expect="a,b",
    ),
    Case(
        description="joining an int is a noop",
        template=r"{{ 123 | join: '#' }}",
        expect="123",
    ),
    Case(
        description="join an array of strings",
        template=r"{{ arr | join: '#' }}",
        expect="a#b",
        globals={"arr": ["a", "b"]},
    ),
    Case(
        description="join an array of integers",
        template=r"{{ arr | join: '#' }}",
        expect="1#2",
        globals={"arr": [1, 2]},
    ),
    Case(
        description="missing argument defaults to a space",
        template=r"{{ arr | join }}",
        expect="a b",
        globals={"arr": ["a", "b"]},
    ),
    Case(
        description="argument is not a string",
        template=r"{{ arr | join: 5 }}",
        expect="a5b",
        globals={"arr": ["a", "b"]},
    ),
    Case(
        description="left value contains non string",
        template=r"{{ arr | join: '#' }}",
        expect="a#b#1",
        globals={"arr": ["a", "b", 1]},
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | join: '#' }}",
        expect="",
    ),
    Case(
        description="undefined argument",
        template=r"{{ arr | join: nosuchthing }}",
        expect="ab",
        globals={"arr": ["a", "b"]},
    ),
    Case(
        description="too many arguments",
        template=r"{{ arr | join: '#', 42 }}",
        expect="",
        globals={"arr": ["a", "b"]},
        error=True,
    ),
]
