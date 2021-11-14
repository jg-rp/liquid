"""Golden tests cases for testing liquid's `decrement` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="named counter",
        template=r"{% decrement foo %}{{ foo }} {% decrement foo %}{{ foo }}",
        expect="-1-1 -2-2",
    ),
    Case(
        description="increment and decrement named counter",
        template=r"{% decrement foo %} {% decrement foo %} {% increment foo %}",
        expect="-1 -2 -2",
    ),
]
