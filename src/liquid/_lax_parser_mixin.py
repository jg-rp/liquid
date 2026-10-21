from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Protocol

from . import tokens
from .exceptions import LiquidSyntaxError
from .tags import ErrorNode
from .tokens import Token, TokenKind, span

if TYPE_CHECKING:
    from ._markup import Markup


class _LegacyParserProtocol(Protocol):
    def parse_output(self) -> Markup: ...
    def parse_tag(self) -> Markup: ...
    def current(self) -> Token: ...
    def next(self) -> Token: ...
    def kind(self) -> TokenKind: ...
    def carry_whitespace_control(self) -> None: ...


class LaxParserMixin(ABC, _LegacyParserProtocol):
    """A legacy Liquid parser that captures and suppresses syntax errors.

    Other parse-time errors such as ``ResourceLimitError`` will still be raised.
    """

    __slots__ = ()

    def parse_output(self) -> Markup:
        try:
            return super().parse_output()  # type: ignore
        except LiquidSyntaxError as err:
            return self.error(err)

    def parse_tag(self) -> Markup:
        try:
            return super().parse_tag()  # type: ignore
        except LiquidSyntaxError as err:
            return self.error(err)

    def error(self, err: LiquidSyntaxError) -> ErrorNode:
        # Skip tokens up to the next delimiter.
        start_token = self.current()

        while 1:
            match self.kind():
                case (
                    tokens.TOKEN_EOI
                    | tokens.TOKEN_COMMENT_END
                    | tokens.TOKEN_COMMENT_START
                    | tokens.TOKEN_OUT_END
                    | tokens.TOKEN_OUT_START
                    | tokens.TOKEN_TAG_END
                    | tokens.TOKEN_TAG_START
                ):
                    break
                case tokens.TOKEN_WC:
                    self.carry_whitespace_control()
                case _:
                    self.pos += 1  # type: ignore

        end_token = self.next()
        return ErrorNode(span(start_token, end_token), err)
