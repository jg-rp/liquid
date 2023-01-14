"""Golden tests cases for testing liquid's built-in `round` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="float round down",
        template=r"{{ 5.1 | round }}",
        expect="5",
    ),
    Case(
        description="float round up",
        template=r"{{ 5.6 | round }}",
        expect="6",
    ),
    Case(
        description="float as a string",
        template=r'{{ "5.6" | round }}',
        expect="6",
    ),
    Case(
        description="string argument",
        template=r'{{ 5.666 | round: "1" }}',
        expect="5.7",
    ),
    Case(
        description="decimal places",
        template=r'{{ "5.666666" | round: 2 }}',
        expect="5.67",
    ),
    Case(
        description="integer",
        template=r"{{ 5 | round }}",
        expect="5",
    ),
    Case(
        description="too many args",
        template=r"{{ 5 | round: 1, 2 }}",
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | round: 2 }}",
        expect="0",
    ),
    Case(
        description="undefined argument",
        template=r"{{ 5.666 | round: nosuchthing }}",
        expect="6",
    ),
    Case(
        description="argument is a string",
        template=r"{{ 5.666 | round: 'foo' }}",
        expect="6",
    ),
    Case(
        description="argument is a string representation of an integer",
        template=r"{{ 5.666 | round: '1' }}",
        expect="5.7",
    ),
    Case(
        description="argument is a string representation of zero",
        template=r"{{ 5.666 | round: '1' }}",
        expect="5.7",
    ),
    # Case(
    #     description="argument is a string representation of a negative integer",
    #     template=r"{{ 5.666 | round: '-1' }}",
    #     expect="10",
    # ),
    Case(
        description="argument is a negative",
        template=r"{{ 5.666 | round: -2 }}",
        expect="0",
    ),
    Case(
        description="argument is a float",
        template=r"{{ 5.666 | round: 1.2 }}",
        expect="5.7",
    ),
    Case(
        description="argument is a zero",
        template=r"{{ 5.666 | round: 0 }}",
        expect="6",
    ),
]
