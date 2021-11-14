"""Golden tests cases for testing liquid's `liquid` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="multiple tags",
        template="\n".join(
            [
                r"{% liquid",
                r"if product.title",
                r"   echo product.title | upcase",
                r"else",
                r"   echo 'product-1' | upcase ",
                r"endif",
                r"",
                r"for i in (0..5)",
                r"   echo i",
                r"endfor %}",
            ]
        ),
        expect="FOO012345",
        globals={"product": {"title": "foo"}},
    ),
]
