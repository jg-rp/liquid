"""Golden tests cases for testing liquid's built-in `first` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="range literal first filter left value",
        template=r"{{ (1..3) | first }}",
        expect="1",
    ),
]
