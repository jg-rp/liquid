"""Golden tests cases for testing liquid's built-in `escape_once` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="make HTML-safe",
        template=r'{{ "&lt;p&gt;test&lt;/p&gt;" | escape_once }}',
        expect="&lt;p&gt;test&lt;/p&gt;",
    ),
    Case(
        description="make HTML-safe from mixed safe and markup.",
        template=r'{{ "&lt;p&gt;test&lt;/p&gt;<p>test</p>" | escape_once }}',
        expect="&lt;p&gt;test&lt;/p&gt;&lt;p&gt;test&lt;/p&gt;",
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | escape_once }}",
        expect="5",
    ),
    Case(
        description="unexpected argument",
        template=r'{{ "HELLO" | escape_once: 5 }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | escape_once }}",
        expect="",
    ),
]
