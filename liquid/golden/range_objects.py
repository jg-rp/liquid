"""Golden tests cases for testing range objects."""

from liquid.golden.case import Case

cases = [
    Case(
        description="start is not a number",
        template=r"{{ (start..end) }}",
        globals={"start": "foo", "end": 5},
        expect="",
        error=True,
    ),
    Case(
        description="end is not a number",
        template=r"{{ (start..end) }}",
        globals={"start": "1", "end": "foo"},
        expect="",
        error=True,
    ),
    Case(
        description="end is less than start",
        template=r"{{ (start..end) | join: '#' }}",
        globals={"start": 5, "end": 1},
        expect="",
    ),
]
