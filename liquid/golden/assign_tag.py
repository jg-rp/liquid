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
    Case(
        description="assign to variable with a hyphen",
        template=r"{% assign some-thing = 'foo' %}{{ some-thing }}",
        expect="foo",
    ),
    Case(
        description="assign an existing array",
        template=r"{% assign foo = bar %}{{ foo[0] }}/{{ foo[1] }}",
        expect="a/b",
        globals={"bar": ["a", "b", "c"]},
    ),
    Case(
        description="assign an item from an existing object with quoted notation",
        template=r"{% assign foo = bar['baz'] %}{{ foo }}",
        expect="hello",
        globals={"bar": {"baz": "hello"}},
    ),
    Case(
        description="assign with quoted notation and extra whitespace",
        template=r"{% assign foo = bar[ 'baz'  ] %}{{ foo }}",
        expect="hello",
        globals={"bar": {"baz": "hello"}},
    ),
]
