"""Built-in filtered expressions."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Union

from liquid import Mode
from liquid.exceptions import FilterArgumentError
from liquid.exceptions import LiquidSyntaxError
from liquid.exceptions import LiquidTypeError
from liquid.exceptions import UnknownFilterError
from liquid.expression import Expression
from liquid.token import TOKEN_ASSIGN
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_DPIPE
from liquid.token import TOKEN_ELSE
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_IF
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_NULL
from liquid.token import TOKEN_PIPE
from liquid.token import TOKEN_RANGE_LITERAL
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_TRUE
from liquid.token import TOKEN_WORD

from .arguments import KeywordArgument
from .arguments import PositionalArgument
from .logical import BooleanExpression
from .primitive import parse_primitive

if TYPE_CHECKING:
    from liquid import Environment
    from liquid import RenderContext
    from liquid import TokenStream
    from liquid.token import Token


FILTER_TOKENS = set(  # noqa: C405
    [
        TOKEN_INTEGER,
        TOKEN_FLOAT,
        TOKEN_STRING,
        TOKEN_FALSE,
        TOKEN_TRUE,
        TOKEN_NIL,
        TOKEN_NULL,
        TOKEN_RANGE_LITERAL,
        TOKEN_LBRACKET,
        TOKEN_LPAREN,
        TOKEN_WORD,
    ]
)


class FilteredExpression(Expression):
    """An expression for the built-in `assign` tag and output statement."""

    __slots__ = ("left", "filters")

    def __init__(
        self,
        token: Token,
        left: Expression,
        filters: list[Filter] | None = None,
    ) -> None:
        super().__init__(token=token)
        self.left = left
        self.filters = filters

    def __str__(self) -> str:
        filters = (
            " | " + " | ".join(str(f) for f in self.filters) if self.filters else ""
        )
        return f"{self.left}{filters}"

    def evaluate(self, context: RenderContext) -> object:
        rv = self.left.evaluate(context)
        if self.filters:
            for f in self.filters:
                rv = f.evaluate(rv, context)
        return rv

    async def evaluate_async(self, context: RenderContext) -> object:
        rv = await self.left.evaluate_async(context)
        if self.filters:
            for f in self.filters:
                rv = await f.evaluate_async(rv, context)
        return rv

    def children(self) -> list[Expression]:
        children = [self.left]
        if self.filters:
            for filter_ in self.filters:
                children.extend(filter_.children())
        return children

    @staticmethod
    def parse(
        env: Environment, tokens: TokenStream
    ) -> Union[FilteredExpression, TernaryFilteredExpression]:
        """Parse a filtered expression from _tokens_."""
        left = parse_primitive(env, tokens)
        filters = Filter.parse(env, tokens, delim=(TOKEN_PIPE,))

        if tokens.current.kind == TOKEN_IF:
            if not env.ternary_expressions:
                raise LiquidSyntaxError(
                    "disallowed ternary expression", token=tokens.current
                )

            return TernaryFilteredExpression.parse(
                env, FilteredExpression(left.token, left, filters), tokens
            )

        tokens.eat(TOKEN_EOF)
        return FilteredExpression(left.token, left, filters)


class TernaryFilteredExpression(Expression):
    __slots__ = ("left", "condition", "alternative", "filters", "tail_filters")

    def __init__(
        self,
        token: Token,
        left: FilteredExpression,
        condition: Expression,
        alternative: Expression | None = None,
        filters: list[Filter] | None = None,
        tail_filters: list[Filter] | None = None,
    ) -> None:
        super().__init__(token=token)
        self.left = left
        self.condition = condition
        self.alternative = alternative
        self.filters = filters
        self.tail_filters = tail_filters

    def __str__(self) -> str:
        buf = [f"{self.left} if {self.condition}"]

        if self.alternative:
            buf.append(f" else {self.alternative}")

        if self.filters:
            buf.append(" | " + " | ".join(str(f) for f in self.filters))

        if self.tail_filters:
            buf.append(" || " + " | ".join(str(f) for f in self.tail_filters))

        return "".join(buf)

    def evaluate(self, context: RenderContext) -> object:
        rv: object = None

        if self.condition.evaluate(context):
            rv = self.left.evaluate(context)
        elif self.alternative:
            rv = self.alternative.evaluate(context)
            if self.filters:
                for f in self.filters:
                    rv = f.evaluate(rv, context)

        if self.tail_filters:
            for f in self.tail_filters:
                rv = f.evaluate(rv, context)

        return rv

    async def evaluate_async(self, context: RenderContext) -> object:
        rv: object = None

        if await self.condition.evaluate_async(context):
            rv = await self.left.evaluate_async(context)
        elif self.alternative:
            rv = await self.alternative.evaluate_async(context)
            if self.filters:
                for f in self.filters:
                    rv = await f.evaluate_async(rv, context)

        if self.tail_filters:
            for f in self.tail_filters:
                rv = await f.evaluate_async(rv, context)

        return rv

    def children(self) -> list[Expression]:
        children = self.left.children()
        children.append(self.condition)

        if self.alternative:
            children.append(self.alternative)

        if self.filters:
            for filter_ in self.filters:
                children.extend(filter_.children())

        if self.tail_filters:
            for filter_ in self.tail_filters:
                children.extend(filter_.children())

        return children

    @staticmethod
    def parse(
        env: Environment, expr: FilteredExpression, tokens: TokenStream
    ) -> TernaryFilteredExpression:
        """Parse a ternary expression from _tokens_."""
        tokens.eat(TOKEN_IF)
        condition = BooleanExpression.parse(env, tokens, inline=True)
        alternative: Expression | None = None
        filters: list[Filter] | None = None
        tail_filters: list[Filter] | None = None

        if tokens.current.kind == TOKEN_ELSE:
            next(tokens)  # else
            alternative = parse_primitive(env, tokens)

            if tokens.current.kind == TOKEN_PIPE:
                filters = Filter.parse(env, tokens, delim=(TOKEN_PIPE,))

        if tokens.current.kind == TOKEN_DPIPE:
            tail_filters = Filter.parse(env, tokens, delim=(TOKEN_PIPE, TOKEN_DPIPE))

        tokens.eat(TOKEN_EOF)
        return TernaryFilteredExpression(
            expr.token, expr, condition, alternative, filters, tail_filters
        )


class Filter:
    __slots__ = ("name", "args", "token")

    def __init__(
        self,
        token: Token,
        name: str,
        arguments: list[KeywordArgument | PositionalArgument],
    ) -> None:
        self.token = token
        self.name = name
        self.args = arguments

    def __str__(self) -> str:
        if self.args:
            return f"{self.name}: {', '.join(str(arg) for arg in self.args)}"
        return self.name

    def validate_filter_arguments(self, env: Environment) -> None:
        try:
            func = env.filters[self.name]
        except KeyError as err:
            raise UnknownFilterError(
                f"unknown filter '{self.name}'", token=self.token
            ) from err

        if hasattr(func, "validate"):
            func.validate(env, self.token, self.name, self.args)

    def evaluate(self, left: object, context: RenderContext) -> object:
        func = context.filter(self.name, token=self.token)
        positional_args, keyword_args = self.evaluate_args(context)
        try:
            return func(left, *positional_args, **keyword_args)
        except TypeError as err:
            raise LiquidTypeError(f"{self.name}: {err}", token=self.token) from err
        except (LiquidTypeError, FilterArgumentError) as err:
            err.token = self.token
            raise err

    async def evaluate_async(self, left: object, context: RenderContext) -> object:
        func = context.filter(self.name, token=self.token)
        positional_args, keyword_args = await self.evaluate_args_async(context)

        try:
            if hasattr(func, "filter_async"):
                return await func.filter_async(left, *positional_args, **keyword_args)
            return func(left, *positional_args, **keyword_args)
        except TypeError as err:
            raise LiquidTypeError(f"{self.name}: {err}", token=self.token) from err
        except (LiquidTypeError, FilterArgumentError) as err:
            err.token = self.token
            raise err

    def evaluate_args(
        self, context: RenderContext
    ) -> tuple[list[object], dict[str, object]]:
        positional_args: list[object] = []
        keyword_args: dict[str, object] = {}
        for arg in self.args:
            name, value = arg.evaluate(context)
            if name:
                keyword_args[name] = value
            else:
                positional_args.append(value)

        return positional_args, keyword_args

    async def evaluate_args_async(
        self, context: RenderContext
    ) -> tuple[list[object], dict[str, object]]:
        positional_args: list[object] = []
        keyword_args: dict[str, object] = {}
        for arg in self.args:
            name, value = await arg.evaluate_async(context)
            if name:
                keyword_args[name] = value
            else:
                positional_args.append(value)

        return positional_args, keyword_args

    def children(self) -> list[Expression]:
        return [arg.value for arg in self.args]

    @staticmethod
    def parse(
        env: Environment, tokens: TokenStream, *, delim: tuple[str, ...]
    ) -> list[Filter]:
        """Parse filters from _tokens_."""
        filters: list[Filter] = []
        argument_separators = (
            (TOKEN_COLON, TOKEN_ASSIGN) if env.keyword_assignment else (TOKEN_COLON,)
        )

        while tokens.current.kind in delim:
            next(tokens)
            token = tokens.eat(TOKEN_WORD)
            args: list[Union[KeywordArgument, PositionalArgument]] = []

            if tokens.current.kind != TOKEN_COLON:
                # No arguments
                filters.append(Filter(token, token.value, args))
                continue

            tokens.eat(TOKEN_COLON)
            while True:
                tok = tokens.current
                if tok.kind == TOKEN_WORD:
                    if tokens.peek.kind in argument_separators:
                        next(tokens)  # word
                        next(tokens)  # : or =
                        args.append(
                            KeywordArgument(
                                tok, tok.value, parse_primitive(env, tokens)
                            )
                        )
                    else:
                        args.append(PositionalArgument(parse_primitive(env, tokens)))

                    if tokens.current.kind in FILTER_TOKENS:
                        raise LiquidSyntaxError(
                            "expected a comma separated list of arguments, "
                            f"found {tokens.current.kind}",
                            token=tokens.current,
                        )
                elif tok.kind in FILTER_TOKENS:
                    args.append(PositionalArgument(parse_primitive(env, tokens)))

                    # There should be a comma between filter tokens.
                    if tokens.current.kind in FILTER_TOKENS:
                        raise LiquidSyntaxError(
                            "expected a comma separated list of arguments, "
                            f"found {tokens.current.kind}",
                            token=tokens.current,
                        )
                elif tok.kind == TOKEN_COMMA:
                    if env.mode == Mode.STRICT and tokens.peek.kind == TOKEN_COMMA:
                        raise LiquidSyntaxError(
                            "expected a comma separated list of arguments, "
                            f"found {tokens.peek.kind}",
                            token=tokens.peek,
                        )
                    next(tokens)
                else:
                    break

            filters.append(Filter(token, token.value, args))

        return filters
