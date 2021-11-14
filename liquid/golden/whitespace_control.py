"""Golden tests cases for testing liquid whitespace control."""

from liquid.golden.case import Case

cases = [
    Case(
        description="white space control with newlines and spaces",
        template="".join(
            [
                "\n{% if customer -%}\n",
                "Welcome back,  {{ customer.first_name -}} !\n",
                " {%- endif -%}",
            ]
        ),
        expect="\nWelcome back,  Holly!",
        globals={"customer": {"first_name": "Holly"}},
    ),
    Case(
        description="white space control with carriage return and spaces",
        template="".join(
            [
                "\r{% if customer -%}\r",
                "Welcome back,  {{ customer.first_name -}} !\r",
                " {%- endif -%}",
            ]
        ),
        expect="\rWelcome back,  Holly!",
        globals={"customer": {"first_name": "Holly"}},
    ),
    Case(
        description=("white space control with  carriage return, newline and spaces"),
        template="".join(
            [
                "\r\n{% if customer -%}\r\n",
                "Welcome back,  {{ customer.first_name -}} !\r\n",
                " {%- endif -%}",
            ]
        ),
        expect="\r\nWelcome back,  Holly!",
        globals={"customer": {"first_name": "Holly"}},
    ),
    Case(
        description="white space control with newlines, tabs and spaces",
        template="".join(
            [
                "\n\t{% if customer -%}\t\n",
                "Welcome back,  {{ customer.first_name -}}\t !\r\n",
                " {%- endif -%}",
            ]
        ),
        expect="\n\tWelcome back,  Holly!",
        globals={"customer": {"first_name": "Holly"}},
    ),
]
