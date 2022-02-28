"""Golden tests cases for testing liquid's built-in `remove_last` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="remove substrings",
        template=(
            r'{{ "I strained to see the train through the rain" | '
            r'remove_last: "rain" }}'
        ),
        expect="I strained to see the train through the ",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | remove_last: 'rain' }}",
        expect="5",
    ),
    Case(
        description="argument not a string",
        template=r'{{ "hello" | remove_last: 5 }}',
        expect="hello",
    ),
    Case(
        description="missing argument",
        template=r'{{ "hello" | remove_last }}',
        expect="",
        error=True,
    ),
    Case(
        description="too many arguments",
        template=r'{{ "hello" | remove_last: "how", "are", "you" }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r'{{ nosuchthing | remove_last: "rain" }}',
        expect="",
    ),
    Case(
        description="undefined argument",
        template=r'{{ "hello" | remove_last: nosuchthing }}',
        expect="hello",
    ),
]
