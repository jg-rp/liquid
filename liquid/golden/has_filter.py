"""Test cases for the standard `has` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="array of strings, default value",
        template=r"{{ a | has: 'z' }}",
        expect="true",
        globals={"a": ["x", "y", "z"]},
    ),
    Case(
        description="array of strings, default value, substring match",
        template=r"{{ a | has: 'z' }}",
        expect="true",
        globals={"a": ["x", "y", "zoo"]},
    ),
    Case(
        description="array of strings, default value, no match",
        template=r"{{ a | has: ':(' }}",
        expect="false",
        globals={"a": ["x", "y", "z"]},
    ),
    Case(
        description="array of ints, default value",
        template=r"{{ a | has: 2 }}",
        expect="true",
        globals={"a": [1, 2, 3]},
    ),
    Case(
        description="array of ints, string argument, default value",
        template=r"{{ a | has: '2' }}",
        expect="",
        globals={"a": [1, 2, 3]},
        error=True,
    ),
    Case(
        description="mixed array, default value",
        template=r"{{ a | has: 'z' }}",
        expect="",
        globals={"a": ["x", None, "z", False, True]},
    ),
    Case(
        description="string input, default value, match",
        template=r"{{ a | has: 'z' }}",
        expect="true",
        globals={"a": "zoo"},
    ),
    Case(
        description="string input, default value, no match",
        template=r"{{ a | has: 'z' }}",
        expect="false",
        globals={"a": "foo"},
    ),
    Case(
        description="hash input, default value, match",
        template=r"{{ a | has: 'z' }}",
        expect="true",
        globals={"a": {"z": 42}},
    ),
    Case(
        description="hash input, default value, no match",
        template=r"{{ a | has: 'z' }}",
        expect="false",
        globals={"a": {"x": 42}},
    ),
    Case(
        description="hash input, int value, match",
        template=r"{{ a | has: 'z', 42 }}",
        expect="true",
        globals={"a": {"z": 42}},
    ),
    Case(
        description="hash input, int value, no match",
        template=r"{{ a | has: 'z', 99 }}",
        expect="false",
        globals={"a": {"z": 42}},
    ),
    Case(
        description="hash input, string value, no type coercion",
        template=r"{{ a | has: 'z', '42' }}",
        expect="false",
        globals={"a": {"z": 42}},
    ),
    Case(
        description="hash input, explicit nil, no match",
        template=r"{{ a | has: 'z', nil }}",
        expect="true",
        globals={"a": {"z": 42}},
    ),
    Case(
        description="hash input, explicit nil, match",
        template=r"{{ a | has: 'z', nil }}",
        expect="false",
        globals={"a": {"z": None}},
    ),
    Case(
        description="hash input, false value, match",
        template=r"{{ a | has: 'z', false }}",
        expect="true",
        globals={"a": {"z": False}},
    ),
    Case(
        description="array of hashes, int value, match",
        template=r"{{ a | has: 'z', 42 }}",
        expect="true",
        globals={"a": [{"x": 99}, {"z": 42}]},
    ),
    Case(
        description="array of hashes, int value, no match",
        template=r"{{ a | has: 'z', 7 }}",
        expect="false",
        globals={"a": [{"x": 99}, {"z": 42}]},
    ),
    Case(
        description="array of hashes, with a nil",
        template=r"{{ a | has: 'z', 42 }}",
        expect="",
        globals={"a": [{"x": 99}, None, {"z": 42}]},
    ),
    Case(
        description="array of hashes, nil property",
        template=r"{{ a | has: nil }}",
        expect="false",
        globals={"a": [{"x": 99}, {"z": 42}]},
    ),
    Case(
        description="array of hashes, int property",
        template=r"{{ a | has: 42 }}",
        expect="false",
        globals={"a": [{"x": 99}, {"z": 42}]},
    ),
    Case(
        description="array of hashes, false property",
        template=r"{{ a | has: false }}",
        expect="false",
        globals={"a": [{"x": 99}, {"z": 42}]},
    ),
]
