"""Golden tests cases for testing liquid's `unless` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="literal false condition",
        template=r"{% unless false %}foo{% endunless %}",
        expect="foo",
    ),
    Case(
        description="literal true condition",
        template=r"{% unless true %}foo{% endunless %}",
        expect="",
    ),
    Case(
        description="blocks that contain only whitespace are not rendered",
        template=r"{% unless false %}  {% endunless %}",
        expect="",
    ),
    Case(
        description="alternative block",
        template=r"{% unless true %}foo{% else %}bar{% endunless %}",
        expect="bar",
    ),
    Case(
        description="conditional alternative block",
        template=r"{% unless true %}foo{% elsif true %}bar{% endunless %}",
        expect="bar",
    ),
    Case(
        description="conditional alternative block with default",
        template=(
            r"{% unless true %}foo"
            r"{% elsif false %}bar"
            r"{% else %}hello"
            r"{% endunless %}"
        ),
        expect="hello",
    ),
    Case(
        description=("zero is not equal to false"),
        template=(r"{% unless 0 == false %}Hello{% else %}Goodbye{% endunless %}"),
        expect="Hello",
    ),
    Case(
        description=("zero is truthy"),
        template=(r"{% unless 0 %}Hello{% else %}Goodbye{% endunless %}"),
        expect="Goodbye",
    ),
    Case(
        description=("one is not equal to true"),
        template=(r"{% unless 1 == true %}Hello{% else %}Goodbye{% endunless %}"),
        expect="Hello",
    ),
    Case(
        description="array is equal to array",
        template=(
            "{% assign x = 'a,b,c' | split: ',' %}"
            "{% assign y = 'a,b,c' | split: ',' %}"
            "{% unless x == y %}true{% else %}false{% endunless %}"
        ),
        expect="false",
    ),
    Case(
        description="array is equal to array from context",
        template=(
            "{% assign y = 'a,b,c' | split: ',' %}"
            "{% unless x == y %}true{% else %}false{% endunless %}"
        ),
        globals={"x": ["a", "b", "c"]},
        expect="false",
    ),
    Case(
        description="else tag expressions are ignored",
        template="{% unless true %}1{% else nonsense %}2{% endunless %}",
        globals={},
        expect="2",
        error=False,
        strict=True,
        future=True,
    ),
    Case(
        description="extra else blocks are ignored",
        template="{% unless true %}1{% else %}2{% else %}3{% endunless %}",
        globals={},
        expect="2",
        error=False,
        strict=True,
        future=True,
    ),
    Case(
        description="extra elsif blocks are ignored",
        template="{% unless true %}1{% else %}2{% elsif true %}3{% endunless %}",
        globals={},
        expect="2",
        error=False,
        strict=True,
        future=True,
    ),
]
