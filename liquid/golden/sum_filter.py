"""Golden tests cases for testing liquid's built-in `sum` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="empty sequence",
        template=r"{{ a | sum }}",
        expect="0",
        globals={"a": []},
    ),
    Case(
        description="only zeros",
        template=r"{{ a | sum }}",
        expect="0",
        globals={"a": [0, 0, 0]},
    ),
    Case(
        description="ints",
        template=r"{{ a | sum }}",
        expect="6",
        globals={"a": [1, 2, 3]},
    ),
    Case(
        description="negative ints",
        template=r"{{ a | sum }}",
        expect="-6",
        globals={"a": [-1, -2, -3]},
    ),
    Case(
        description="floats",
        template=r"{{ a | sum }}",
        expect="0.6",
        globals={"a": [0.1, 0.2, 0.3]},
    ),
    Case(
        description="floats and ints",
        template=r"{{ a | sum }}",
        expect="6.6",
        globals={"a": [0.1, 0.2, 0.3, 1, 2, 3]},
    ),
    Case(
        description="negative strings",
        template=r"{{ a | sum }}",
        expect="-6",
        globals={"a": ["-1", "-2", "-3"]},
    ),
    Case(
        description="positive and negative ints",
        template=r"{{ a | sum }}",
        expect="5",
        globals={"a": [-2, -3, 10]},
    ),
]
