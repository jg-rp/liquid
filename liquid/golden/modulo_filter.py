"""Golden tests cases for testing liquid's built-in `modulo` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="integer value and integer arg",
        template=r"{{ 10 | modulo: 2 }}",
        expect="0",
    ),
    Case(
        description="integer value and float arg",
        template=r"{{ 10 | modulo: 2.0 }}",
        expect="0.0",
    ),
    Case(
        description="float value and float arg",
        template=r"{{ 10.1 | modulo: 7.0 }}",
        expect="3.1",
    ),
    Case(
        description="string value and argument",
        template=r'{{ "10" | modulo: "2.0" }}',
        expect="0.0",
    ),
    Case(
        description="string not a number",
        template=r'{{ "foo" | modulo: "2.0" }}',
        expect="0.0",
    ),
    Case(
        description="arg string not a number",
        template=r'{{ "10" | modulo: "foo" }}',
        expect="",
        error=True,
    ),
    Case(
        description="too many args",
        template=r"{{ 5 | modulo: 1, '5' }}",
        expect="",
        error=True,
    ),
    Case(
        description="not a string, int or float",
        template=r"{{ a | modulo: 1 }}",
        expect="0",
        globals={"a": {}},
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | modulo: 2 }}",
        expect="0",
    ),
    Case(
        description="undefined argument",
        template=r"{{ 5 | modulo: nosuchthing }}",
        expect="",
        error=True,
    ),
]
