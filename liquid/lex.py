"""Tokenize Liquid templates.

The template lexer generates a stream of template literals, tags, output statements and
expressions, where each expression token is an unscanned string. Lexing of expression
tokens is delegated to the "parse" method of each registered Tag.
"""

from __future__ import annotations

import re
from functools import lru_cache
from functools import partial
from typing import Callable
from typing import Iterable
from typing import Iterator
from typing import Pattern

from liquid.exceptions import LiquidSyntaxError
from liquid.token import TOKEN_COMMENT
from liquid.token import TOKEN_CONTENT
from liquid.token import TOKEN_DOC
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_OUTPUT
from liquid.token import TOKEN_TAG
from liquid.token import Token


def compile_liquid_rules(
    tag_start_string: str = r"{%",
    tag_end_string: str = r"%}",
    statement_start_string: str = r"{{",
    statement_end_string: str = r"}}",
    comment_start_string: str = r"",
    comment_end_string: str = r"",
) -> Pattern[str]:
    """Compile rules for lexing liquid templates."""
    tag_s = re.escape(tag_start_string)
    tag_e = re.escape(tag_end_string)
    stmt_s = re.escape(statement_start_string)
    stmt_e = re.escape(statement_end_string)
    comment_s = re.escape(comment_start_string)
    comment_e = re.escape(comment_end_string)

    raw_pattern = (
        rf"{tag_s}-?\s*raw\s*(?P<rsr>-?){tag_e}"
        r"(?P<raw>.*?)"
        rf"{tag_s}-?\s*endraw\s*(?P<rsr_e>-?){tag_e}"
    )

    doc_pattern = (
        rf"{tag_s}-?\s*doc\s*(?P<lsd>-?){tag_e}"
        r"(?P<doc>.*?)"
        rf"{tag_s}-?\s*enddoc\s*(?P<rsd>-?){tag_e}"
    )

    output_pattern = rf"{stmt_s}-?\s*(?P<stmt>.*?)\s*(?P<rss>-?){stmt_e}"

    # The "name" group is zero or more characters so that a malformed tag (one
    # with no name) does not get treated as a literal.
    #
    # The `#` in the `name` group is specifically for the inline comment tag.
    tag_pattern = (
        rf"{tag_s}-?(?P<pre>\s*(?P<name>#|\w*)\s*)(?P<expr>.*?)\s*(?P<rst>-?){tag_e}"
    )

    if not comment_start_string:
        # Do not support shorthand comment syntax
        content_pattern = rf".+?(?=(({tag_s}|{stmt_s})(?P<rstrip>-?))|$)"

        liquid_rules = [
            ("RAW", raw_pattern),
            ("DOC", doc_pattern),
            (TOKEN_OUTPUT, output_pattern),
            ("TAG", tag_pattern),
            (TOKEN_CONTENT, content_pattern),
        ]
    else:
        content_pattern = rf".+?(?=(({tag_s}|{stmt_s}|{comment_s})(?P<rstrip>-?))|$)"
        comment_pattern = rf"{comment_s}(?P<comment>.*?)(?P<rsc>-?){comment_e}"

        liquid_rules = [
            ("RAW", raw_pattern),
            ("DOC", doc_pattern),
            ("COMMENT", comment_pattern),
            (TOKEN_OUTPUT, output_pattern),
            ("TAG", tag_pattern),
            (TOKEN_CONTENT, content_pattern),
        ]

    return _compile_rules(liquid_rules)


def _compile_rules(rules: Iterable[tuple[str, str]]) -> Pattern[str]:
    """Compile the given rules into a single regular expression."""
    pattern = "|".join(f"(?P<{name}>{pattern})" for name, pattern in rules)
    return re.compile(pattern, re.DOTALL)


def _tokenize_template(source: str, rules: Pattern[str]) -> Iterator[Token]:  # noqa: PLR0912, PLR0915
    lstrip = False
    comment_index = 0
    comment_text: list[str] = []
    comment_depth = 0

    for match in rules.finditer(source):
        kind = match.lastgroup
        assert kind is not None

        value = match.group()

        if comment_depth:
            if kind == "TAG":
                name = match.group("name")
                if name == "endcomment":
                    comment_depth -= 1
                    if not comment_depth:
                        yield Token(
                            kind=TOKEN_COMMENT,
                            value="".join(comment_text),
                            start_index=comment_index,
                            source=source,
                        )

                        comment_index = 0
                        comment_text.clear()

                        yield Token(
                            kind=TOKEN_TAG,
                            value=name,
                            start_index=match.start("name"),
                            source=source,
                        )

                        lstrip = bool(match.group("rst"))
                        continue
                elif name == "comment":
                    comment_depth += 1

            comment_text.append(value)
            continue

        if kind == TOKEN_OUTPUT:
            yield Token(
                kind=TOKEN_OUTPUT,
                value=match.group(),
                start_index=match.start(),
                source=source,
            )

            yield Token(
                TOKEN_EXPRESSION,
                match.group("stmt"),
                start_index=match.start("stmt"),
                source=source,
            )

            lstrip = bool(match.group("rss"))
            continue
        elif kind == "TAG":
            name = match.group("name")
            yield Token(
                kind=TOKEN_TAG,
                value=name,
                start_index=match.start("name"),
                source=source,
            )

            value = match.group("expr")
            lstrip = bool(match.group("rst"))

            if value:
                yield Token(
                    kind=TOKEN_EXPRESSION,
                    value=value,
                    start_index=match.start("expr"),
                    source=source,
                )

            if name == "comment":
                if not comment_depth:
                    comment_index = match.end()
                comment_depth += 1

            continue

        elif kind == "COMMENT":
            lstrip = bool(match.group("rsc"))
            value = match.group("comment")

        elif kind == "RAW":
            kind = TOKEN_CONTENT
            value = match.group("raw")
            lstrip = bool(match.group("rsr"))

        elif kind == "DOC":
            kind = TOKEN_DOC
            value = match.group("doc")
            lstrip = bool(match.group("rsd"))

        elif kind == TOKEN_CONTENT:
            if lstrip:
                value = value.lstrip()
            if match.group("rstrip"):
                value = value.rstrip()

            if not value:
                continue

            if value.startswith(r"{{"):
                raise LiquidSyntaxError(
                    "expected '}}', found end of file",
                    token=Token(
                        TOKEN_EOF,
                        value=match.group(),
                        start_index=match.start(),
                        source=source,
                    ),
                )
            if value.startswith(r"{%"):
                raise LiquidSyntaxError(
                    "expected '%}', found end of file",
                    token=Token(
                        TOKEN_EOF,
                        value=match.group(),
                        start_index=match.start(),
                        source=source,
                    ),
                )

        yield Token(kind, value, start_index=match.start(), source=source)


@lru_cache(maxsize=128)
def get_lexer(
    tag_start_string: str = r"{%",
    tag_end_string: str = r"%}",
    statement_start_string: str = r"{{",
    statement_end_string: str = r"}}",
    comment_start_string: str = "",
    comment_end_string: str = "",
) -> Callable[[str], Iterator[Token]]:
    """Return a template lexer using the given tag and statement delimiters."""
    rules = compile_liquid_rules(
        tag_start_string,
        tag_end_string,
        statement_start_string,
        statement_end_string,
        comment_start_string,
        comment_end_string,
    )
    return partial(_tokenize_template, rules=rules)
