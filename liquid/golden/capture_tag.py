"""Golden tests cases for testing liquid's `capture` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="capture template literal and global variable",
        template=(
            r"{% capture greeting %}"
            r"Hello, {{ customer.first_name }}."
            r"{% endcapture %}"
            r"{{ greeting }}"
        ),
        expect="Hello, Holly.",
        globals={"customer": {"first_name": "Holly"}},
    ),
    Case(
        description="capture into a variable with a hyphen",
        template=(
            r"{% capture this-thing %}"
            r"Hello, {{ customer.first_name }}."
            r"{% endcapture %}"
            r"{{ this-thing }}"
        ),
        expect="Hello, Holly.",
        globals={"customer": {"first_name": "Holly"}},
    ),
    Case(
        description="assign to a variable from a captured variable",
        template=(
            r"{% capture some %}"
            r"hello"
            r"{% endcapture %}"
            r"{% assign other = some %}"
            r"{{ some }}-{{ other }}"
        ),
        expect="hello-hello",
    ),
]
