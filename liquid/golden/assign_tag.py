"""Golden tests cases for testing liquid's `assign` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="assign a filtered literal",
        template="{% assign foo = 'foo' | upcase %}{{ foo }}",
        expect="FOO",
    ),
    Case(
        description="local variables shadow global variables",
        template="{{ foo }}{% assign foo = 'foo' | upcase %}{{ foo }}",
        expect="barFOO",
        globals={"foo": "bar"},
    ),
    Case(
        description="assign a range literal",
        template="{% assign foo = (1..3) %}{{ foo }}",
        expect="1..3",
    ),
]
