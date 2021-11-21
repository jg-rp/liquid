"""Golden tests cases for testing liquid's built-in `remove_first` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="remove substrings",
        template=(
            r'{{ "I strained to see the train through the rain" | '
            r'remove_first: "rain" }}'
        ),
        expect="I sted to see the train through the rain",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | remove_first: 'rain' }}",
        expect="5",
    ),
    Case(
        description="argument not a string",
        template=r'{{ "hello" | remove_first: 5 }}',
        expect="hello",
    ),
    Case(
        description="missing argument",
        template=r'{{ "hello" | remove_first }}',
        expect="",
        error=True,
    ),
    Case(
        description="too many arguments",
        template=r'{{ "hello" | remove_first: "how", "are", "you" }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r'{{ nosuchthing | remove_first: "rain" }}',
        expect="",
    ),
    Case(
        description="undefined argument",
        template=r'{{ "hello" | remove_first: nosuchthing }}',
        expect="hello",
    ),
]
