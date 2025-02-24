"""Tag expression argument helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from liquid.exceptions import LiquidSyntaxError
from liquid.token import TOKEN_ASSIGN
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_WORD

from .primitive import parse_primitive

if TYPE_CHECKING:
    from liquid import Environment
    from liquid import RenderContext
    from liquid import Token
    from liquid import TokenStream
    from liquid.expression import Expression


class KeywordArgument:
    """A name/value pair."""

    __slots__ = ("token", "name", "value")

    def __init__(self, token: Token, name: str, value: Expression) -> None:
        self.token = token
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return f"{self.name}:{self.value}"

    def evaluate(self, context: RenderContext) -> tuple[str, object]:
        return (self.name, self.value.evaluate(context))

    async def evaluate_async(self, context: RenderContext) -> tuple[str, object]:
        return (self.name, await self.value.evaluate_async(context))

    @staticmethod
    def parse(env: Environment, tokens: TokenStream) -> list[KeywordArgument]:
        """Parse a keyword arguments from _tokens_."""
        args: list[KeywordArgument] = []

        while True:
            token = next(tokens)

            if token.kind == TOKEN_COMMA:
                token = next(tokens)

            if token.kind == TOKEN_EOF:
                break

            if token.kind == TOKEN_WORD:
                # TODO: allow colon or assign
                tokens.eat(TOKEN_COLON)
                value = parse_primitive(env, tokens)
                args.append(KeywordArgument(token, token.value, value))
            else:
                raise LiquidSyntaxError(
                    f"expected an argument name, found {token.kind}", token=token
                )

        # TODO: expect EOS?
        return args


class PositionalArgument:
    """Just a value."""

    __slots__ = (
        "token",
        "value",
    )

    def __init__(self, value: Expression) -> None:
        self.token = value.token
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def evaluate(self, context: RenderContext) -> tuple[None, object]:
        return (None, self.value.evaluate(context))

    async def evaluate_async(self, context: RenderContext) -> tuple[None, object]:
        return (None, await self.value.evaluate_async(context))

    @staticmethod
    def parse(env: Environment, tokens: TokenStream) -> list[PositionalArgument]:
        """Parse a positional arguments from _tokens_."""
        args: list[PositionalArgument] = []

        while True:
            token = next(tokens)

            if token.kind == TOKEN_COMMA:
                token = next(tokens)

            if token.kind == TOKEN_EOF:
                break

            if token.kind == TOKEN_WORD:
                args.append(PositionalArgument(parse_primitive(env, tokens)))
            else:
                raise LiquidSyntaxError(
                    f"expected an argument, found {token.kind}", token=token
                )

        return args


class Parameter:
    """A name, possibly with a default value."""

    __slots__ = ("token", "name", "value")

    def __init__(self, token: Token, name: str, value: Expression | None) -> None:
        self.token = token
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return f"{self.name}:{self.value}" if self.value else self.name

    # TODO: static parse()


def parse_arguments(
    env: Environment, tokens: TokenStream
) -> tuple[list[PositionalArgument], list[KeywordArgument]]:
    """Parse arguments from _tokens_ until end of input."""
    args: list[PositionalArgument] = []
    kwargs: list[KeywordArgument] = []

    while True:
        token = next(tokens)

        if token.kind == TOKEN_COMMA:
            token = next(tokens)

        if token.kind == TOKEN_EOF:
            break

        if token.kind == TOKEN_WORD:
            if tokens.current.kind == TOKEN_COLON:
                # TODO: allow colon or assign
                tokens.eat(TOKEN_COLON)
                value = parse_primitive(env, tokens)
                kwargs.append(KeywordArgument(token, token.value, value))
            else:
                args.append(PositionalArgument(parse_primitive(env, tokens)))
        else:
            raise LiquidSyntaxError(
                f"expected an argument, found {token.kind}", token=token
            )

    return args, kwargs


# TODO: parse_macro_arguments
# TODO: parse_call_arguments
