"""Golden tests cases for testing liquid's built-in `base64_url_safe_decode` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="from string",
        template=r'{{ "XyMvLg==" | base64_url_safe_decode }}',
        expect="_#/.",
    ),
    Case(
        description="from string with URL unsafe",
        template=r"{{ a | base64_url_safe_decode }}",
        expect=(
            r"abcdefghijklmnopqrstuvwxyz "
            r"ABCDEFGHIJKLMNOPQRSTUVWXYZ "
            r"1234567890 !@#$%^&*()-=_+/?.:;[]{}\|"
        ),
        globals={
            "a": (
                "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXogQUJDREVGR0hJSktMTU5PUFFSU1RVV"
                "ldYWVogMTIzNDU2Nzg5MCAhQCMkJV4mKigpLT1fKy8_Ljo7W117fVx8"
            )
        },
    ),
    Case(
        description="not a string",
        template=r"{{ 5 | base64_url_safe_decode }}",
        expect="",
        error=True,
    ),
    Case(
        description="unexpected argument",
        template=r'{{ "hello" | base64_url_safe_decode: 5 }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | base64_url_safe_decode }}",
        expect="",
    ),
]
