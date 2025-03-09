"""Built-in loop expressions."""

from __future__ import annotations

from itertools import islice
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterator
from typing import Mapping
from typing import Sequence
from typing import Union

from liquid import Mode
from liquid.exceptions import LiquidSyntaxError
from liquid.exceptions import LiquidTypeError
from liquid.expression import Expression
from liquid.limits import to_int
from liquid.token import TOKEN_ASSIGN
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COLS
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_CONTINUE
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_IN
from liquid.token import TOKEN_LIMIT
from liquid.token import TOKEN_OFFSET
from liquid.token import TOKEN_REVERSED

from .primitive import StringLiteral
from .primitive import parse_identifier
from .primitive import parse_primitive

if TYPE_CHECKING:
    from liquid import Environment
    from liquid import RenderContext
    from liquid import TokenStream
    from liquid.token import Token


class LoopExpression(Expression):
    """An expression for the `for` and `tablerow` tag."""

    __slots__ = ("identifier", "iterable", "limit", "offset", "reversed", "cols")

    def __init__(
        self,
        token: Token,
        identifier: str,
        iterable: Expression,
        *,
        limit: Expression | None,
        offset: Expression | None,
        reversed_: bool,
        cols: Expression | None,
    ) -> None:
        super().__init__(token)
        self.identifier = identifier
        self.iterable = iterable
        self.limit = limit
        self.offset = offset
        self.reversed = reversed_
        self.cols = cols

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, LoopExpression)
            and self.identifier == other.identifier
            and self.iterable == other.iterable
            and self.limit == other.limit
            and self.offset == other.offset
            and self.cols == other.cols
            and self.reversed == other.reversed
        )

    def __str__(self) -> str:
        buf = [f"{self.identifier} in", str(self.iterable)]

        if self.limit is not None:
            buf.append(f"limit:{self.limit}")

        if self.offset is not None:
            buf.append(f"offset:{self.offset}")

        if self.cols is not None:
            buf.append(f"cols:{self.cols}")

        if self.reversed:
            buf.append("reversed")

        return " ".join(buf)

    def _to_iter(
        self, obj: object, context: RenderContext
    ) -> tuple[Iterator[Any], int]:
        if isinstance(obj, Mapping):
            return iter(obj.items()), len(obj)
        if isinstance(obj, range):
            return iter(obj), len(obj)
        if isinstance(obj, str) and not context.env.string_sequences:
            return iter([obj]), 1
        if isinstance(obj, Sequence):
            return iter(obj), len(obj)

        raise LiquidTypeError(
            f"expected an iterable at '{self.iterable}', found '{obj}'",
            token=self.token,
        )

    def _to_int(self, obj: object, *, token: Token) -> int:
        try:
            return to_int(obj)
        except (ValueError, TypeError) as err:
            raise LiquidTypeError(
                f"expected an integer, found {obj.__class__.__name__}",
                token=token,
            ) from err

    def _slice(
        self,
        it: Iterator[object],
        length: int,
        context: RenderContext,
        *,
        limit: int | None,
        offset: int | str | None,
    ) -> tuple[Iterator[object], int]:
        offset_key = f"{self.identifier}-{self.iterable}"

        if limit is None and offset is None:
            context.stopindex(key=offset_key, index=length)
            if self.reversed:
                return reversed(list(it)), length
            return it, length

        if offset == "continue":
            offset = context.stopindex(key=offset_key)
            length = max(length - offset, 0)
        elif offset is not None:
            assert isinstance(offset, int), f"found {offset!r}"
            length = max(length - offset, 0)

        if limit is not None:
            length = min(length, limit)

        stop = offset + length if offset else length
        context.stopindex(key=offset_key, index=stop)
        it = islice(it, offset, stop)

        if self.reversed:
            return reversed(list(it)), length
        return it, length

    def evaluate(self, context: RenderContext) -> tuple[Iterator[object], int]:
        it, length = self._to_iter(self.iterable.evaluate(context), context)
        limit = (
            self._to_int(self.limit.evaluate(context), token=self.limit.token)
            if self.limit
            else None
        )

        if isinstance(self.offset, StringLiteral):
            offset: Union[str, int, None] = self.offset.value
            if offset != "continue":
                offset = self._to_int(offset, token=self.offset.token)
        elif self.offset is None:
            offset = None
        else:
            offset = self._to_int(
                self.offset.evaluate(context), token=self.offset.token
            )

        return self._slice(it, length, context, limit=limit, offset=offset)

    async def evaluate_async(
        self, context: RenderContext
    ) -> tuple[Iterator[object], int]:
        it, length = self._to_iter(await self.iterable.evaluate_async(context), context)
        limit = (
            self._to_int(
                await self.limit.evaluate_async(context), token=self.limit.token
            )
            if self.limit
            else None
        )

        if self.offset is None:
            offset: str | int | None = None
        elif isinstance(self.offset, StringLiteral):
            offset = self.offset.evaluate(context)
            if offset != "continue":
                offset = self._to_int(offset, token=self.offset.token)
        else:
            offset = self._to_int(
                await self.offset.evaluate_async(context), token=self.offset.token
            )

        return self._slice(it, length, context, limit=limit, offset=offset)

    def children(self) -> list[Expression]:
        children = [self.iterable]

        if self.limit is not None:
            children.append(self.limit)

        if self.offset is not None:
            children.append(self.offset)

        if self.cols is not None:
            children.append(self.cols)

        return children

    @staticmethod
    def parse(env: Environment, tokens: TokenStream) -> LoopExpression:
        """Parse a loop expression from _tokens_."""
        token = tokens.current
        identifier = parse_identifier(env, tokens)
        tokens.eat(TOKEN_IN)
        iterable = parse_primitive(env, tokens)

        reversed_ = False
        offset: Expression | None = None
        limit: Expression | None = None
        cols: Expression | None = None

        argument_separators = (
            (TOKEN_COLON, TOKEN_ASSIGN) if env.keyword_assignment else (TOKEN_COLON,)
        )

        # Leading commas are OK
        if tokens.current.kind == TOKEN_COMMA:
            next(tokens)

        while True:
            arg_token = next(tokens)
            kind = arg_token.kind

            if kind == TOKEN_LIMIT:
                tokens.eat_one_of(*argument_separators)
                limit = parse_primitive(env, tokens)
            elif kind == TOKEN_REVERSED:
                reversed_ = True
            elif kind == TOKEN_OFFSET:
                tokens.eat_one_of(*argument_separators)
                offset_token = tokens.current
                if offset_token.kind == TOKEN_CONTINUE:
                    next(tokens)
                    offset = StringLiteral(token=offset_token, value="continue")
                else:
                    offset = parse_primitive(env, tokens)
            elif kind == TOKEN_COLS:
                tokens.eat_one_of(*argument_separators)
                cols = parse_primitive(env, tokens)
            elif kind == TOKEN_COMMA:
                if env.mode == Mode.STRICT and tokens.peek.kind == TOKEN_COMMA:
                    raise LiquidSyntaxError(
                        f"expected 'reversed', 'offset' or 'limit', found {kind}",
                        token=tokens.peek,
                    )
                continue
            elif kind == TOKEN_EOF:
                break
            else:
                raise LiquidSyntaxError(
                    "expected 'reversed', 'offset' or 'limit'",
                    token=arg_token,
                )

        tokens.eat(TOKEN_EOF)
        return LoopExpression(
            token,
            identifier,
            iterable,
            limit=limit,
            offset=offset,
            reversed_=reversed_,
            cols=cols,
        )
