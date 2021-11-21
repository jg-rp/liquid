"""Golden tests cases for testing liquid's built-in `remove` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="remove substrings",
        template=(
            r'{{ "I strained to see the train through the rain" | remove: "rain" }}'
        ),
        expect="I sted to see the t through the ",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | remove: 'there' }}",
        expect="5",
    ),
    Case(
        description="argument not a string",
        template=r'{{ "hello" | remove: 5 }}',
        expect="hello",
    ),
    Case(
        description="missing argument",
        template=r'{{ "hello" | remove }}',
        expect="",
        error=True,
    ),
    Case(
        description="too many arguments",
        template=r'{{ "hello" | remove: "how", "are", "you" }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r'{{ nosuchthing | remove: "rain" }}',
        expect="",
    ),
    Case(
        description="undefined argument",
        template=r'{{ "hello" | remove: nosuchthing }}',
        expect="hello",
    ),
]
