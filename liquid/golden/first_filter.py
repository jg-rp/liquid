"""Golden tests cases for testing liquid's built-in `first` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="range literal first filter left value",
        template=r"{{ (1..3) | first }}",
        expect="1",
    ),
    Case(
        description="array of strings",
        template=r"{{ arr | first }}",
        expect="a",
        globals={"arr": ["a", "b"]},
    ),
    Case(
        description="array of things",
        template=r"{{ arr | first }}",
        expect="a",
        globals={"arr": ["a", "b", 1, [], {}]},
    ),
    Case(
        description="empty left value",
        template=r"{{ arr | first }}",
        expect="",
        globals={"arr": []},
    ),
    Case(
        description="left value is not an array",
        template=r"{{ arr | first }}",
        expect="",
        globals={"arr": 12},
    ),
    Case(
        description="left value is undefined",
        template=r"{{ nosuchthing | first }}",
        expect="",
    ),
    Case(
        description="first of a string",
        template=r"{{ 'hello' | first }}",
        expect="",
    ),
    Case(
        description="first of a hash",
        template=r"{% assign x = a | first %}({{ x[0] }},{{ x[1] }})",
        expect="(b,1)",
        globals={"a": {"b": 1, "c": 2}},
    ),
]
