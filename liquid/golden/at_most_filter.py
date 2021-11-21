"""Golden tests cases for testing liquid's built-in `at_most` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="positive integer < arg",
        template=r"{{ 5 | at_most: 8 }}",
        expect="5",
    ),
    Case(
        description="positive integer > arg",
        template=r"{{ 8 | at_most: 5 }}",
        expect="5",
    ),
    Case(
        description="negative integer < arg",
        template=r"{{ -8 | at_most: 5 }}",
        expect="-8",
    ),
    Case(
        description="positive integer == arg",
        template=r"{{ 5 | at_most: 5 }}",
        expect="5",
    ),
    Case(
        description="positive float < arg",
        template=r"{{ 5.4 | at_most: 8.9 }}",
        expect="5.4",
    ),
    Case(
        description="positive float > arg",
        template=r"{{ 8.4 | at_most: 5.9 }}",
        expect="5.9",
    ),
    Case(
        description="positive string > arg",
        template=r'{{ "9" | at_most: 8 }}',
        expect="8",
    ),
    Case(
        description="missing arg",
        template=r"{{ 5 | at_most }}",
        expect="",
        error=True,
    ),
    Case(
        description="too many args",
        template=r"{{ 5 | at_most: 1, 2}}",
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | at_most: 5 }}",
        expect="0",
    ),
    Case(
        description="undefined argument",
        template=r"{{ 5 | at_most: nosuchthing }}",
        expect="0",
    ),
    Case(
        description="left value not a number",
        template=r'{{ "abc" | at_most: -2 }}',
        expect="-2",
    ),
]
