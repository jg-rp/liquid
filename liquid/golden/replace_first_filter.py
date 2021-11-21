"""Golden tests cases for testing liquid's built-in `replace_first` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="replace substrings",
        template=(
            r'{{ "Take my protein pills and put my helmet on" '
            r'| replace_first: "my", "your" }}'
        ),
        expect="Take your protein pills and put my helmet on",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | replace_first: 'rain', 'foo' }}",
        expect="5",
    ),
    Case(
        description="argument not a string",
        template=r'{{ "hello5" | replace_first: 5, "your" }}',
        expect="helloyour",
    ),
    Case(
        description="missing argument",
        template=r'{{ "hello" | replace_first: "ll" }}',
        expect="heo",
    ),
    Case(
        description="missing arguments",
        template=r'{{ "hello" | replace_first }}',
        expect="",
        error=True,
    ),
    Case(
        description="too many arguments",
        template=r'{{ "hello" | replace_first: "how", "are", "you" }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r'{{ nosuchthing | replace_first: "my", "your" }}',
        expect="",
    ),
    Case(
        description="undefined first argument",
        template=r'{{ "Take my protein" | replace_first: nosuchthing, "#" }}',
        expect="#Take my protein",
    ),
    Case(
        description="undefined second argument",
        template=(
            r'{{ "Take my protein pills and put my helmet on" '
            r'| replace_first: "my", nosuchthing }}'
        ),
        expect="Take  protein pills and put my helmet on",
    ),
]
