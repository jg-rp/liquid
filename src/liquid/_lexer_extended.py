from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ._lexer import Lexer, State
from .tokens import *

if TYPE_CHECKING:
    from .environment import Environment

RE_TRIVIA = re.compile(r"[ \n\r\t\f]+")
RE_TAG_NAME = re.compile(r"#|[a-zA-Z0-9_]+")
RE_LINE_TRIVIA = re.compile(r"[ \r\t\f]+")


class ExtendedLexer(Lexer):
    """A tokenizer that accepts alternative markup delimiters."""

    __slots__ = (
        "comment_end",
        "comment_start",
        "out_end",
        "out_start",
        "re_markup_start",
        "tag_end",
        "tag_start",
    )

    def __init__(self, env: Environment, source: str) -> None:
        super().__init__(env, source)
        self.comment_start = env.comment_start_delimiter
        self.comment_end = env.comment_end_delimiter
        self.out_start = env.output_start_delimiter
        self.out_end = env.output_end_delimiter
        self.tag_start = env.tag_start_delimiter
        self.tag_end = env.tag_end_delimiter

        self.re_markup_start = re.compile(
            rf"{re.escape(self.out_start)}|"
            rf"{re.escape(self.tag_start)}|"
            rf"{re.escape(self.comment_start)}"
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

            elif self.source.startswith(self.comment_start, self.pos):
                self.accept_comment()

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
            limit = self.source.find(self.tag_end, self.pos)
            if limit == -1:
                return
            self.accept_inline_comment(limit)

        elif tag_name == "comment":
            limit = self.source.find(self.tag_end, self.pos)
            if limit == -1:
                return
            self.accept_block_comment(limit)

        elif tag_name == "doc":
            limit = self.source.find(self.tag_end, self.pos)
            if limit == -1:
                return
            self.accept_doc_comment(limit)

        elif tag_name == "raw":
            limit = self.source.find(self.tag_end, self.pos)
            if limit == -1:
                return
            self.accept_raw_tag(limit)

        elif tag_name == "liquid":
            self.accept_line_statements()

        else:
            self.accept_expression()
            self.skip(RE_TRIVIA)
            self.accept_whitespace_control()

            if self.source.startswith(self.tag_end, self.pos):
                self.pos += len(self.tag_end)
                self.emit(TOKEN_TAG_END)

    def accept_comment(self) -> None:
        # TODO:
        raise NotImplementedError

    def accept_expression(self, trivia: re.Pattern[str] = RE_TRIVIA) -> None:
        # TODO:
        raise NotImplementedError
