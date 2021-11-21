"""Golden tests cases for testing liquid's built-in `url_encode` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="some special URL characters",
        template=r'{{ "email address is bob@example.com!" | url_encode }}',
        expect=r"email+address+is+bob%40example.com%21",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | url_encode }}",
        expect="5",
    ),
    Case(
        description="unexpected argument",
        template=r'{{ "hello" | url_encode: 5 }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | url_encode }}",
        expect="",
    ),
]
