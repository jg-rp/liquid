import re
import timeit

from typing import Iterator, Tuple, Iterable

from liquid import Token
from liquid.token import (
    TOKEN_STATEMENT,
    TOKEN_LITERAL,
    TOKEN_TAG_NAME,
    TOKEN_EXPRESSION,
)

from liquid.exceptions import LiquidSyntaxError

LIQUID_SPEC = [
    ("RAW", r"{%\s*raw\s*%}(?P<raw>.*?){%\s*endraw\s*%}"),
    (TOKEN_STATEMENT, r"{{-?\s*(?P<stmt>.*?)\s*(?P<rss>-?)}}"),
    ("TAG", r"{%-?\s*(?P<name>\w*)\s*(?P<expr>.*?)\s*(?P<rst>-?)%}"),
    (TOKEN_LITERAL, r".+?(?=({[{%](?P<rstrip>-?))|$)"),
]


def compile(spec: Iterable[Tuple[str, str]]):
    """"""
    pattern = "|".join(f"(?P<{name}>{pattern})" for name, pattern in spec)
    return re.compile(pattern, re.DOTALL)


RE_LIQUID_SPEC = compile(LIQUID_SPEC)


def tokenize_liquid(source: str) -> Iterator:
    line_count = 1
    lstrip = False

    for match in RE_LIQUID_SPEC.finditer(source):
        kind = match.lastgroup
        assert kind is not None

        line_num = line_count
        value = match.group()
        line_count += value.count("\n")

        if kind == TOKEN_STATEMENT:
            value = match.group("stmt")
            lstrip = bool(match.group("rss"))

        elif kind == "TAG":
            name = match.group("name")

            if not name:
                raise LiquidSyntaxError("missing tag name", linenum=line_num)

            yield Token(line_num, TOKEN_TAG_NAME, name)

            kind = TOKEN_EXPRESSION
            value = match.group("expr")
            lstrip = bool(match.group("rst"))

            if not value:
                continue

        elif kind == "RAW":
            kind = TOKEN_LITERAL
            value = match.group("raw")

        elif kind == TOKEN_LITERAL:
            if lstrip:
                value = value.lstrip()
            if match.group("rstrip"):
                value = value.rstrip()
            if not value:
                continue

        yield Token(line_num, kind, value)


def main():
    # source = "<HTML>{%if  product %}some  {%- else  %}  other{% endif -%}</HTML>"
    # source = "<HTML>{{ foo }}{% if product %}some  {% else  %}other{% endif -%}</HTML>"
    # source = "Some\n\n{{- obj -}}\n{% assign x = 1 %}"
    source = "text {{"

    for tok in tokenize_liquid(source):
        print(tok)


if __name__ == "__main__":
    main()
