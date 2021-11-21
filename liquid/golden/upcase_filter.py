"""Golden tests cases for testing liquid's built-in `upcase` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="make lower case",
        template=r'{{ "hello" | upcase }}',
        expect="HELLO",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | upcase }}",
        expect="5",
    ),
    Case(
        description="unexpected argument",
        template=r'{{ "hello" | upcase: 5 }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | upcase }}",
        expect="",
    ),
]
