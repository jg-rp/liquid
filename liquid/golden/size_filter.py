"""Golden tests cases for testing liquid's built-in `size` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="size of an array",
        template=r"{{ a | size }}",
        globals={"a": ["a", "b", "c"]},
        expect="3",
    ),
    Case(
        description="size of a string",
        template=r"{{ a | size }}",
        globals={"a": "abc"},
        expect="3",
    ),
    Case(
        description="size of an empty array",
        template=r"{{ a | size }}",
        globals={"a": []},
        expect="0",
    ),
    Case(
        description="size of a hash",
        template=r"{{ a | size }}",
        globals={"a": {"a": 1, "b": 2}},
        expect="2",
    ),
    Case(
        description="unexpected argument",
        template=r"{{ a | size: 'foo' }}",
        globals={"a": [1, 2, 3]},
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | size }}",
        expect="0",
    ),
]
