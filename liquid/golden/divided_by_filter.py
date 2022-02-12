"""Golden tests cases for testing liquid's built-in `divided_by` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="integer value and integer arg",
        template=r"{{ 10 | divided_by: 2 }}",
        expect="5",
    ),
    Case(
        description="integer value and float arg",
        template=r"{{ 10 | divided_by: 2.0 }}",
        expect="5.0",
    ),
    Case(
        description="integer division",
        template=r"{{ 9 | divided_by: 2 }}",
        expect="4",
    ),
    Case(
        description="float value and integer arg",
        template=r"{{ 9.0 | divided_by: 2 }}",
        expect="4.5",
    ),
    Case(
        description="float division",
        template=r"{{ 20 | divided_by: 7.0 }}",
        expect="2.857142857142857",
    ),
    Case(
        description="string value and argument",
        template=r'{{ "10" | divided_by: "2" }}',
        expect="5",
    ),
    Case(
        description="string not a number",
        template=r'{{ "foo" | divided_by: "2" }}',
        expect="0",
    ),
    Case(
        description="arg string not a number",
        template=r'{{ "10" | divided_by: "foo" }}',
        expect="",
        error=True,
    ),
    Case(
        description="too many args",
        template=r"{{ 5 | divided_by: 1, '5' }}",
        expect="",
        error=True,
    ),
    Case(
        description="not a string, int or float",
        template=r"{{ a | divided_by: 1 }}",
        expect="0",
        globals={"a": {}},
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | divided_by: 2 }}",
        expect="0",
    ),
    Case(
        description="undefined argument",
        template=r"{{ 10 | divided_by: nosuchthing }}",
        expect="",
        error=True,
    ),
    Case(
        description="divied by zero",
        template=r"{{ 10 | divided_by: 0 }}",
        expect="",
        error=True,
    ),
    Case(
        description="zero divided by float",
        template=r"{{ 0 | divided_by: 1.1 }}",
        expect="0.0",
    ),
    Case(
        description="zero divided by integer",
        template=r"{{ 0 | divided_by: 1 }}",
        expect="0",
    ),
    Case(
        description="issue",
        template=r"{{ 5 | divided_by: 3 }}",
        expect="1",
    ),
    Case(
        description="render",
        template=r"{{ 5.0 }} {{ 5 }}",
        expect="5.0 5",
    ),
    Case(
        description="left value is an empty string",
        template=r"{{ '' | divided_by: 2 }}",
        expect="0",
    ),
]
