"""Golden tests cases for testing liquid's built-in `strip` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="left padded",
        template='{{ " \t\r\n  hello" | strip }}',
        expect="hello",
    ),
    Case(
        description="right padded",
        template='{{ "hello \t\r\n  " | strip }}',
        expect="hello",
    ),
    Case(
        description="left and right padded",
        template='{{ " \t\r\n  hello  \t\r\n " | strip }}',
        expect="hello",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | strip }}",
        expect="5",
    ),
    Case(
        description="unexpected argument",
        template=r'{{ "hello" | strip: 5 }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | strip }}",
        expect="",
    ),
]
