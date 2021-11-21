"""Golden tests cases for testing liquid's built-in `rstrip` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="left padded",
        template='{{ " \t\r\n  hello" | rstrip }}',
        expect=" \t\r\n  hello",
    ),
    Case(
        description="right padded",
        template='{{ "hello \t\r\n  " | rstrip }}',
        expect="hello",
    ),
    Case(
        description="left and right padded",
        template='{{ " \t\r\n  hello  \t\r\n " | rstrip }}',
        expect=" \t\r\n  hello",
    ),
    Case(
        description="not a string",
        template="{{ 5 | rstrip }}",
        expect="5",
    ),
    Case(
        description="unexpected argument",
        template='{{ "hello" | rstrip: 5 }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template="{{ nosuchthing | rstrip }}",
        expect="",
    ),
]
