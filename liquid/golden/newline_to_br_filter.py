"""Golden tests cases for testing liquid's built-in `newline_to_br` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="string with newlines",
        template='{{ "- apples\n- oranges\n" | newline_to_br }}',
        expect="- apples<br />\n- oranges<br />\n",
    ),
    Case(
        description="not a string",
        template="{{ 5 | newline_to_br }}",
        expect="5",
    ),
    Case(
        description="unexpected argument",
        template='{{ "hello" | newline_to_br: 5 }}',
        expect="",
        error=True,
    ),
    Case(
        description="reference implementation test 1",
        template='{{ "a\nb\nc" | newline_to_br }}',
        expect="a<br />\nb<br />\nc",
    ),
    Case(
        description="reference implementation test 2",
        template='{{ "a\r\nb\nc" | newline_to_br }}',
        expect="a<br />\nb<br />\nc",
    ),
    Case(
        description="undefined left value",
        template="{{ nosuchthing | newline_to_br }}",
        expect="",
    ),
]
