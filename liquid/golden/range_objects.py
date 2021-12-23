"""Golden tests cases for testing range objects."""

from liquid.golden.case import Case

cases = [
    Case(
        description="start is not a number",
        template=r"{{ (start..end) | join: '#' }}",
        globals={"start": "foo", "end": 5},
        expect="0#1#2#3#4#5",
    ),
    Case(
        description="end is not a number",
        template=r"{{ (start..end) | join: '#' }}",
        globals={"start": "1", "end": "foo"},
        expect="",
    ),
    Case(
        description="end is less than start",
        template=r"{{ (start..end) | join: '#' }}",
        globals={"start": 5, "end": 1},
        expect="",
    ),
    Case(
        description="start is negative",
        template=r"{{ (start..end) | join: '#' }}",
        globals={"start": -5, "end": 1},
        expect="-5#-4#-3#-2#-1#0#1",
    ),
    Case(
        description="start and end are negative",
        template=r"{{ (start..end) | join: '#' }}",
        globals={"start": -5, "end": -2},
        expect="-5#-4#-3#-2",
    ),
]
