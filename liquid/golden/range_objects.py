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
    Case(
        description="integer literals",
        template=r"{{ (1..5) | join: '#' }}",
        globals={},
        expect="1#2#3#4#5",
    ),
    Case(
        description="whitespace before start",
        template="{{ ( \n\t1..5) | join: '#' }}",
        globals={},
        expect="1#2#3#4#5",
    ),
    Case(
        description="whitespace after stop",
        template="{{ (1..5 \n\t) | join: '#' }}",
        globals={},
        expect="1#2#3#4#5",
    ),
    Case(
        description="whitespace before dots",
        template="{{ (1 \n\t..5) | join: '#' }}",
        globals={},
        expect="1#2#3#4#5",
    ),
    Case(
        description="whitespace after dots",
        template="{{ (1.. \n\t5) | join: '#' }}",
        globals={},
        expect="1#2#3#4#5",
    ),
    Case(
        description="whitespace before and after dots",
        template="{{ (1 .. 5) | join: '#' }}",
        globals={},
        expect="1#2#3#4#5",
    ),
    Case(
        description="whitespace before and after dots, for loop",
        template=r"{% for x in (1 .. 5) %}{{ x }},{% endfor %}",
        globals={},
        expect="1,2,3,4,5,",
        strict=True,
    ),
]
