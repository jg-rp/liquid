"""Golden tests cases for testing liquid's `#` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="with whitespace control and padding",
        template=r"{%- # some comment -%}",
        expect="",
    ),
    Case(
        description="with whitespace control no padding",
        template=r"{%-# some comment -%}",
        expect="",
    ),
    Case(
        description="no whitespace control with padding",
        template=r"{% # some comment %}",
        expect="",
    ),
    Case(
        description="no whitespace control no padding",
        template=r"{%# some comment %}",
        expect="",
    ),
    Case(
        description="no padding after the hash",
        template=r"{%#some comment %}",
        expect="",
    ),
    Case(
        description="empty",
        template=r"{%#%}",
        expect="",
    ),
    Case(
        description="liquid tag",
        template="\n".join(
            [
                r"{% liquid ",
                r"  # first comment line",
                r"  # second comment line",
                r"",
                r"  # another comment line",
                r"  echo 'Hello '",
                r"",
                r"  # more comments",
                r"  echo 'goodbye'",
                r"-%}",
            ]
        ),
        expect="Hello goodbye",
    ),
    Case(
        description="multiple lines",
        template="\n".join(
            [
                "{%-",
                "  # spread inline comments",
                "  # over multiple lines",
                "-%}",
            ]
        ),
        expect="",
    ),
    Case(
        description="lots of hashes in a liquid tag",
        template="\n".join(
            [
                r"{% liquid",
                r"  ##########################",
                r"  # spread inline comments #",
                r"  ##########################",
                r"-%}",
            ]
        ),
        expect="",
    ),
    Case(
        description="enforce leading hash",
        template="\n".join(
            [
                "{%-",
                "  # spread inline comments",
                "  over multiple lines",
                "-%}",
            ]
        ),
        expect="",
        error=True,
    ),
    Case(
        description="can't comment tags",
        template="{%- # {% echo 'hello world' %} -%}",
        expect=" -%}",
    ),
]
