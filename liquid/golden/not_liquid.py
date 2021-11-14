"""Golden tests cases for testing text that is not liquid."""

from liquid.golden.case import Case

cases = [
    Case(
        description="plain text gets passed through unchanged",
        template="a literal string",
        expect="a literal string",
    ),
    Case(
        description="css text gets passed through unchanged",
        template=" div { font-weight: bold; } ",
        expect=" div { font-weight: bold; } ",
    ),
]
