"""Golden tests cases for testing liquid's built-in `url_decode` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="some special URL characters",
        template=r'{{ "email+address+is+bob%40example.com%21" | url_decode }}',
        expect="email address is bob@example.com!",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | url_decode }}",
        expect="5",
    ),
    Case(
        description="unexpected argument",
        template=r'{{ "hello" | url_decode: 5 }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | url_decode }}",
        expect="",
    ),
]
