"""Golden tests cases for testing liquid's built-in `ceil` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="positive integer",
        template=r"{{ 5 | floor }}",
        expect="5",
    ),
    Case(
        description="negative integer",
        template=r"{{ -5 | floor }}",
        expect="-5",
    ),
    Case(
        description="positive float",
        template=r"{{ 5.4 | floor }}",
        expect="5",
    ),
    Case(
        description="negative float",
        template=r"{{ -5.4 | floor }}",
        expect="-6",
    ),
    Case(
        description="zero",
        template=r"{{ 0 | floor }}",
        expect="0",
    ),
    Case(
        description="positive string float",
        template=r'{{ "5.1" | floor }}',
        expect="5",
    ),
    Case(
        description="negative string float",
        template=r'{{ "-5.1" | floor }}',
        expect="-6",
    ),
    Case(
        description="unexpected argument",
        template=r"{{ -3.1 | floor: 1 }}",
        expect="",
        error=True,
    ),
    Case(
        description="string not a number",
        template=r'{{ "hello" | floor }}',
        expect="0",
    ),
    Case(
        description="not a string, int or float",
        template=r"{{ a | floor }}",
        expect="0",
        globals={"a": {}},
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | floor }}",
        expect="0",
    ),
]
