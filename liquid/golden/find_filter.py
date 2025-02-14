"""Test cases for the standard `find` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="array of strings, default value",
        template=r"{{ a | find: 'z' }}",
        expect="z",
        globals={"a": ["x", "y", "z"]},
    ),
    Case(
        description="array of strings, substring match, default value",
        template=r"{{ a | find: 'oo' }}",
        expect="zoo",
        globals={"a": ["x", "y", "zoo"]},
    ),
    Case(
        description="array of strings, default value, no match",
        template=r"{{ a | find: 'foo' }}",
        expect="",
        globals={"a": ["x", "y", "zoo"]},
    ),
    # Case(
    #     description="array of ints, default value",
    #     template=r"{{ a | find: 2 }}",
    #     expect="1",
    #     globals={"a": [1, 2, 3]},
    # ),
    Case(
        description="mixed array, default value",
        template=r"{{ a | find: 'z' }}",
        expect="",
        globals={"a": ["x", None, "z", False, True]},
    ),
    Case(
        description="string input, default value, match",
        template=r"{{ a | find: 'z' }}",
        expect="zoo",
        globals={"a": "zoo"},
    ),
    Case(
        description="string input, string value, match",
        template=r"{{ a | find: 'z', 'z' }}",
        expect="zoo",
        globals={"a": "zoo"},
    ),
    Case(
        description="string input, string value, no match",
        template=r"{{ a | find: 'z', 'y' }}",
        expect="",
        globals={"a": "zoo"},
    ),
    Case(
        description="hash input, default value, match",
        template=r"{% assign b = a | find: 'z' %}{{ b.z }}",
        expect="42",
        globals={"a": {"z": 42}},
    ),
    Case(
        description="hash input, default value, no match",
        template=r"{% assign b = a | find: 'foo' %}{{ b }}",
        expect="",
        globals={"a": {"z": 42}},
    ),
    Case(
        description="hash input, int value, match",
        template=r"{% assign b = a | find: 'z', 42 %}{{ b.z }}",
        expect="42",
        globals={"a": {"z": 42}},
    ),
    Case(
        description="hash input, explicit nil, match",
        template=r"{% assign b = a | find: 'z', nil %}{{ b.z }}",
        expect="",
        globals={"a": {"z": None}},
    ),
    Case(
        description="array of hashes, int value, match",
        template=r"{% assign b = a | find: 'z', 42 %}{{ b.foo }}",
        expect="bar",
        globals={"a": [{"x": 99}, {"z": 42, "foo": "bar"}]},
    ),
    Case(
        description="array of hashes, with a nil",
        template=r"{% assign b = a | find: 'z', 42 %}{{ b.foo }}",
        expect="",
        globals={"a": [{"x": 99}, None, {"z": 42, "foo": "bar"}]},
    ),
]
