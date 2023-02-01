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
    Case(
        description="suppress whitespace only if blocks",
        template="\n".join(
            [
                "!{% if true %}",
                "",
                "{% assign bar = 'foo' %}",
                "{% if true %}",
                "",
                "",
                "    {% assign foo = 'bar' %}",
                "",
                "{% endif %}",
                "",
                "",
                "{% endif %}!",
            ]
        ),
        expect="!!",
        globals={},
    ),
    Case(
        description="suppress whitespace only unless blocks",
        template="\n".join(
            [
                "!{% unless false %}",
                "",
                "{% assign bar = 'foo' %}",
                "{% unless false %}",
                "",
                "",
                "    {% assign foo = 'bar' %}",
                "",
                "{% endunless %}",
                "",
                "",
                "{% endunless %}!",
            ]
        ),
        expect="!!",
        globals={},
    ),
    Case(
        description="suppress whitespace only case blocks",
        template="\n".join(
            [
                "!{% assign x = 1 %}{% case x %}",
                "",
                "  {% when 1 %}",
                "    {% assign foo = 'bar' %}",
                "",
                "",
                "{% endcase %}!",
            ]
        ),
        expect="!!",
        globals={},
    ),
    Case(
        description="don't suppress whitespace only blocks containing output",
        template="\n".join(
            [
                "!{% if true %}",
                "",
                "{% assign bar = 'foo' %}",
                "    {{ '' }}",
                "",
                "    {% assign foo = 'bar' %}",
                "",
                "",
                "",
                "{% endif %}!",
            ]
        ),
        expect="!\n\n\n    \n\n    \n\n\n\n!",
        globals={},
    ),
    Case(
        description="don't suppress whitespace only blocks containing echo",
        template="\n".join(
            [
                "!{% if true %}",
                "",
                "{% assign bar = 'foo' %}",
                "    {% echo '' %}",
                "",
                "    {% assign foo = 'bar' %}",
                "",
                "",
                "",
                "{% endif %}!",
            ]
        ),
        expect="!\n\n\n    \n\n    \n\n\n\n!",
        globals={},
    ),
    Case(
        description=(
            "don't suppress whitespace only blocks containing output in nested block"
        ),
        template="\n".join(
            [
                "!{% if 1 %}",
                "",
                "{% assign bar = 'foo' %}",
                "{% if 2 %}",
                "    {{ '' }}",
                "",
                "    {% assign foo = 'bar' %}",
                "",
                "{% endif %}",
                "",
                "",
                "{% endif %}!",
            ]
        ),
        expect="!\n\n\n\n    \n\n    \n\n\n\n\n!",
        globals={},
    ),
    Case(
        description=(
            "don't suppress whitespace only unless blocks containing output in nested "
            "blocks"
        ),
        template="\n".join(
            [
                "!{% unless false %}",
                "",
                "{% assign bar = 'foo' %}",
                "{% unless false %}",
                "    {{ '' }}",
                "",
                "    {% assign foo = 'bar' %}",
                "",
                "{% endunless %}",
                "",
                "",
                "{% endunless %}!",
            ]
        ),
        expect="!\n\n\n\n    \n\n    \n\n\n\n\n!",
        globals={},
    ),
    Case(
        description=(
            "don't suppress whitespace only blocks containing output in "
            "unreachable blocks"
        ),
        template="\n".join(
            [
                "!{% if 1 %}",
                "",
                "{% assign bar = 'foo' %}",
                "{% if true %}",
                "",
                "    {% assign foo = 'bar' %}",
                "",
                "{% else %}",
                "    {{ '' }}",
                "{% endif %}",
                "",
                "",
                "{% endif %}!",
            ]
        ),
        expect="!\n\n\n\n\n    \n\n\n\n\n!",
        globals={},
    ),
    Case(
        description="suppress whitespace surrounding an empty capture block",
        template="\n".join(
            [
                "!{% if true %}",
                "",
                "{% capture foo %}{% endcapture %}",
                "",
                "{% endif %}!",
            ]
        ),
        expect="!!",
        globals={},
    ),
    Case(
        description="suppress whitespace surrounding a capture block",
        template="\n".join(
            [
                "!{% if true %}",
                "",
                "{% capture foo %}",
                "{{ '' }}",
                "{% endcapture %}",
                "",
                "{% endif %}!",
            ]
        ),
        expect="!!",
        globals={},
    ),
    Case(
        description="don't suppress whitespace only case blocks containing output",
        template="\n".join(
            [
                "!{% assign x = 1 %}{% case x %}",
                "",
                "  {% when 1 %}",
                "    {% assign foo = 'bar' %}",
                "",
                "  {% when 2 %}",
                "    {{ '' }}",
                "",
                "{% endcase %}!",
            ]
        ),
        expect="!\n    \n\n  !",
        globals={},
    ),
    Case(
        description="white space control with raw tags",
        template="".join(
            [
                "! {% raw %}{{ hello }}{% endraw %} !\n",
                "! {%- raw -%}{{ hello }}{%- endraw -%} !",
            ]
        ),
        expect="! {{ hello }} !\n!{{ hello }}!",
        globals={},
    ),
]
