"""Golden tests cases for testing liquid's built-in `at_least` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="positive integer < arg",
        template=r"{{ 5 | at_least: 8 }}",
        expect="8",
    ),
    Case(
        description="positive integer > arg",
        template=r"{{ 8 | at_least: 5 }}",
        expect="8",
    ),
    Case(
        description="negative integer < arg",
        template=r"{{ -8 | at_least: 5 }}",
        expect="5",
    ),
    Case(
        description="positive integer == arg",
        template=r"{{ 5 | at_least: 5 }}",
        expect="5",
    ),
    Case(
        description="positive float < arg",
        template=r"{{ 5.4 | at_least: 8.9 }}",
        expect="8.9",
    ),
    Case(
        description="positive float > arg",
        template=r"{{ 8.4 | at_least: 5.9 }}",
        expect="8.4",
    ),
    Case(
        description="positive string > arg",
        template=r'{{ "9" | at_least: 8 }}',
        expect="9",
    ),
    Case(
        description="missing arg",
        template=r"{{ 5 | at_least }}",
        expect="",
        error=True,
    ),
    Case(
        description="too many args",
        template=r"{{ 5 | at_least: 1, 2}}",
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | at_least: 5 }}",
        expect="5",
    ),
    Case(
        description="undefined argument",
        template=r"{{ 5 | at_least: nosuchthing }}",
        expect="5",
    ),
    Case(
        description="left value not a number",
        template=r'{{ "abc" | at_least: 2 }}',
        expect="2",
    ),
    Case(
        description="left value not a number negative argument",
        template=r'{{ "abc" | at_least: -2 }}',
        expect="0",
    ),
    Case(
        description="argument string not a number",
        template=r'{{ -1 | at_least: "abc" }}',
        expect="0",
    ),
]
