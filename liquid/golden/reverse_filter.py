"""Golden tests cases for testing liquid's built-in `reverse` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="array of strings",
        template=r"{{ a | reverse | join: '#' }}",
        expect="A#B#a#b",
        globals={"a": ["b", "a", "B", "A"]},
    ),
    Case(
        description="array of things",
        template=r"{{ a | reverse | join: '#' }}",
        expect=r"{}#1#b#a",
        globals={"a": ["a", "b", 1, [], {}]},
    ),
    Case(
        description="empty array",
        template=r"{{ a | reverse | join: '#' }}",
        expect="",
        globals={"a": []},
    ),
    Case(
        description="unexpected argument",
        template=r"{{ a | reverse: 0 | join: '#' }}",
        expect="",
        globals={"a": []},
        error=True,
    ),
    Case(
        description="left value not an array",
        template=r"{{ a | reverse | join: '#' }}",
        expect="123",
        globals={"a": 123},
    ),
    Case(
        description="left value is undefined",
        template=r"{{ nosuchthing | reverse | join: '#' }}",
        expect="",
    ),
]
