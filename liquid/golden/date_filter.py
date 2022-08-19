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
    Case(
        description="literal percent",
        template=r"{{ 'March 14, 2016' | date: '%%%b %d, %y' }}",
        expect="%Mar 14, 16",
    ),
    Case(
        description="timestamp integer",
        template=r"{{ 1152098955 | date: '%m/%d/%Y' }}",
        expect="07/05/2006",
    ),
    Case(
        description="timestamp string",
        template=r"{{ '1152098955' | date: '%m/%d/%Y' }}",
        expect="07/05/2006",
    ),
    # Case(
    #     description="negative timestamp integer",
    #     template=r"{{ -1152098955 | date: '%m/%d/%Y' }}",
    #     expect="06/29/1933",
    # ),
    Case(
        description="negative timestamp string",
        template=r"{{ '-1152098955' | date: '%m/%d/%Y' }}",
        expect="-1152098955",
    ),
]
