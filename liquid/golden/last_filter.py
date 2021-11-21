"""Golden tests cases for testing liquid's built-in `first` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="range literal last filter left value",
        template=r"{{ (1..3) | last }}",
        expect="3",
    ),
    Case(
        description="array of strings",
        template=r"{{ arr | last }}",
        expect="b",
        globals={"arr": ["a", "b"]},
    ),
    Case(
        description="array of things",
        template=r"{{ arr | last }}",
        expect="{}",
        globals={"arr": ["a", "b", 1, [], {}]},
    ),
    Case(
        description="empty array",
        template=r"{{ arr | last }}",
        expect="",
        globals={"arr": []},
    ),
    Case(
        description="left value not an array",
        template=r"{{ arr | last }}",
        expect="",
        globals={"arr": 12},
    ),
    Case(
        description="left value is undefined",
        template=r"{{ nosuchthing | last }}",
        expect="",
    ),
    Case(
        description="last of a string",
        template=r"{{ 'hello' | last }}",
        expect="",
    ),
    Case(
        description="last of a hash",
        template=r"{{ a | last }}",
        expect="",
        globals={"a": {"b": 1, "c": 2}},
    ),
]
