"""Golden tests cases for testing liquid's built-in `escape` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="make HTML-safe",
        template=r'{{ "<p>test</p>" | escape }}',
        expect="&lt;p&gt;test&lt;/p&gt;",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | escape }}",
        expect="5",
    ),
    Case(
        description="unexpected argument",
        template=r'{{ "HELLO" | escape: 5 }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | escape }}",
        expect="",
    ),
]
