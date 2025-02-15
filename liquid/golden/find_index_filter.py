"""Test cases for the standard `find_index` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="array of strings, default value",
        template=r"{{ a | find_index: 'z' }}",
        expect="2",
        globals={"a": ["x", "y", "z"]},
    ),
    Case(
        description="array of strings, substring match, default value",
        template=r"{{ a | find_index: 'oo' }}",
        expect="2",
        globals={"a": ["x", "y", "zoo"]},
    ),
    Case(
        description="array of strings, default value, no match",
        template=r"{{ a | find_index: 'foo' }}",
        expect="",
        globals={"a": ["x", "y", "zoo"]},
    ),
    # Case(
    #     description="array of ints, default value",
    #     template=r"{{ a | find_index: 3 }}",
    #     expect="0",
    #     globals={"a": [1, 2, 3]},
    # ),
    Case(
        description="mixed array, default value",
        template=r"{{ a | find_index: 'z' }}",
        expect="",
        globals={"a": ["x", None, "z", False, True]},
    ),
    Case(
        description="string input, default value, match",
        template=r"{{ a | find_index: 'z' }}",
        expect="0",
        globals={"a": "zoo"},
    ),
    Case(
        description="string input, string value, match",
        template=r"{{ a | find_index: 'z', 'z' }}",
        expect="0",
        globals={"a": "zoo"},
    ),
    Case(
        description="string input, string value, no match",
        template=r"{{ a | find_index: 'z', 'y' }}",
        expect="",
        globals={"a": "zoo"},
    ),
    Case(
        description="hash input, default value, match",
        template=r"{{ a | find_index: 'z' }}",
        expect="0",
        globals={"a": {"z": 42}},
    ),
    Case(
        description="hash input, default value, no match",
        template=r"{{ a | find_index: 'foo' }}",
        expect="",
        globals={"a": {"z": 42}},
    ),
    Case(
        description="hash input, int value, match",
        template=r"{{ a | find_index: 'z', 42 }}",
        expect="0",
        globals={"a": {"z": 42}},
    ),
    Case(
        description="hash input, explicit nil, match",
        template=r"{{ a | find_index: 'z', nil }}",
        expect="",
        globals={"a": {"z": None}},
    ),
    Case(
        description="array of hashes, explicit nil, match",
        template=r"{{ a | find_index: 'z', nil }}",
        expect="",
        globals={"a": ["foo", "bar", {"z": None}]},
    ),
    Case(
        description="array of hashes, int value, match",
        template=r"{{ a | find_index: 'z', 42 }}",
        expect="1",
        globals={"a": [{"x": 99}, {"z": 42, "foo": "bar"}]},
    ),
    Case(
        description="array of hashes, with a nil",
        template=r"{% assign b = a | find_index: 'z', 42 %}{{ b.foo }}",
        expect="",
        globals={"a": [{"x": 99}, None, {"z": 42, "foo": "bar"}]},
    ),
]
