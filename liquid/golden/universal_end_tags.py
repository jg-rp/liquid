"""Universal `end` tag test cases."""

from liquid.golden.case import Case

cases = [
    Case(
        description="end if",
        template=r"{% if true %}foo{% end %}",
        expect="foo",
        future=True,
    ),
    Case(
        description="end if, else",
        template=r"{% if false %}foo{% else %}bar{% end %}",
        expect="bar",
        future=True,
    ),
    Case(
        description="end if, elsif",
        template=r"{% if false %}foo{% elsif true %}bar{% end %}",
        expect="bar",
        future=True,
    ),
    Case(
        description="end if, whitespace control",
        template="{% if true -%}\nfoo\n{%- end %}",
        expect="foo",
        future=True,
    ),
    Case(
        description="end for",
        template=r"{% for x in (1..2) %}{{ x }},{% end %}",
        expect="1,2,",
        future=True,
    ),
    Case(
        description="end for, else",
        template=r"{% for x in a %}{{ x }},{% else %}bar{% end %}",
        expect="bar",
        future=True,
        globals={"a": []},
    ),
    Case(
        description="end if, nested universal",
        template="\n".join(
            [
                r"{% if true %}",
                r"foo",
                r"{% if true %}",
                r"bar",
                r"{% end %}",
                r"{% end %}",
            ]
        ),
        expect="\nfoo\n\nbar\n\n",
        future=True,
    ),
    Case(
        description="end if, alternative, nested universal",
        template="\n".join(
            [
                r"{% if false %}",
                r"foo",
                r"{% else %}",
                r"{% if true %}",
                r"bar",
                r"{% end %}",
                r"{% end %}",
            ]
        ),
        expect="\n\nbar\n\n",
        future=True,
    ),
    Case(
        description="end if, nested inner",
        template="\n".join(
            [
                r"{% if true %}",
                r"foo",
                r"{% if true %}",
                r"bar",
                r"{% end %}",
                r"{% endif %}",
            ]
        ),
        expect="\nfoo\n\nbar\n\n",
        future=True,
    ),
    Case(
        description="end if, nested outer",
        template="\n".join(
            [
                r"{% if true %}",
                r"foo",
                r"{% if true %}",
                r"bar",
                r"{% endif %}",
                r"{% end %}",
            ]
        ),
        expect="\nfoo\n\nbar\n\n",
        future=True,
    ),
    Case(
        description="liquid, end if",
        template="\n".join(
            [
                r"{% liquid ",
                r"if true",
                r"    echo 'foo'",
                r"end",
                r"%}",
            ]
        ),
        expect="foo",
        future=True,
    ),
]
