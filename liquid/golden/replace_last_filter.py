"""Golden tests cases for testing liquid's built-in `replace_last` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="replace substrings",
        template=(
            r'{{ "Take my protein pills and put my helmet on" '
            r'| replace_last: "my", "your" }}'
        ),
        expect="Take my protein pills and put your helmet on",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | replace_last: 'rain', 'foo' }}",
        expect="5",
    ),
    Case(
        description="argument not a string",
        template=r'{{ "hello5" | replace_last: 5, "your" }}',
        expect="helloyour",
    ),
    Case(
        description="missing argument",
        template=r'{{ "hello" | replace_last: "ll" }}',
        expect="",
        error=True,
    ),
    Case(
        description="missing arguments",
        template=r'{{ "hello" | replace_last }}',
        expect="",
        error=True,
    ),
    Case(
        description="too many arguments",
        template=r'{{ "hello" | replace_last: "how", "are", "you" }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r'{{ nosuchthing | replace_last: "my", "your" }}',
        expect="",
    ),
    Case(
        description="undefined first argument",
        template=r'{{ "Take my protein" | replace_last: nosuchthing, "#" }}',
        expect="Take my protein#",
    ),
    Case(
        description="undefined second argument",
        template=(
            r'{{ "Take my protein pills and put my helmet on" '
            r'| replace_last: "my", nosuchthing }}'
        ),
        expect="Take my protein pills and put  helmet on",
    ),
]
