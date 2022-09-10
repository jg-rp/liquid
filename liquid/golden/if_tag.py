"""Golden tests cases for testing liquid's `if` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="condition with literal consequence",
        template=r"{% if product.title == 'foo' %}bar{% endif %}",
        expect="bar",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="condition with literal consequence and literal alternative",
        template=r"{% if product.title == 'hello' %}bar{% else %}baz{% endif %}",
        expect="baz",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="condition with conditional alternative",
        template=(
            r"{% if product.title == 'hello' %}"
            r"foo"
            r"{% elsif product.title == 'foo' %}"
            r"bar"
            r"{% endif %}"
        ),
        expect="bar",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="condition with conditional alternative and final alternative",
        template=(
            r"{% if product.title == 'hello' %}"
            r"foo"
            r"{% elsif product.title == 'goodbye' %}"
            r"bar"
            r"{% else %}"
            r"baz"
            r"{% endif %}"
        ),
        expect="baz",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="non-empty hash is truthy",
        template=r"{% if product %}bar{% else %}foo{% endif %}",
        expect="bar",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="literal nil is falsy",
        template=r"{% if nil %}bar{% else %}foo{% endif %}",
        expect="foo",
    ),
    Case(
        description="undefined variables are falsy",
        template=r"{% if nosuchthing %}bar{% else %}foo{% endif %}",
        expect="foo",
    ),
    Case(
        description="nested condition in the consequence block",
        template=(
            r"{% if product %}"
            r"{% if title == 'Hello' %}"
            r"baz"
            r"{% endif %}"
            r"{% endif %}"
        ),
        expect="baz",
        globals={
            "product": {"title": "foo"},
            "title": "Hello",
        },
    ),
    Case(
        description="nested condition, alternative in the consequence block",
        template=(
            r"{% if product %}"
            r"{% if title == 'goodbye' %}"
            r"baz"
            r"{% else %}"
            r"hello"
            r"{% endif %}"
            r"{% endif %}"
        ),
        expect="hello",
        globals={"product": {"title": "foo"}, "title": "Hello"},
    ),
    Case(
        description="literal false condition",
        template=r"{% if false %}{% endif %}",
        expect="",
    ),
    Case(
        description="contains condition",
        template=r"{% if product.tags contains 'garden' %}baz{% endif %}",
        expect="baz",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="not equal condition",
        template=r"{% if product.title != 'foo' %}baz{% endif %}",
        expect="",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="alternate not equal condition",
        template=r"{% if product.title <> 'foo' %}baz{% endif %}",
        expect="",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="blocks that contain only whitespace are not rendered",
        template=r"{% if true %}  {% elsif false %} {% else %} {% endif %}",
        expect="",
    ),
    Case(
        description=(
            "blocks that contain only whitespace and comments are not rendered"
        ),
        template=(
            r"{% if true %} "
            r"{% comment %} this is blank {% endcomment %} "
            r"{% endif %}"
        ),
        expect="",
    ),
    Case(
        description="compare empty string literal to blank",
        template=r"{% if '' == blank %}is blank{% endif %}",
        expect="is blank",
        standard=False,
    ),
    Case(
        description="conditional alternative with default",
        template=(
            r"{% if false %}foo"
            r"{% elsif false %}bar"
            r"{% else %}hello"
            r"{% endif %}"
        ),
        expect="hello",
    ),
    Case(
        description="range equals range",
        template=(
            r"{% assign foo = (1..3) %}"
            r"{% if foo == (1..3) %}true"
            r"{% else %}false"
            r"{% endif %}"
        ),
        expect="true",
    ),
    Case(
        description="logical operators are right associative",
        template=(r"{% if true and false and false or true %}hello{% endif %}"),
        expect="",
    ),
    Case(
        description=("zero is not equal to false"),
        template=(r"{% if 0 == false %}Hello{% else %}Goodbye{% endif %}"),
        expect="Goodbye",
    ),
    Case(
        description=("zero is truthy"),
        template=(r"{% if 0 %}Hello{% else %}Goodbye{% endif %}"),
        expect="Hello",
    ),
    Case(
        description=("0.0 is truthy"),
        template=(r"{% if 0.0 %}Hello{% else %}Goodbye{% endif %}"),
        expect="Hello",
    ),
    Case(
        description=("one is not equal to true"),
        template=(r"{% if 1 == true %}Hello{% else %}Goodbye{% endif %}"),
        expect="Goodbye",
    ),
]
