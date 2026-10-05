import re

from ._lexer import Lexer, State
from ._tokens import *
from ._tokens import TokenKind

RE_COMMENT_SEGMENT = re.compile(
    r"\{%-?\s*(comment|raw|endcomment|endraw)(?:(?!-?%\})[\s\S])*-?%\}"
)
RE_END_DOC = re.compile(r"\{%-?\s*enddoc\s*-?%\}")
RE_END_RAW = re.compile(r"\{%-?\s*endraw\s*-?%\}")
RE_FLOAT = re.compile(r"-?\d+\.\d+")
RE_IDENT = re.compile(r"[a-zA-Z_][a-zA-Z0-9_-]*\??")
RE_INT = re.compile(r"-?\d+")
RE_MARKUP_START = re.compile(r"\{[%{]")
RE_OUT_END = re.compile(r"-?(\}\}?|%\}(?!\}))")
RE_TAG_END = re.compile(r"-?%\}")
RE_TAG_NAME = re.compile(r"#|[a-zA-Z0-9_]+")
RE_TRIVIA = re.compile(r"[ \n\r\t\f]+")
RE_LINE_TRIVIA = re.compile(r"[ \r\t\f]+")
RE_LINE_COMMENT_SEGMENT = re.compile(r"\n\s*(comment|endcomment).*")

# TODO: benchmark without emit


class LegacyLexer(Lexer):
    """A Shopify/liquid v5.12.0 compatible tokenizer with hard coded delimiters."""

    def scan_markup(self) -> State | None:
        # TODO: Benchmark with a local pos and source

        while 1:
            if self.source.startswith("{{", self.pos):
                self.pos += 2

                # Output statements can be closed by `}}`, `}` or `%}`.
                # Markup delimiters are greedy and not string literal aware.
                limit = self.index(RE_OUT_END)

                if limit is None:
                    # No markup and no more '}'. Emit text to end of string.
                    self.pos = self.length
                    self.emit(TOKEN_TEXT)
                    return None

                self.emit(TOKEN_OUT_START)
                self.accept_whitespace_control()
                self.accept_expression(limit)
                self.skip(RE_TRIVIA)
                self.accept_whitespace_control()

                if self.source.startswith("}}", self.pos) or self.source.startswith(
                    "%}", self.pos
                ):
                    self.pos += 2
                    self.emit(TOKEN_OUT_END)

                elif self.source.startswith("}", self.pos):
                    self.pos += 1
                    self.emit(TOKEN_OUT_END)

            elif self.source.startswith("{%", self.pos):
                self.pos += 2

                # Tags must be closed by `%}`.
                # Markup delimiters are greedy and not string literal aware.
                limit = self.index(RE_TAG_END)

                if limit is not None:
                    self.emit(TOKEN_TAG_START)
                    self.accept_whitespace_control()
                    self.skip(RE_TRIVIA)
                    self.accept_tag(limit)

                elif self.scan_until(RE_MARKUP_START):
                    self.emit(TOKEN_TEXT)

                else:
                    # No more markup. Emit text to end of string.
                    self.pos = self.length
                    if self.start < self.pos:
                        self.emit(TOKEN_TEXT)
                    return None

            elif self.scan_until(RE_MARKUP_START):
                self.emit(TOKEN_TEXT)

            else:
                # No more markup. Emit text to end of string.
                self.pos = self.length
                if self.start < self.pos:
                    self.emit(TOKEN_TEXT)
                return None

    def accept_expression(
        self, limit: int, trivia: re.Pattern[str] = RE_TRIVIA
    ) -> None:
        # TODO: Benchmark with a local pos and source
        while self.pos < limit:
            ch = self.source[self.pos]

            if _is_trivia(ord(ch)):
                self.skip(RE_TRIVIA)

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
                else:
                    self.emit(TOKEN_IDENT)

            elif _is_number_ch(ord(ch)):
                if match := self.scan(RE_FLOAT):
                    self.emit(TOKEN_FLOAT)

                elif match := self.scan(RE_INT):
                    self.emit(TOKEN_INT)

                else:
                    assert False  # unreachable

            else:
                self.pos += 1
                self.emit(TOKEN_UNKNOWN)

    def accept_tag(self, limit: int) -> None:
        tag_name = self.scan(RE_TAG_NAME)

        if tag_name is not None:
            self.emit(TOKEN_TAG_NAME)

        if tag_name == "#":
            self.accept_inline_comment(limit)

        elif tag_name == "comment":
            self.accept_block_comment(limit)

        elif tag_name == "doc":
            self.accept_doc_comment(limit)

        elif tag_name == "raw":
            self.accept_raw_tag(limit)

        elif tag_name == "liquid":
            self.accept_line_statements(limit)

        else:
            self.accept_expression(limit)
            self.skip(RE_TRIVIA)
            self.accept_whitespace_control()
            if self.scan(RE_TAG_END):
                self.emit(TOKEN_TAG_END)

    def accept_inline_comment(self, limit: int) -> None:
        self.pos = limit
        self.emit(TOKEN_COMMENT)
        self.accept_whitespace_control()

        if self.source.startswith("%}", self.pos):
            self.pos += 2
            self.emit(TOKEN_TAG_END)

    def accept_block_comment(self, limit: int) -> None:
        self.skip(RE_TRIVIA)

        # Ignore everything up to the next delimiter.
        self.pos = limit
        self.accept_whitespace_control()
        if self.source.startswith("%}", self.pos):
            self.pos += 2
            self.emit(TOKEN_TAG_END)

        comment_depth = 1
        raw_depth = 0

        # Find the matching `{% endcomment %}` while allowing fully-formed,
        # nested comments and raw blocks.
        while 1:
            match = self.skip_until(RE_COMMENT_SEGMENT)

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
        self.accept_expression(limit)
        self.skip(RE_TRIVIA)
        self.accept_whitespace_control()

        if self.source.startswith("%}", self.pos):
            self.pos += 2
            self.emit(TOKEN_TAG_END)

        if self.scan_until(RE_END_DOC):
            self.emit(TOKEN_COMMENT)

        # Leave `{% enddoc %}` for scan_markup.

    def accept_raw_tag(self, limit: int) -> None:
        self.accept_expression(limit)
        self.skip(RE_TRIVIA)
        self.accept_whitespace_control()

        if self.source.startswith("%}", self.pos):
            self.pos += 2
            self.emit(TOKEN_TAG_END)

        if self.scan_until(RE_END_RAW):
            self.emit(TOKEN_TEXT)

        # Leave `{% endraw %}` for scan_markup.

    def accept_line_statements(self, limit: int) -> None:
        while self.pos < limit:
            self.skip(RE_TRIVIA)

            line_limit = self.source.find("\n", self.pos)
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

        if self.source.startswith("%}", self.pos):
            self.pos += 2
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


def _is_name_first_ch(ch: int) -> bool:
    return (ch >= 65 and ch <= 90) or (ch >= 97 and ch <= 122) or ch == 95


def _is_number_ch(ch: int) -> bool:
    return ch == 45 or (ch >= 48 and ch <= 57)


def _is_trivia(ch: int) -> bool:
    return ch == 32 or ch == 9 or ch == 10 or ch == 12 or ch == 13
