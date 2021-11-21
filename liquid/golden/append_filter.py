"""Golden tests cases for testing liquid's built-in `append` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="concat",
        template=r'{{ "hello" | append: "there" }}',
        expect="hellothere",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | append: 'there' }}",
        expect="5there",
    ),
    Case(
        description="argument not a string",
        template=r'{{ "hello" | append: 5 }}',
        expect="hello5",
    ),
    Case(
        description="missing argument",
        template=r'{{ "hello" | append }}',
        expect="",
        error=True,
    ),
    Case(
        description="too many arguments",
        template=r'{{ "hello" | append: "how", "are", "you" }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r'{{ nosuchthing | append: "hi" }}',
        expect="hi",
    ),
    Case(
        description="undefined argument",
        template=r'{{ "hi" | append: nosuchthing }}',
        expect="hi",
    ),
]
