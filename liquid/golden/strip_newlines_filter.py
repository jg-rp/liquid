"""Golden tests cases for testing liquid's built-in `strip_newlines` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="newline and other whitespace",
        template='{{ "hello there\nyou" | strip_newlines }}',
        expect="hello thereyou",
    ),
    Case(
        description="not a string",
        template="{{ 5 | strip_newlines }}",
        expect="5",
    ),
    Case(
        description="unexpected argument",
        template='{{ "hello" | strip_newlines: 5 }}',
        expect="",
        error=True,
    ),
    Case(
        description="reference implementation test 1",
        template='{{ "a\nb\nc" | strip_newlines }}',
        expect="abc",
    ),
    Case(
        description="reference implementation test 2",
        template='{{ "a\r\nb\nc" | strip_newlines }}',
        expect="abc",
    ),
    Case(
        description="undefined left value",
        template="{{ nosuchthing | strip_newlines }}",
        expect="",
    ),
]
