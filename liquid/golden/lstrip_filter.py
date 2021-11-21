"""Golden tests cases for testing liquid's built-in `lstrip` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="left padded",
        template='{{ " \t\r\n  hello" | lstrip }}',
        expect="hello",
    ),
    Case(
        description="right padded",
        template='{{ "hello \t\r\n  " | lstrip }}',
        expect="hello \t\r\n  ",
    ),
    Case(
        description="left and right padded",
        template='{{ " \t\r\n  hello  \t\r\n " | lstrip }}',
        expect="hello  \t\r\n ",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | lstrip }}",
        expect="5",
    ),
    Case(
        description="unexpected argument",
        template=r'{{ "hello" | lstrip: 5 }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | lstrip }}",
        expect="",
    ),
]
