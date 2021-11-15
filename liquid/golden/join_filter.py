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
]
