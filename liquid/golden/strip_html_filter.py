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
    Case(
        description="html block",
        template=r"{{ s | strip_html }}",
        expect="test",
        globals={"s": "<div>test</div>"},
    ),
    Case(
        description="html block with id",
        template=r"{{ s | strip_html }}",
        expect="test",
        globals={"s": "<div id='test'>test</div>"},
    ),
    Case(
        description="script block",
        template=r"{{ s | strip_html }}",
        expect="",
        globals={
            "s": "<script type='text/javascript'>document.write('some stuff');</script>"
        },
    ),
    Case(
        description="style block",
        template=r"{{ s | strip_html }}",
        expect="",
        globals={"s": "<style type='text/css'>foo bar</style>"},
    ),
    Case(
        description="html block with newline",
        template=r"{{ s | strip_html }}",
        expect="test",
        globals={"s": "<div\nclass='multiline'>test</div>"},
    ),
    Case(
        description="html comment with newline",
        template=r"{{ s | strip_html }}",
        expect="test",
        globals={"s": "<!-- foo bar \n test -->test"},
    ),
]
