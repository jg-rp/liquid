"""Golden tests cases for testing liquid's built-in `base64_encode` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="from string",
        template=r'{{ "_#/." | base64_encode }}',
        expect="XyMvLg==",
    ),
    Case(
        description="from string with URL unsafe",
        template=r"{{ a | base64_encode }}",
        expect=(
            "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXogQUJDREVGR0hJSktMTU5PUFFSU1RVV"
            "ldYWVogMTIzNDU2Nzg5MCAhQCMkJV4mKigpLT1fKy8/Ljo7W117fVx8"
        ),
        globals={
            "a": (
                r"abcdefghijklmnopqrstuvwxyz "
                r"ABCDEFGHIJKLMNOPQRSTUVWXYZ "
                r"1234567890 !@#$%^&*()-=_+/?.:;[]{}\|"
            )
        },
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | base64_encode }}",
        expect="NQ==",
    ),
    Case(
        description="unexpected argument",
        template=r'{{ "hello" | base64_encode: 5 }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | base64_encode }}",
        expect="",
    ),
]
