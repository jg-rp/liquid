"""Golden tests cases for testing liquid's built-in `truncate` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="default end",
        template=r'{{ "Ground control to Major Tom." | truncate: 20 }}',
        expect="Ground control to...",
    ),
    Case(
        description="custom end",
        template=r'{{ "Ground control to Major Tom." | truncate: 25, ", and so on" }}',
        expect="Ground control, and so on",
    ),
    Case(
        description="no end",
        template=r'{{ "Ground control to Major Tom." | truncate: 20, "" }}',
        expect="Ground control to Ma",
    ),
    Case(
        description="string is shorter than length",
        template=r'{{ "Ground control" | truncate: 20 }}',
        expect="Ground control",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | truncate: 10 }}",
        expect="5",
    ),
    Case(
        description="too many arguments",
        template=r'{{ "hello" | truncate: 5, "foo", "bar" }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | truncate: 5 }}",
        expect="",
    ),
    Case(
        description="undefined first argument",
        template=r'{{ "Ground control to Major Tom." | truncate: nosuchthing }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined second argument",
        template=r'{{ "Ground control to Major Tom." | truncate: 20, nosuchthing }}',
        expect="Ground control to Ma",
    ),
    Case(
        description="default length is 50",
        template=(
            r'{{ "Ground control to Major Tom. Ground control to Major Tom." '
            r"| truncate }}"
        ),
        expect="Ground control to Major Tom. Ground control to ...",
    ),
]
