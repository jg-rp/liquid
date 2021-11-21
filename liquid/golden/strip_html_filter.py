"""Golden tests cases for testing liquid's built-in `strip_html` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="some HTML markup",
        template=r"{{ s | strip_html }}",
        expect="Have you read Ulysses &amp; &#20;?",
        globals={"s": "Have <em>you</em> read <strong>Ulysses</strong> &amp; &#20;?"},
    ),
    Case(
        description="some HTML markup with HTML comment",
        template=r"{{ s | strip_html }}",
        expect="you read Ulysses &amp; &#20;?",
        globals={
            "s": "<!-- Have --><em>you</em> read <strong>Ulysses</strong> &amp; &#20;?"
        },
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | strip_html }}",
        expect="5",
    ),
    Case(
        description="unexpected argument",
        template=r'{{ "hello" | strip_html: 5 }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | strip_html }}",
        expect="",
    ),
]
