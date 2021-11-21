"""Golden tests cases for testing liquid's built-in `date` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="well formed string",
        template=r"{{ 'March 14, 2016' | date: '%b %d, %y' }}",
        expect="Mar 14, 16",
    ),
    Case(
        description="too many arguments",
        template=r"{{ 'March 14, 2016' | date: '%b %d, %y', 'foo' }}",
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | date: '%b %d, %y' }}",
        expect="",
    ),
    Case(
        description="missing argument",
        template=r"{{ 'March 14, 2016' | date }}",
        expect="",
        error=True,
    ),
    Case(
        description="undefined argument",
        template=r"{{ 'March 14, 2016' | date: nosuchthing }}",
        expect="March 14, 2016",
    ),
]
