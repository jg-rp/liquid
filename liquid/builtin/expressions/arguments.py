"""Tag expression argument helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from liquid import Mode
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
        argument_separators = (
            (TOKEN_COLON, TOKEN_ASSIGN) if env.keyword_assignment else (TOKEN_COLON,)
        )

        args: list[KeywordArgument] = []

        # Leading commas are OK
        if tokens.current.kind == TOKEN_COMMA:
            next(tokens)

        while True:
            token = next(tokens)

            if token.kind == TOKEN_COMMA:
                token = next(tokens)

            if token.kind == TOKEN_EOF:
                break

            if token.kind == TOKEN_WORD:
                tokens.eat_one_of(*argument_separators)
                value = parse_primitive(env, tokens)
                args.append(KeywordArgument(token, token.value, value))
                if env.mode == Mode.STRICT and tokens.current.kind == TOKEN_WORD:
                    raise LiquidSyntaxError(
                        "expected a comma separated list of arguments, "
                        f"found {tokens.current.kind}",
                        token=tokens.current,
                    )
            else:
                raise LiquidSyntaxError(
                    f"expected an argument name, found {token.kind}", token=token
                )

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
            if tokens.current.kind == TOKEN_COMMA:
                next(tokens)

            if tokens.current.kind == TOKEN_EOF:
                break

            args.append(PositionalArgument(parse_primitive(env, tokens)))

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

    @staticmethod
    def parse(env: Environment, tokens: TokenStream) -> dict[str, Parameter]:
        """Parse macro tag parameters from _tokens_."""
        params: dict[str, Parameter] = {}
        argument_separators = (
            (TOKEN_COLON, TOKEN_ASSIGN) if env.keyword_assignment else (TOKEN_COLON,)
        )

        while True:
            token = next(tokens)

            if token.kind == TOKEN_COMMA:
                # Leading and/or trailing commas are OK.
                token = next(tokens)

            if token.kind == TOKEN_EOF:
                break

            if token.kind == TOKEN_WORD:
                if tokens.current.kind in argument_separators:
                    # A parameter with a default value
                    next(tokens)  # Move past ":" or "="
                    value = parse_primitive(env, tokens)
                    params[token.value] = Parameter(token, token.value, value)
                else:
                    params[token.value] = Parameter(token, token.value, None)
            else:
                raise LiquidSyntaxError(
                    f"expected a parameter list, found {token.kind}",
                    token=token,
                )

        return params


def parse_arguments(
    env: Environment, tokens: TokenStream
) -> tuple[list[PositionalArgument], list[KeywordArgument]]:
    """Parse arguments from _tokens_ until end of input."""
    args: list[PositionalArgument] = []
    kwargs: list[KeywordArgument] = []
    argument_separators = (
        (TOKEN_COLON, TOKEN_ASSIGN) if env.keyword_assignment else (TOKEN_COLON,)
    )

    # Leading commas are OK
    if tokens.current.kind == TOKEN_COMMA:
        next(tokens)

    while True:
        token = tokens.current

        if token.kind == TOKEN_EOF:
            break

        if token.kind == TOKEN_WORD:
            if tokens.peek.kind in argument_separators:
                name_token = next(tokens)
                next(tokens)  # = or :
                value = parse_primitive(env, tokens)
                kwargs.append(KeywordArgument(name_token, token.value, value))
            else:
                args.append(PositionalArgument(parse_primitive(env, tokens)))
        else:
            # A primitive as a positional argument
            args.append(PositionalArgument(parse_primitive(env, tokens)))

        if tokens.current.kind != TOKEN_COMMA:
            break

        tokens.eat(TOKEN_COMMA)

    return args, kwargs
