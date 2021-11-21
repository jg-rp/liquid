"""Golden tests cases for testing liquid's built-in `capitalize` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="lower case string",
        template=r'{{ "hello" | capitalize }}',
        expect="Hello",
    ),
    Case(
        description="already capitalized string",
        template=r'{{ "Hello" | capitalize }}',
        expect="Hello",
    ),
    Case(
        description="unexpected argument",
        template=r'{{ "hello" | capitalize: 2 }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | capitalize }}",
        expect="",
    ),
]
