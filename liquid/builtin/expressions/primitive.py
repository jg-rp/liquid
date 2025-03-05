"""Built-in primitive expressions."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Any
from typing import Generic
from typing import TypeVar
from typing import Union

from markupsafe import Markup

from liquid.exceptions import LiquidSyntaxError
from liquid.expression import Expression
from liquid.limits import to_int
from liquid.token import TOKEN_BLANK
from liquid.token import TOKEN_EMPTY
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_IDENTSTRING
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_NULL
from liquid.token import TOKEN_RANGE
from liquid.token import TOKEN_RANGE_LITERAL
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_TRUE
from liquid.token import TOKEN_WORD

from .path import Path

if TYPE_CHECKING:
    from liquid import Environment
    from liquid import RenderContext
    from liquid import Token
    from liquid import TokenStream


class Nil(Expression):
    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        return other is None or isinstance(other, Nil)

    def __str__(self) -> str:  # pragma: no cover
        return ""

    def evaluate(self, _: RenderContext) -> None:
        return None

    def children(self) -> list[Expression]:
        return []


class Empty(Expression):
    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Empty):
            return True
        return isinstance(other, (list, dict, str)) and not other

    def __str__(self) -> str:  # pragma: no cover
        return ""

    def evaluate(self, _: RenderContext) -> Empty:
        return self

    def children(self) -> list[Expression]:
        return []


class Blank(Expression):
    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str) and (not other or other.isspace()):
            return True
        if isinstance(other, (list, dict)) and not other:
            return True
        return isinstance(other, Blank)

    def __str__(self) -> str:  # pragma: no cover
        return ""

    def evaluate(self, _: RenderContext) -> Blank:
        return self

    def children(self) -> list[Expression]:
        return []


class Continue(Expression):
    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Continue)

    def __str__(self) -> str:  # pragma: no cover
        return "continue"

    def evaluate(self, _: RenderContext) -> int:
        return 0

    def children(self) -> list[Expression]:
        return []


T = TypeVar("T")


class Literal(Expression, Generic[T]):
    __slots__ = ("value",)

    def __init__(self, token: Token, value: T):
        super().__init__(token)
        self.value = value

    def __str__(self) -> str:
        return repr(self.value)

    def __eq__(self, other: object) -> bool:
        return self.value == other

    def __hash__(self) -> int:
        return hash(self.value)

    def __sizeof__(self) -> int:
        return sys.getsizeof(self.value)

    def evaluate(self, _: RenderContext) -> object:
        return self.value

    def children(self) -> list[Expression]:
        return []


class TrueLiteral(Literal[bool]):
    __slots__ = ()

    def __init__(self, token: Token):
        super().__init__(token, True)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, TrueLiteral)

    def __str__(self) -> str:
        return "true"


class FalseLiteral(Literal[bool]):
    __slots__ = ()

    def __init__(self, token: Token):
        super().__init__(token, False)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, FalseLiteral)

    def __str__(self) -> str:
        return "false"


class StringLiteral(Literal[str]):
    __slots__ = ()

    def __init__(self, token: Token, value: str):
        super().__init__(token, value)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, StringLiteral) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __sizeof__(self) -> int:
        return sys.getsizeof(self.value)

    def evaluate(self, context: RenderContext) -> Union[str, Markup]:
        if context.autoescape:
            return Markup(self.value)
        return self.value


class IntegerLiteral(Literal[int]):
    __slots__ = ()

    def __init__(self, token: Token, value: int):
        super().__init__(token, value)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, IntegerLiteral) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class FloatLiteral(Literal[float]):
    __slots__ = ()

    def __init__(self, token: Token, value: float):
        super().__init__(token, value)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, FloatLiteral) and self.value == other.value


class RangeLiteral(Expression):
    __slots__ = ("start", "stop")

    def __init__(self, token: Token, start: Expression, stop: Expression):
        super().__init__(token)
        self.start = start
        self.stop = stop

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, RangeLiteral)
            and self.start == other.start
            and self.stop == other.stop
        )

    def __str__(self) -> str:
        return f"({self.start}..{self.stop})"

    def __hash__(self) -> int:
        return hash((self.start, self.stop))

    def __sizeof__(self) -> int:
        return (
            super().__sizeof__() + sys.getsizeof(self.start) + sys.getsizeof(self.stop)
        )

    def _make_range(self, start: Any, stop: Any) -> range:
        try:
            start = to_int(start)
        except ValueError:
            start = 0

        try:
            stop = to_int(stop)
        except ValueError:
            stop = 0

        # Descending ranges don't work
        if start > stop:
            return range(0)

        return range(start, stop + 1)

    def evaluate(self, context: RenderContext) -> range:
        return self._make_range(
            self.start.evaluate(context), self.stop.evaluate(context)
        )

    async def evaluate_async(self, context: RenderContext) -> range:
        return self._make_range(
            await self.start.evaluate_async(context),
            await self.stop.evaluate_async(context),
        )

    def children(self) -> list[Expression]:
        return [self.start, self.stop]

    @staticmethod
    def parse(env: Environment, tokens: TokenStream) -> RangeLiteral:
        token = tokens.eat(TOKEN_RANGE_LITERAL)
        start = parse_primitive(env, tokens)
        tokens.eat(TOKEN_RANGE)
        stop = parse_primitive(env, tokens)
        tokens.eat(TOKEN_RPAREN)
        return RangeLiteral(token, start, stop)


def parse_primitive(env: Environment, tokens: TokenStream) -> Expression:  # noqa: PLR0911
    """Parse a primitive expression from _tokens_."""
    token = tokens.current
    kind = token.kind

    if kind == TOKEN_TRUE:
        return TrueLiteral(next(tokens))
    if kind == TOKEN_FALSE:
        return FalseLiteral(next(tokens))
    if kind in (TOKEN_NIL, TOKEN_NULL):
        return Nil(next(tokens))
    if kind == TOKEN_INTEGER:
        return IntegerLiteral(next(tokens), to_int(token.value))
    if kind == TOKEN_FLOAT:
        return FloatLiteral(next(tokens), float(token.value))
    if kind == TOKEN_STRING:
        return StringLiteral(next(tokens), token.value)
    if kind == TOKEN_RANGE_LITERAL:
        return RangeLiteral.parse(env, tokens)
    if kind == TOKEN_EMPTY:
        return Empty(next(tokens))
    if kind == TOKEN_BLANK:
        return Blank(next(tokens))
    if kind in (TOKEN_WORD, TOKEN_IDENTSTRING, TOKEN_LBRACKET):
        return Path.parse(env, tokens)

    raise LiquidSyntaxError(
        f"expected a primitive expression, found {token.kind}", token=token
    )


class Identifier(str):
    """A string, token pair."""

    def __new__(
        cls, obj: object, *args: object, token: Token, **kwargs: object
    ) -> Identifier:
        instance = super().__new__(cls, obj, *args, **kwargs)
        instance.token = token
        return instance

    def __init__(
        self,
        obj: object,  # noqa: ARG002
        *args: object,  # noqa: ARG002
        token: Token,  # noqa: ARG002
        **kwargs: object,  # noqa: ARG002
    ) -> None:
        super().__init__()
        self.token: Token

    def __eq__(self, value: object) -> bool:
        return super().__eq__(value)

    def __hash__(self) -> int:
        return super().__hash__()


def parse_identifier(
    env: Environment,
    tokens: TokenStream,
    *,
    allow_trailing_question_mark: bool = True,
) -> Identifier:
    """Parse a word that might otherwise be considered a path with one segment."""
    expr = parse_primitive(env, tokens)

    if isinstance(expr, IntegerLiteral):
        return Identifier(str(expr.value), token=expr.token)

    if not isinstance(expr, Path):
        raise LiquidSyntaxError(
            f"expected an identifier, found {expr.__class__.__name__}", token=expr.token
        )

    if len(expr.path) != 1:
        raise LiquidSyntaxError(
            "expected an identifier, found a path with multiple segments",
            token=expr.token,
        )

    word = expr.path[0]

    if not isinstance(word, str):
        raise LiquidSyntaxError(
            f"expected an identifier, found {word.__class__.__name__}",
            token=expr.token,
        )

    if not allow_trailing_question_mark and word.endswith("?"):
        raise LiquidSyntaxError("invalid identifier", token=expr.token)

    return Identifier(word, token=expr.token)


def parse_name(env: Environment, tokens: TokenStream) -> Identifier:
    """Parse a quoted or unquoted word."""
    expr = parse_primitive(env, tokens)

    if isinstance(expr, StringLiteral):
        return Identifier(expr.value, token=expr.token)

    if not isinstance(expr, Path):
        raise LiquidSyntaxError(
            f"expected a name, found {expr.__class__.__name__}", token=expr.token
        )

    if len(expr.path) != 1:
        raise LiquidSyntaxError(
            f"expected a name, found a path with multiple segments, {expr.path!r}",
            token=expr.token,
        )

    word = expr.path[0]

    if not isinstance(word, str):
        raise LiquidSyntaxError(
            f"expected a name, found {word.__class__.__name__}",
            token=expr.token,
        )

    return Identifier(word, token=expr.token)


def parse_string_or_path(
    env: Environment, tokens: TokenStream
) -> Union[Path, StringLiteral]:
    """Parse a string literal or path to a string variable."""
    expr = parse_primitive(env, tokens)
    if not isinstance(expr, (Path, StringLiteral)):
        raise LiquidSyntaxError(
            f"expected an string or variable, found {expr.__class__.__name__}",
            token=expr.token,
        )
    return expr


def is_empty(obj: object) -> bool:
    """Return True if _obj_ is considered empty."""
    return isinstance(obj, (list, dict, str)) and not obj
