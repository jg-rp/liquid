"""Golden tests cases for testing liquid's built-in `replace` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="replace substrings",
        template=(
            r'{{ "Take my protein pills and put my helmet on" '
            r'| replace: "my", "your" }}'
        ),
        expect="Take your protein pills and put your helmet on",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | replace: 'rain', 'foo' }}",
        expect="5",
    ),
    Case(
        description="left value is an object",
        template=r"{{ a | replace: '{', '!' }}",
        expect="!}",
        globals={"a": {}},
    ),
    Case(
        description="argument not a string",
        template=r'{{ "hello" | replace: 5, "your" }}',
        expect="hello",
    ),
    Case(
        description="missing argument",
        template=r'{{ "hello" | replace: "ll" }}',
        expect="heo",
    ),
    Case(
        description="missing arguments",
        template=r'{{ "hello" | replace }}',
        expect="",
        error=True,
    ),
    Case(
        description="too many arguments",
        template=r'{{ "hello" | replace: "how", "are", "you" }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r'{{ nosuchthing | replace: "my", "your" }}',
        expect="",
    ),
    Case(
        description="undefined first argument",
        template=r'{{ "Take my protein" | replace: nosuchthing, "#" }}',
        expect="#T#a#k#e# #m#y# #p#r#o#t#e#i#n#",
    ),
    Case(
        description="undefined second argument",
        template=(
            r'{{ "Take my protein pills and put my helmet on" '
            r'| replace: "my", nosuchthing }}'
        ),
        expect="Take  protein pills and put  helmet on",
    ),
]
