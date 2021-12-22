"""Golden tests cases for testing liquid's `liquid` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="newline terminated tags",
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
    Case(
        description="carriage return and newline terminated tags",
        template="\r\n".join(
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
    Case(
        description="carriage return terminated tags",
        template="\r".join(
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
        expect="",
        globals={"product": {"title": "foo"}},
        error=True,
    ),
    Case(
        description="empty liquid tag",
        template=r"{% liquid %}",
        expect="",
    ),
    Case(
        description="only whitespace",
        template="{% liquid\n   \n\n   \t \n\t\n  %}",
        expect="",
    ),
    Case(
        description="single line comment tag",
        template="\n".join(
            [
                r"{% liquid",
                r"comment this is a comment",
                r"endcomment",
                r"%}",
            ]
        ),
        expect="",
    ),
    Case(
        description="multi-line comment tag",
        template="\n".join(
            [
                r"{% liquid",
                r"comment this is a comment",
                r"split over two lines",
                r"endcomment",
                r"%}",
            ]
        ),
        expect="",
    ),
    Case(
        description="whitespace control",
        template="\n".join(
            [
                r"Hello,     ",
                r"{%- liquid",
                r"  echo ' World! '",
                r"-%}",
                r"   Goodbye.",
            ]
        ),
        expect="Hello, World! Goodbye.",
    ),
    Case(
        description="reference test #2",
        template="\n".join(
            [
                r"{%- liquid",
                r"  for value in array",
                r"    echo value",
                r"    unless forloop.last",
                r"      echo '#'",
                r"    endunless",
                r"  endfor",
                r"-%}",
            ]
        ),
        expect="1#2#3",
        globals={"array": [1, 2, 3]},
    ),
    Case(
        description="reference test #3",
        template="\n".join(
            [
                r"{%- liquid",
                r"  for value in array",
                r"    assign double_value = value | times: 2",
                r"    echo double_value | times: 2",
                r"    unless forloop.last",
                r"      echo '#'",
                r"    endunless",
                r"  endfor",
                r"",
                r"  echo '#'",
                r"  echo double_value",
                r"-%}",
            ]
        ),
        expect="4#8#12#6",
        globals={"array": [1, 2, 3]},
    ),
    Case(
        description="reference test #4",
        template="\n".join(
            [
                r"{%- liquid echo 'a' -%}",
                r"b",
                r"{%- liquid echo 'c' -%}",
            ]
        ),
        expect="abc",
    ),
    Case(
        description="nested liquid",
        template="\n".join(
            [
                r"{%- if true %}",
                r"  {%- liquid",
                r'    echo "good"',
                r"  %}",
                r"{%- endif -%}",
            ]
        ),
        expect="good",
    ),
    Case(
        description="can't close nested blocks",
        template="\n".join(
            [
                r"{%- if true -%}",
                r"42",
                r"{%- liquid endif -%}",
            ]
        ),
        expect="",
        error=True,
    ),
]
