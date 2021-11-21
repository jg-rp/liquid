"""Golden tests cases for testing liquid's built-in `abs` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="positive integer",
        template=r"{{ 5 | abs }}",
        expect="5",
    ),
    Case(
        description="negative integer",
        template=r"{{ -5 | abs }}",
        expect="5",
    ),
    Case(
        description="positive float",
        template=r"{{ 5.4 | abs }}",
        expect="5.4",
    ),
    Case(
        description="negative float",
        template=r"{{ -5.4 | abs }}",
        expect="5.4",
    ),
    Case(
        description="zero",
        template=r"{{ 0 | abs }}",
        expect="0",
    ),
    Case(
        description="positive string integer",
        template=r"{{ '5' | abs }}",
        expect="5",
    ),
    Case(
        description="negative string integer",
        template=r"{{ '-5' | abs }}",
        expect="5",
    ),
    Case(
        description="positive string float",
        template=r"{{ '5.1' | abs }}",
        expect="5.1",
    ),
    Case(
        description="negative string float",
        template=r"{{ '-5.1' | abs }}",
        expect="5.1",
    ),
    Case(
        description="unexpected argument",
        template=r"{{ -3 | abs: 1 }}",
        expect="",
        error=True,
    ),
    Case(
        description="string not a number",
        template=r"{{ 'hello' | abs }}",
        expect="0",
    ),
    Case(
        description="not a string, int or float",
        template=r"{{ a | abs }}",
        expect="0",
        globals={"a": {}},
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | abs }}",
        expect="0",
    ),
]
