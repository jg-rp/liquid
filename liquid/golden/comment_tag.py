"""Golden tests cases for testing liquid's `comment` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="don't render comments",
        template=r"{% comment %}foo{% endcomment %}",
        expect="",
    ),
    Case(
        description="respect whitespace control in comments",
        template="\n{%- comment %}foo{% endcomment -%}\t \r",
        expect="",
    ),
    Case(
        description="don't render comments with tags",
        template=(
            r"{% comment %}"
            r"{% if true %}"
            r"{{ title }}"
            r"{% endif %}"
            r"{% endcomment %}"
        ),
        expect="",
    ),
    Case(
        description="comment inside liquid tag",
        template="\n".join(
            [
                r"{% liquid",
                r"    if 1 != 1",
                r"    comment",
                r"    else",
                r"    echo 123",
                r"    endcomment",
                r"    endif",
                r"%}",
            ]
        ),
        expect="",
    ),
    Case(
        description="commented tags are not parsed",
        template=(
            r"{% comment %}"
            r"    {% if true %}"
            r"    {% if ... %}"
            r"    {%- for ? -%}"
            r"    {% while true %}"
            r"    {%"
            r"    unless if"
            r"    %}"
            r"    {% endcase %}"
            r"{% endcomment %}"
        ),
        expect="",
    ),
    Case(
        description="malformed tags are not parsed",
        template=r"{% comment %}{% assign foo = '1'{% endcomment %}",
        expect="",
        error=True,
    ),
    Case(
        description="incomplete tags are not parsed",
        template=r"{% comment %}{% {{ {%- endcomment %}",
        expect="",
        error=True,
    ),
    Case(
        description="nested comment blocks",
        template=(
            r"{% comment %}"
            r"    {% comment %}"
            r"    {% comment %}{%    endcomment     %}"
            r"    {% endcomment %}"
            r"{% endcomment %}"
        ),
        expect="",
        future=True,
    ),
    Case(
        description="nested comment blocks, with nested tags",
        template=(
            r"{% comment %}"
            r"    {% comment %}"
            r"    {% comment %}{% if true %}hello{%endif%}{%    endcomment     %}"
            r"    {% endcomment %}"
            r"{% endcomment %}"
        ),
        expect="",
        future=True,
    ),
    Case(
        description="unclosed nested comment blocks",
        template=(
            r"{% comment %}"
            r"    {% comment %}"
            r"    {% comment %}"
            r"    {% endcomment %}"
            r"{% endcomment %}"
        ),
        expect="",
        error=True,
        future=True,
    ),
    Case(
        description="raw inside comment block",
        template=(
            r"{% comment %}"
            r"    {% raw %}"
            r"    {% endcomment %}"
            r"    {% endraw %}"
            r"{% endcomment %}"
        ),
        expect="",
    ),
]
