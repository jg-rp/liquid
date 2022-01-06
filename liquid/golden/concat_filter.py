"""Golden tests cases for testing liquid's built-in `concat` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="range literal concat filter left value",
        template=r"{{ (1..3) | concat: foo | join: '#' }}",
        expect="1#2#3#5#6#7",
        globals={"foo": [5, 6, 7]},
    ),
    Case(
        description="two arrays of strings",
        template=r"{{ a | concat: b | join: '#' }}",
        expect="a#b#c#d",
        globals={"a": ["a", "b"], "b": ["c", "d"]},
    ),
    Case(
        description="missing argument is an error",
        template=r"{{ a | concat | join: '#' }}",
        expect="a#b",
        globals={"a": ["a", "b"]},
        error=True,
    ),
    Case(
        description="non array-like argument is an error",
        template=r"{{ a | concat: b | join: '#' }}",
        expect="",
        globals={"a": ["a", "b"], "b": 5},
        error=True,
    ),
    Case(
        description="left value is not array-like",
        template=r"{{ a | concat: b | join: '#' }}",
        expect="ab#c#d",
        globals={"a": "ab", "b": ["c", "d"]},
    ),
    Case(
        description="left value contains non string",
        template=r"{{ a | concat: b | join: '#' }}",
        expect="a#b#5#c#d",
        globals={"a": ["a", "b", 5], "b": ["c", "d"]},
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | concat: b | join: '#' }}",
        expect="c#d",
        globals={"b": ["c", "d"]},
    ),
    Case(
        description="undefined argument is an error",
        template=r"{{ a | concat: nosuchthing | join: '#' }}",
        expect="",
        globals={"a": ["a", "b"]},
        error=True,
    ),
    Case(
        description="nested left value gets flattened",
        template=r"{{ a | concat: b | join: '#' }}",
        expect="a#x#b#y#z#c#d",
        globals={"a": [["a", "x"], ["b", ["y", ["z"]]]], "b": ["c", "d"]},
    ),
]
