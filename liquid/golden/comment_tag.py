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
]
