"""Tokenize Liquid templates and expressions.

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
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_ILLEGAL
from liquid.token import TOKEN_LITERAL
from liquid.token import TOKEN_OUTOUT
from liquid.token import TOKEN_TAG
from liquid.token import Token

__all__ = (
    "get_lexer",
    "get_liquid_expression_lexer",
)


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
    statement_pattern = rf"{stmt_s}-?\s*(?P<stmt>.*?)\s*(?P<rss>-?){stmt_e}"

    # The "name" group is zero or more characters so that a malformed tag (one
    # with no name) does not get treated as a literal.
    #
    # The `#` in the `name` group is specifically for the inline comment tag.
    tag_pattern = (
        rf"{tag_s}-?(?P<pre>\s*(?P<name>#|\w*)\s*)(?P<expr>.*?)\s*(?P<rst>-?){tag_e}"
    )

    if not comment_start_string:
        # Do not support shorthand comment syntax
        literal_pattern = rf".+?(?=(({tag_s}|{stmt_s})(?P<rstrip>-?))|$)"

        liquid_rules = [
            ("RAW", raw_pattern),
            (TOKEN_OUTOUT, statement_pattern),
            ("TAG", tag_pattern),
            (TOKEN_LITERAL, literal_pattern),
        ]
    else:
        literal_pattern = rf".+?(?=(({tag_s}|{stmt_s}|{comment_s})(?P<rstrip>-?))|$)"
        comment_pattern = rf"{comment_s}(?P<comment>.*?)(?P<rsc>-?){comment_e}"

        liquid_rules = [
            ("RAW", raw_pattern),
            ("COMMENT", comment_pattern),
            (TOKEN_OUTOUT, statement_pattern),
            ("TAG", tag_pattern),
            (TOKEN_LITERAL, literal_pattern),
        ]

    return _compile_rules(liquid_rules)


def _compile_rules(rules: Iterable[tuple[str, str]]) -> Pattern[str]:
    """Compile the given rules into a single regular expression."""
    pattern = "|".join(f"(?P<{name}>{pattern})" for name, pattern in rules)
    return re.compile(pattern, re.DOTALL)


# NOTE: Here we're talking about expressions found in "liquid" tags only. Each line
# starts with a tag name, optionally followed by zero or more space or tab characters
# and an expression, which is terminated by a newline.


def _tokenize_liquid_expression(
    source: str,
    rules: Pattern[str],
    token: Token,
    comment_start_string: str = "",
) -> Iterator[Token]:
    """Tokenize a "{% liquid %}" tag."""
    for match in rules.finditer(source):
        kind = match.lastgroup
        assert kind is not None

        value = match.group()

        if kind == "LIQUID_EXPR":
            name = match.group("name")
            if name == comment_start_string:
                continue

            yield Token(
                TOKEN_TAG,
                value=name,
                start_index=token.start_index + match.start(),
                source=token.source,
            )

            if match.group("expr"):
                yield Token(
                    TOKEN_EXPRESSION,
                    value=match.group("expr"),
                    start_index=token.start_index + match.start(),
                    source=token.source,
                )
        elif kind == "SKIP":
            continue
        else:
            raise LiquidSyntaxError(
                f"expected newline delimited tag expressions, found {value!r}",
                token=token,
            )


@lru_cache(maxsize=128)
def get_liquid_expression_lexer(
    comment_start_string: str = "",
) -> Callable[..., Iterator[Token]]:
    """Return a tokenizer that yields tokens from a `liquid` tag's expression."""
    # Dubious assumption here.
    comment_start_string = comment_start_string.replace("{", "")
    if comment_start_string:
        comment = re.escape(comment_start_string)
        rules = (
            (
                "LIQUID_EXPR",
                rf"[ \t]*(?P<name>(\w+|{comment}))[ \t]*(?P<expr>.*?)[ \t\r]*?(\n+|$)",
            ),
            ("SKIP", r"[\r\n]+"),
            (TOKEN_ILLEGAL, r"."),
        )
    else:
        rules = (
            (
                "LIQUID_EXPR",
                r"[ \t]*(?P<name>#|\w+)[ \t]*(?P<expr>.*?)[ \t\r]*?(\n+|$)",
            ),
            ("SKIP", r"[\r\n]+"),
            (TOKEN_ILLEGAL, r"."),
        )
    return partial(
        _tokenize_liquid_expression,
        rules=_compile_rules(rules),
        comment_start_string=comment_start_string,
    )


# TODO: move me
tokenize_liquid_expression = get_liquid_expression_lexer(comment_start_string="")


def _tokenize_template(source: str, rules: Pattern[str]) -> Iterator[Token]:
    lstrip = False

    for match in rules.finditer(source):
        kind = match.lastgroup
        assert kind is not None

        value = match.group()

        if kind == TOKEN_OUTOUT:
            value = match.group("stmt")
            lstrip = bool(match.group("rss"))

        elif kind == "TAG":
            name = match.group("name")
            yield Token(
                kind=TOKEN_TAG,
                value=name,
                start_index=match.start(),
                source=source,
            )

            kind = TOKEN_EXPRESSION
            value = match.group("expr")
            lstrip = bool(match.group("rst"))

            if not value:
                continue

        elif kind == "COMMENT":
            lstrip = bool(match.group("rsc"))
            continue

        elif kind == "RAW":
            kind = TOKEN_LITERAL
            value = match.group("raw")
            lstrip = bool(match.group("rsr_e"))

        elif kind == TOKEN_LITERAL:
            if lstrip:
                value = value.lstrip()
            if match.group("rstrip"):
                value = value.rstrip()

            if not value:
                continue

            if value.startswith(r"{{"):
                raise LiquidSyntaxError(
                    "expected '}}', found 'eof'",
                    token=Token(
                        TOKEN_EOF,
                        value=match.group(),
                        start_index=match.start(),
                        source=source,
                    ),
                )
            if value.startswith(r"{%"):
                raise LiquidSyntaxError(
                    "expected '%}', found 'eof'",
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
