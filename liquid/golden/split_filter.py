"""Golden tests cases for testing liquid's built-in `split` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="split string",
        template=r'{{ "Hi, how are you today?" | split: " " | join: "#" }}',
        expect="Hi,#how#are#you#today?",
    ),
    Case(
        description="not a string",
        template=r"{{ 56 | split: ' ' | first }}",
        expect="56",
    ),
    Case(
        description="argument not a string",
        template=r'{{ "hello th1ere" | split: 1 | join: "#" }}',
        expect="hello th#ere",
    ),
    Case(
        description="missing argument",
        template=r'{{ "hello there" | split }}',
        expect="",
        error=True,
    ),
    Case(
        description="too many arguments",
        template=r'{{ "hello there" | split: " ", "," }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r'{{ nosuchthing | split: " " }}',
        expect="",
    ),
    Case(
        description="undefined argument",
        template=r'{{ "Hello there" | split: nosuchthing | join: "#" }}',
        expect="H#e#l#l#o# #t#h#e#r#e",
    ),
]
