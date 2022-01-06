"""Golden tests cases for testing liquid's `assign` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="assign a filtered literal",
        template=r"{% assign foo = 'foo' | upcase %}{{ foo }}",
        expect="FOO",
    ),
    Case(
        description="local variables shadow global variables",
        template=r"{{ foo }}{% assign foo = 'foo' | upcase %}{{ foo }}",
        expect="barFOO",
        globals={"foo": "bar"},
    ),
    Case(
        description="assign a range literal",
        template=r"{% assign foo = (1..3) %}{{ foo | join: '#' }}",
        expect="1#2#3",
    ),
]
