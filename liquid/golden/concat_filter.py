"""Golden tests cases for testing liquid's built-in `concat` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="range literal concat filter left value",
        template=r"{{ (1..3) | concat: foo }}",
        expect="123567",
        globals={"foo": [5, 6, 7]},
    ),
]
