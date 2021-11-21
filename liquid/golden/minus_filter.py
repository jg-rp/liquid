"""Golden tests cases for testing liquid's built-in `minus` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="integer value and integer arg",
        template=r"{{ 10 | minus: 2 }}",
        expect="8",
    ),
    Case(
        description="integer value and float arg",
        template=r"{{ 10 | minus: 2.0 }}",
        expect="8.0",
    ),
    Case(
        description="float value and float arg",
        template=r"{{ 10.1 | minus: 2.2 }}",
        expect="7.9",
    ),
    Case(
        description="string value and string arg",
        template=r'{{ "10.1" | minus: "2.2" }}',
        expect="7.9",
    ),
    Case(
        description="string not a number",
        template=r'{{ "foo" | minus: "2.0" }}',
        expect="-2.0",
    ),
    Case(
        description="arg string not a number",
        template=r'{{ "10" | minus: "foo" }}',
        expect="10",
    ),
    Case(
        description="too many args",
        template=r"{{ 5 | minus: 1, '5' }}",
        expect="",
        error=True,
    ),
    Case(
        description="not a string, int or float",
        template=r"{{ a | minus: 1 }}",
        expect="-1",
        globals={"a": {}},
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | minus: 2 }}",
        expect="-2",
    ),
    Case(
        description="undefined argument",
        template=r"{{ 10 | minus: nosuchthing }}",
        expect="10",
    ),
]
