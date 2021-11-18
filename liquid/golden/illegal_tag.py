"""Golden tests cases for testing illegal tags."""

from liquid.golden.case import Case

cases = [
    Case(
        description="unknown tag",
        template=r"{% nosuchthing %}",
        expect="",
        error=True,
    ),
]
