"""Golden tests cases for testing liquid's `increment` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="named counter",
        template=r"{% increment foo %} {% increment foo %} {% increment foo %}",
        expect="0 1 2",
    ),
    Case(
        description="incrementing counter renders before incrementing",
        template=r"{% increment foo %} {{ foo }}",
        expect="0 1",
    ),
    Case(
        description="multiple named counters",
        template=(
            r"{% increment foo %} "
            r"{% increment bar %} "
            r"{% increment foo %} "
            r"{% increment bar %}"
        ),
        expect="0 0 1 1",
    ),
    Case(
        description="assign and increment",
        template=(
            r"{% assign foo = 5 %}"
            r"{{ foo }} "
            r"{% increment foo %} "
            r"{% increment foo %} "
            r"{{ foo }}"
        ),
        expect="5 0 1 5",
    ),
    Case(
        description="named counters are in scope for subsequent expressions",
        template=(
            r"{% increment foo %} "
            r"{% increment foo %} "
            r"{% if foo > 0 %}"
            r"{{ foo }}"
            r"{% endif %}"
        ),
        expect="0 1 2",
    ),
]
