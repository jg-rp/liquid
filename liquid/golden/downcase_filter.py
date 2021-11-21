"""Golden tests cases for testing liquid's built-in `downcase` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="make lower case",
        template=r'{{ "HELLO" | downcase }}',
        expect="hello",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | downcase }}",
        expect="5",
    ),
    Case(
        description="unexpected argument",
        template=r'{{ "HELLO" | downcase: 5 }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | downcase }}",
        expect="",
    ),
]
