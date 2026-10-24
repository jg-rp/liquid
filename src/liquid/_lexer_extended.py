from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ._lexer import Lexer, State
from .tokens import *

if TYPE_CHECKING:
    from .environment import Environment
    from .tokens import TokenKind

RE_FLOAT = re.compile(r"-?\d+\.\d+")
RE_IDENT = re.compile(r"[a-zA-Z_][a-zA-Z0-9_-]*\??")
RE_INT = re.compile(r"-?\d+")
RE_TRIVIA = re.compile(r"[ \n\r\t\f]+")
RE_TAG_NAME = re.compile(r"#|[a-zA-Z0-9_]+")
RE_LINE_TRIVIA = re.compile(r"[ \r\t\f]+")
RE_LINE_COMMENT_SEGMENT = re.compile(r"\n\s*(comment|endcomment).*")


class ExtendedLexer(Lexer):
    """A tokenizer that accepts alternative markup delimiters."""

    comment_start: str = "{#"
    comment_end: str = "#}"

    out_start: str = "{{"
    out_end: str = "}}"

    tag_start: str = "{%"
    tag_end: str = "%}"

    __slots__ = (
        "re_comment_segment",
        "re_doc_segment",
        "re_end_raw",
        "re_markup_start",
    )

    def __init__(self, env: Environment, source: str) -> None:
        super().__init__(env, source)

        self.re_markup_start = re.compile(
            rf"{re.escape(self.out_start)}|"
            rf"{re.escape(self.tag_start)}|"
            rf"{re.escape(self.comment_start)}"
        )

        self.re_comment_segment = re.compile(
            rf"{re.escape(self.tag_start)}"
            r"-?\s*"
            r"(comment|raw|endcomment|endraw)"
            rf"(?:(?!-?{re.escape(self.tag_end)})[\s\S])*"
            rf"-?{re.escape(self.tag_end)}"
        )

        self.re_doc_segment = re.compile(
            rf"{re.escape(self.tag_start)}"
            r"-?\s*"
            r"(doc|enddoc)"
            rf"(?:(?!-?{re.escape(self.tag_end)})[\s\S])*"
            rf"-?{re.escape(self.tag_end)}"
        )

        self.re_end_raw = re.compile(
            rf"{re.escape(self.tag_start)}-?\s*endraw\s*-?{re.escape(self.tag_end)}"
        )

    def scan_markup(self) -> State | None:

        while 1:
            if self.source.startswith(self.out_start, self.pos):
                self.pos += len(self.out_start)
                self.emit(TOKEN_OUT_START)
                self.accept_whitespace_control()
                self.accept_expression()
                self.skip(RE_TRIVIA)
                self.accept_whitespace_control()

                if self.source.startswith(self.out_end, self.pos):
                    self.pos += len(self.out_end)
                    self.emit(TOKEN_OUT_END)

            elif self.source.startswith(self.tag_start, self.pos):
                self.pos += len(self.tag_start)
                self.emit(TOKEN_TAG_START)
                self.accept_whitespace_control()
                self.skip(RE_TRIVIA)
                self.accept_tag()

            elif self.comment_start and self.source.startswith(
                self.comment_start, self.pos
            ):
                self.accept_template_comment()

            # TODO: try min(source.find)
            elif self.scan_until(self.re_markup_start):
                self.emit(TOKEN_TEXT)

            else:
                # No more markup. Emit text to end of string.
                self.pos = self.length
                if self.start < self.pos:
                    self.emit(TOKEN_TEXT)
                return None

    def accept_tag(self) -> None:
        tag_name = self.scan(RE_TAG_NAME)

        if tag_name is not None:
            self.emit(TOKEN_TAG_NAME)

        if tag_name == "#":
            limit = self.tag_limit()
            if limit == -1:
                return
            self.accept_inline_comment(limit)

        elif tag_name == "comment":
            limit = self.tag_limit()
            if limit == -1:
                return
            self.accept_block_comment(limit)

        elif tag_name == "doc":
            limit = self.tag_limit()
            if limit == -1:
                return
            self.accept_doc_comment(limit)

        elif tag_name == "raw":
            limit = self.tag_limit()
            if limit == -1:
                return
            self.accept_raw_tag(limit)

        elif tag_name == "liquid":
            self.accept_line_statements(self.length)

        else:
            self.accept_expression()
            self.skip(RE_TRIVIA)
            self.accept_whitespace_control()

            if self.source.startswith(self.tag_end, self.pos):
                self.pos += len(self.tag_end)
                self.emit(TOKEN_TAG_END)

    def accept_inline_comment(self, limit: int) -> None:
        self.pos = limit
        self.emit(TOKEN_COMMENT)
        self.accept_whitespace_control()

        if self.source.startswith(self.tag_end, self.pos):
            self.pos += len(self.tag_end)
            self.emit(TOKEN_TAG_END)

    def accept_block_comment(self, limit: int) -> None:
        self.skip(RE_TRIVIA)

        # Ignore everything up to the next delimiter.
        self.pos = limit
        self.accept_whitespace_control()
        if self.source.startswith(self.tag_end, self.pos):
            self.pos += len(self.tag_end)
            self.emit(TOKEN_TAG_END)

        comment_depth = 1
        raw_depth = 0

        # Find the matching `{% endcomment %}` while allowing fully-formed,
        # nested comments and raw blocks.
        while 1:
            match = self.skip_until(self.re_comment_segment)

            if not match:
                self.emit(TOKEN_UNKNOWN)
                break

            tag_name = match.group(1)

            if tag_name == "comment":
                comment_depth += 1
                self.pos = match.end()

            elif tag_name == "raw":
                raw_depth += 1
                self.pos = match.end()

            elif tag_name == "endraw":
                if raw_depth > 0:
                    raw_depth -= 1
                self.pos = match.end()

            elif tag_name == "endcomment":
                if raw_depth > 0:
                    self.pos = match.end()
                    continue

                comment_depth -= 1

                if comment_depth > 0:
                    self.pos = match.end()
                    continue

                self.emit(TOKEN_COMMENT)

                # Leave the `{% endcomment %}` for scan_markup.
                break

    def accept_doc_comment(self, limit: int) -> None:
        self.skip(RE_TRIVIA)
        self.accept_expression(limit)
        self.pos = limit
        if self.start < self.pos:
            self.emit(TOKEN_UNKNOWN)
            self.skip(RE_TRIVIA)
        self.accept_whitespace_control()

        if self.source.startswith(self.tag_end, self.pos):
            self.pos += len(self.tag_end)
            self.emit(TOKEN_TAG_END)

        doc_depth = 1

        # Find the matching `{% enddoc %}` while allowing fully-formed,
        # nested doc blocks.
        while 1:
            match = self.skip_until(self.re_doc_segment)

            if not match:
                self.emit(TOKEN_UNKNOWN)
                break

            tag_name = match.group(1)

            if tag_name == "doc":
                doc_depth += 1
                self.pos = match.end()

            elif tag_name == "enddoc":
                doc_depth -= 1

                if doc_depth > 0:
                    self.pos = match.end()
                    continue

                self.emit(TOKEN_COMMENT)
                # Leave the `{% enddoc %}` for scan_markup.
                break

    def accept_raw_tag(self, limit: int) -> None:
        self.skip(RE_TRIVIA)
        self.pos = limit
        if self.start < self.pos:
            self.emit(TOKEN_UNKNOWN)
            self.skip(RE_TRIVIA)
        self.accept_whitespace_control()

        if self.source.startswith(self.tag_end, self.pos):
            self.pos += len(self.tag_end)
            self.emit(TOKEN_TAG_END)

        if self.scan_until(self.re_end_raw):
            self.emit(TOKEN_TEXT)

        # Leave `{% endraw%}` for scan_markup.

    def accept_template_comment(self) -> None:
        limit = self.source.find(self.comment_end, self.pos + len(self.comment_start))

        if limit > 0 and self.source[limit - 1] == "-":
            # Subtract one for whitespace control.
            limit -= 1

        if limit == -1:
            # No matching end comment delimiter. Treat the start comment delimiter as text.
            self.pos += len(self.comment_start)
            self.emit(TOKEN_TEXT)
            return

        self.pos += len(self.comment_start)
        self.emit(TOKEN_COMMENT_START)
        self.accept_whitespace_control()

        self.pos = limit
        if self.start < self.pos:
            self.emit(TOKEN_COMMENT)

        self.accept_whitespace_control()
        self.pos += len(self.comment_end)
        if self.start < self.pos:
            self.emit(TOKEN_COMMENT_END)

    def accept_expression(
        self, limit: int | None = None, trivia: re.Pattern[str] = RE_TRIVIA
    ) -> None:
        limit = limit or self.length

        while self.pos < limit:
            if self.source.startswith((self.tag_end, self.out_end), self.pos) or (
                self.source.startswith("-", self.pos)
                and self.source.startswith((self.tag_end, self.out_end), self.pos + 1)
            ):
                break

            ch = self.source[self.pos]

            if _is_trivia(ord(ch)):  # XXX: is_lint_trivia?
                self.skip(trivia)

            elif ch == ",":
                self.pos += 1
                self.emit(TOKEN_COMMA)

            elif ch == "|":
                self.pos += 1
                self.emit(TOKEN_PIPE)

            elif ch == ":":
                self.pos += 1
                self.emit(TOKEN_COLON)

            elif ch == "[":
                self.pos += 1
                self.emit(TOKEN_LBRACKET)

            elif ch == "]":
                self.pos += 1
                self.emit(TOKEN_RBRACKET)

            elif ch == "(":
                self.pos += 1
                self.emit(TOKEN_LPAREN)

            elif ch == ")":
                self.pos += 1
                self.emit(TOKEN_RPAREN)

            elif ch == "#":
                self.pos += 1
                self.emit(TOKEN_HASH)

            elif ch == ".":
                if self.pos + 1 < limit and self.source[self.pos + 1] == ".":
                    self.pos += 2
                    self.emit(TOKEN_DOUBLE_DOT)
                else:
                    self.pos += 1
                    self.emit(TOKEN_DOT)

            elif ch == "=":
                if self.pos + 1 < limit and self.source[self.pos + 1] == "=":
                    self.pos += 2
                    self.emit(TOKEN_EQ)
                else:
                    self.pos += 1
                    self.emit(TOKEN_ASSIGN)

            elif ch == "<":
                if self.pos + 1 < limit and self.source[self.pos + 1] == "=":
                    self.pos += 2
                    self.emit(TOKEN_LE)
                elif self.pos + 1 < limit and self.source[self.pos + 1] == ">":
                    self.pos += 2
                    self.emit(TOKEN_NE)
                else:
                    self.pos += 1
                    self.emit(TOKEN_LT)

            elif ch == ">":
                if self.pos + 1 < limit and self.source[self.pos + 1] == "=":
                    self.pos += 2
                    self.emit(TOKEN_GE)
                else:
                    self.pos += 1
                    self.emit(TOKEN_GT)

            elif ch == "!":
                if self.pos + 1 < limit and self.source[self.pos + 1] == "=":
                    self.pos += 2
                    self.emit(TOKEN_NE)
                else:
                    self.pos += 1
                    self.emit(TOKEN_UNKNOWN)

            elif ch == "'":
                self.scan_string_literal(
                    "'", TOKEN_SINGLE_QUOTE, TOKEN_SINGLE_QUOTED, limit
                )

            elif ch == '"':
                self.scan_string_literal(
                    '"', TOKEN_DOUBLE_QUOTE, TOKEN_DOUBLE_QUOTED, limit
                )

            elif _is_name_first_ch(ord(ch)):
                match = self.scan(RE_IDENT)

                if match == "true":
                    self.emit(TOKEN_TRUE)
                elif match == "false":
                    self.emit(TOKEN_FALSE)
                elif match in ("nil", "null"):
                    self.emit(TOKEN_NIL)
                elif match == "and":
                    self.emit(TOKEN_AND)
                elif match == "or":
                    self.emit(TOKEN_OR)
                elif match == "contains":
                    self.emit(TOKEN_CONTAINS)
                elif match == "in":
                    self.emit(TOKEN_IN)
                elif match == "blank":
                    self.emit(TOKEN_BLANK)
                elif match == "empty":
                    self.emit(TOKEN_EMPTY)
                elif match == "if":
                    self.emit(TOKEN_IF)
                elif match == "else":
                    self.emit(TOKEN_ELSE)
                elif match == "not":
                    self.emit(TOKEN_NOT)
                else:
                    self.emit(TOKEN_IDENT)

            elif _is_number_ch(ord(ch)):
                if match := self.scan(RE_FLOAT):
                    self.emit(TOKEN_FLOAT)

                elif match := self.scan(RE_INT):
                    self.emit(TOKEN_INT)

                elif ch == "-":
                    self.pos += 1
                    self.emit(TOKEN_SUB)

                else:
                    self.pos += 1
                    self.emit(TOKEN_UNKNOWN)

            elif ch == "+":
                self.pos += 1
                self.emit(TOKEN_ADD)

            elif ch == "*":
                self.pos += 1
                self.emit(TOKEN_MUL)

            elif ch == "/":
                self.pos += 1
                self.emit(TOKEN_DIV)

            elif ch == "%":
                self.pos += 1
                self.emit(TOKEN_MOD)

            else:
                self.pos += 1
                self.emit(TOKEN_UNKNOWN)

    def accept_line_statements(self, limit: int) -> None:
        while self.pos < limit:
            self.skip(RE_TRIVIA)

            if self.source.startswith(self.tag_end, self.pos) or (
                self.source.startswith("-", self.pos)
                and self.source.startswith(self.tag_end, self.pos + 1)
            ):
                break

            line_limit = self.source.find(("\n"), self.pos)
            if line_limit == -1:
                line_limit = limit

            line_limit = min(line_limit, limit)

            self.emit(TOKEN_TAG_START)

            tag_name = self.scan(RE_TAG_NAME)

            if tag_name == "#":
                self.emit(TOKEN_TAG_NAME)
                self.pos = line_limit
                self.emit(TOKEN_COMMENT)
                self.emit(TOKEN_TAG_END)

            elif tag_name == "comment":
                self.emit(TOKEN_TAG_NAME)
                self.emit(TOKEN_TAG_END)
                self.accept_line_block_comment(limit)

            elif tag_name == "doc":
                self.emit(TOKEN_TAG_NAME)
                self.accept_line_doc_comment(limit)

            elif tag_name == "raw":
                self.emit(TOKEN_TAG_NAME)
                self.accept_line_raw_tag(limit)

            elif tag_name == "liquid":
                self.emit(TOKEN_TAG_NAME)
                self.accept_line_statements(line_limit)

            elif tag_name is None:
                # Remove empty TAG_START
                self.tokens.pop()

            else:
                self.emit(TOKEN_TAG_NAME)
                self.accept_expression(line_limit, RE_LINE_TRIVIA)
                self.emit(TOKEN_TAG_END)

        self.skip(RE_TRIVIA)
        self.accept_whitespace_control()

        if self.source.startswith(self.tag_end, self.pos):
            self.pos += len(self.tag_end)

        self.emit(TOKEN_TAG_END)

    def accept_line_block_comment(self, limit: int) -> None:
        comment_depth = 1

        while self.pos < limit:
            index = self.index(RE_LINE_COMMENT_SEGMENT)
            if not index or index > limit:
                self.pos = limit
                self.emit(TOKEN_UNKNOWN)
                break

            match = self.skip_until(RE_LINE_COMMENT_SEGMENT)

            if not match:
                self.emit(TOKEN_UNKNOWN)
                break

            tag_name = match.group(1)

            if tag_name == "comment":
                comment_depth += 1
                self.pos = match.end()

            elif tag_name == "endcomment":
                comment_depth -= 1

                if comment_depth > 0:
                    self.pos = match.end()
                    continue

                self.emit(TOKEN_COMMENT)
                return

            else:
                assert False  # unreachable

    def accept_line_doc_comment(self, limit: int) -> None:
        # Shopify/liquid always raises a syntax error for `doc` in `{% liquid %}`.
        self.pos = limit
        self.emit(TOKEN_UNKNOWN)

    def accept_line_raw_tag(self, limit: int) -> None:
        # Shopify/liquid always raises a syntax error for `raw` in `{% liquid %}`.
        self.pos = limit
        self.emit(TOKEN_UNKNOWN)

    def scan_string_literal(
        self,
        quote: str,
        delim_kind: TokenKind,
        kind: TokenKind,
        limit: int,
    ) -> None:
        self.pos += 1
        self.emit(delim_kind)

        if self.source.startswith(quote, self.pos):
            # Empty string
            self.pos += 1
            self.emit(delim_kind)
            return

        index = self.source.find(quote, self.pos)
        if index == -1:
            index = limit

        self.pos = min(index, limit)
        self.emit(kind)

        if self.source.startswith(quote, self.pos):
            self.pos += 1
            self.emit(delim_kind)

    def tag_limit(self) -> int:
        """Find the next tag end delimiter, disregarding string literals.

        This is only suitable for tags that don't accept expressions that could
        possibly contain string literals. Built-in tags include ``{% comment %}``,
        ``{% # ... %}``, ``{% raw %}`` and ``{% doc%}``.
        """
        limit = self.source.find(self.tag_end, self.pos)
        if limit > 0 and self.source[limit - 1] == "-":
            # Subtract one for whitespace control.
            limit -= 1
        return limit


def _is_name_first_ch(ch: int) -> bool:
    return (ch >= 65 and ch <= 90) or (ch >= 97 and ch <= 122) or ch == 95


def _is_number_ch(ch: int) -> bool:
    return ch == 45 or (ch >= 48 and ch <= 57)


def _is_trivia(ch: int) -> bool:
    return ch == 32 or ch == 9 or ch == 10 or ch == 12 or ch == 13
