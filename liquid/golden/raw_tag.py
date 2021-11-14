"""Golden tests cases for testing liquid's `raw` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="literal",
        template=r"{% raw %}foo{% endraw %}",
        expect="foo",
    ),
    Case(
        description="statement",
        template=r"{% raw %}{{ foo }}{% endraw %}",
        expect=r"{{ foo }}",
    ),
    Case(
        description="tag",
        template=r"{% raw %}{% assign x = 1 %}{% endraw %}",
        expect=r"{% assign x = 1 %}",
    ),
    Case(
        description="partial tag",
        template=r"{% raw %} %} {% }} {{ {% endraw %}",
        expect=r" %} {% }} {{ ",
    ),
    Case(
        description="continue after raw",
        template=r"{% raw %} {% some raw content %} {% endraw %}a literal",
        expect=r" {% some raw content %} a literal",
    ),
]
