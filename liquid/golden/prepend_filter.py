"""Golden tests cases for testing liquid's built-in `prepend` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="concat",
        template=r'{{ "hello" | prepend: "there" }}',
        expect="therehello",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | prepend: 'there' }}",
        expect="there5",
    ),
    Case(
        description="argument not a string",
        template=r'{{ "hello" | prepend: 5 }}',
        expect="5hello",
    ),
    Case(
        description="missing argument",
        template=r'{{ "hello" | prepend }}',
        expect="",
        error=True,
    ),
    Case(
        description="too many arguments",
        template=r'{{ "hello" | prepend: "how", "are", "you" }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r'{{ nosuchthing | prepend: "hi" }}',
        expect="hi",
    ),
    Case(
        description="undefined argument",
        template=r'{{ "hi" | prepend: nosuchthing }}',
        expect="hi",
    ),
]
