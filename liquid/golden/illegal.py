"""Golden tests cases for testing illegal tags."""

from liquid.golden.case import Case

cases = [
    Case(
        description="unknown tag",
        template=r"{% nosuchthing %}",
        expect="",
        error=True,
        strict=True,
    ),
    Case(
        description="no addition operator",
        template=r"{% assign x = 1 + 2 %}{{ x }}",
        expect="",
        error=True,
        strict=True,
    ),
    Case(
        description="no subtraction operator",
        template=r"{% assign x = 1 - 2 %}{{ x }}",
        expect="",
        error=True,
        strict=True,
    ),
    Case(
        description="no multiplication operator",
        template=r"{% assign x = 2 %}{{ x * 3 }}",
        expect="",
        error=True,
        strict=True,
    ),
]
