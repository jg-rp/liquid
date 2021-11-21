"""Golden tests cases for testing liquid's built-in `times` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="int times int",
        template=r"{{ 5 | times: 2 }}",
        expect="10",
    ),
    Case(
        description="int times float",
        template=r"{{ 5 | times: 2.1 }}",
        expect="10.5",
    ),
    Case(
        description="float times float",
        template=r"{{ 5.0 | times: 2.1 }}",
        expect="10.5",
    ),
    Case(
        description="string times string",
        template=r'{{ "5.0" | times: "2.1" }}',
        expect="10.5",
    ),
    Case(
        description="negative multiplication",
        template=r"{{ -5 | times: 2 }}",
        expect="-10",
    ),
    Case(
        description="missing arg",
        template=r"{{ 5 | times }}",
        expect="",
        error=True,
    ),
    Case(
        description="too many args",
        template=r"{{ 5 | times: 1, 2 }}",
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | times: 2 }}",
        expect="0",
    ),
    Case(
        description="undefined argument",
        template=r"{{ 5 | times: nosuchthing }}",
        expect="0",
    ),
]
