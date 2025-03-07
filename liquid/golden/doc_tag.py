"""Golden tests cases for testing liquid's `doc` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="don't render docs",
        template=r"{% doc %}don't render me{% enddoc %}",
        expect="",
    ),
    Case(
        description="doc arguments is an error",
        template=r"{% doc hello %}don't render me{% enddoc %}",
        expect="",
        error=True,
    ),
    Case(
        description="doc tag block must be closed",
        template=r"{% doc %}don't render me",
        expect="",
        error=True,
    ),
    Case(
        description="doc text is not parsed",
        template=(
            r"{% doc %}"
            r"    {% if true %}"
            r"    {% if ... %}"
            r"    {%- for ? -%}"
            r"    {% while true %}"
            r"    {%"
            r"    unless if"
            r"    %}"
            r"    {% endcase %}"
            r"    {% raw %}"
            r"{% enddoc %}"
        ),
        expect="",
    ),
    Case(
        description="nested docs are not allowed",
        template=r"{% doc hello %}Hello{% doc %}{% enddoc %}",
        expect="",
        error=True,
    ),
    Case(
        description="docs containing unclosed tags are ok",
        template=r"{% doc %}{% assign x = y {% enddoc %}",
        expect="",
    ),
    Case(
        description="docs containing unclosed output are ok",
        template=r"{% doc %}{{ foo {% enddoc %}",
        expect="",
    ),
    Case(
        description="whitespace control",
        template="foo\n {%- doc %}I'm a doc comment{% enddoc -%}  \tbar",
        expect="foobar",
    ),
]
