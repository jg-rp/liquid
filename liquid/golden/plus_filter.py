"""Golden tests cases for testing liquid's built-in `plus` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="integer value and integer arg",
        template=r"{{ 10 | plus: 2 }}",
        expect="12",
    ),
    Case(
        description="integer value and float arg",
        template=r"{{ 10 | plus: 2.0 }}",
        expect="12.0",
    ),
    Case(
        description="float value and float arg",
        template=r"{{ 10.1 | plus: 2.2 }}",
        expect="12.3",
    ),
    Case(
        description="string value and string arg",
        template=r'{{ "10.1" | plus: "2.2" }}',
        expect="12.3",
    ),
    Case(
        description="string not a number",
        template=r'{{ "foo" | plus: "2.0" }}',
        expect="2.0",
    ),
    Case(
        description="arg string not a number",
        template=r'{{ "10" | plus: "foo" }}',
        expect="10",
    ),
    Case(
        description="too many args",
        template=r"{{ 5 | plus: 1, '5' }}",
        expect="",
        error=True,
    ),
    Case(
        description="not a string, int or float",
        template=r"{{ a | plus: 1 }}",
        expect="1",
        globals={"a": {}},
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | plus: 2 }}",
        expect="2",
    ),
    Case(
        description="undefined argument",
        template=r"{{ 10 | plus: nosuchthing }}",
        expect="10",
    ),
]
