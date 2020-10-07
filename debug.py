import re
import timeit

from typing import Iterator, Tuple, Iterable

from liquid import Token
from liquid.token import (
    TOKEN_STATEMENT,
    TOKEN_LITERAL,
    TOKEN_TAG,
    TOKEN_EXPRESSION,
)

from liquid.lex import get_lexer

from liquid.exceptions import LiquidSyntaxError


LIQUID_EXPRESSION_RE = re.compile(r"[ \t]*(?P<name>\w+)[ \t]*(?P<expr>.*)[ \t]*?(\n|$)")


def tokenize_liquid_expression(source: str) -> Iterator:
    line_count = 1

    for match in LIQUID_EXPRESSION_RE.finditer(source):

        line_num = line_count
        value = match.group()
        line_count += value.count("\n")

        yield Token(line_num, TOKEN_TAG, match.group("name"))
        if match.group("expr"):
            yield Token(line_num, TOKEN_EXPRESSION, match.group("expr"))


def main():
    # source = "<HTML>{%if  product %}some  {%- else  %}  other{% endif -%}</HTML>"
    # source = "<HTML>{{ foo }}{% if product %}some  {% else  %}other{% endif -%}</HTML>"
    # source = "Some\n\n{{- obj -}}\n{% assign x = 1 %}"
    template = "\n".join(
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
    )

    source = "if product.title\n   echo product.title | upcase\nelse\n   echo 'product-1' | upcase \nendif\n\nfor i in (0..5)\n   echo i\nendfor"

    # for tok in tokenize_template(template):
    #     print(tok)

    for tok in tokenize_liquid_expression(source):
        print(tok)


if __name__ == "__main__":
    main()
