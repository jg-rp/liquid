"""Built-in logical expressions."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from typing import Collection

from liquid.exceptions import LiquidSyntaxError
from liquid.exceptions import LiquidTypeError
from liquid.expression import Expression
from liquid.limits import to_int
from liquid.token import TOKEN_AND
from liquid.token import TOKEN_BLANK
from liquid.token import TOKEN_CONTAINS
from liquid.token import TOKEN_EMPTY
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_EQ
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_GE
from liquid.token import TOKEN_GT
from liquid.token import TOKEN_IDENTSTRING
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_LE
from liquid.token import TOKEN_LG
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_LT
from liquid.token import TOKEN_NE
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_NOT
from liquid.token import TOKEN_NULL
from liquid.token import TOKEN_OR
from liquid.token import TOKEN_RANGE_LITERAL
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_TRUE
from liquid.token import TOKEN_WORD
from liquid.token import Token
from liquid.undefined import is_undefined

from .path import Path
from .primitive import Blank
from .primitive import Empty
from .primitive import FalseLiteral
from .primitive import FloatLiteral
from .primitive import IntegerLiteral
from .primitive import Nil
from .primitive import RangeLiteral
from .primitive import StringLiteral
from .primitive import TrueLiteral

if TYPE_CHECKING:
    from liquid import Environment
    from liquid import RenderContext
    from liquid import TokenStream

PRECEDENCE_LOWEST = 1
PRECEDENCE_LOGICAL_RIGHT = 2
PRECEDENCE_LOGICAL_OR = 3
PRECEDENCE_LOGICAL_AND = 4
PRECEDENCE_RELATIONAL = 5
PRECEDENCE_MEMBERSHIP = 6
PRECEDENCE_PREFIX = 7

PRECEDENCES = {
    TOKEN_EQ: PRECEDENCE_RELATIONAL,
    TOKEN_LT: PRECEDENCE_RELATIONAL,
    TOKEN_GT: PRECEDENCE_RELATIONAL,
    TOKEN_NE: PRECEDENCE_RELATIONAL,
    TOKEN_LG: PRECEDENCE_RELATIONAL,
    TOKEN_LE: PRECEDENCE_RELATIONAL,
    TOKEN_GE: PRECEDENCE_RELATIONAL,
    TOKEN_CONTAINS: PRECEDENCE_MEMBERSHIP,
    # TOKEN_IN: PRECEDENCE_MEMBERSHIP,
    TOKEN_AND: PRECEDENCE_LOGICAL_RIGHT,
    TOKEN_OR: PRECEDENCE_LOGICAL_RIGHT,
    TOKEN_NOT: PRECEDENCE_PREFIX,
    TOKEN_RPAREN: PRECEDENCE_LOWEST,
}

BINARY_OPERATORS = frozenset(
    [
        TOKEN_EQ,
        TOKEN_LT,
        TOKEN_GT,
        TOKEN_LG,
        TOKEN_NE,
        TOKEN_LE,
        TOKEN_GE,
        TOKEN_CONTAINS,
        # TOKEN_IN,
        TOKEN_AND,
        TOKEN_OR,
    ]
)


class BooleanExpression(Expression):
    """An expression that evaluates to true or false."""

    __slots__ = ("expression",)

    def __init__(self, token: Token, expression: Expression):
        super().__init__(token)
        self.expression = expression

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, BooleanExpression) and self.expression == other.expression
        )

    def __str__(self) -> str:
        def _str(expression: Expression, parent_precedence: int) -> str:
            if isinstance(expression, LogicalAndExpression):
                precedence = PRECEDENCE_LOGICAL_AND
                op = "and"
                left = _str(expression.left, precedence)
                right = _str(expression.right, precedence)
            elif isinstance(expression, LogicalOrExpression):
                precedence = PRECEDENCE_LOGICAL_OR
                op = "or"
                left = _str(expression.left, precedence)
                right = _str(expression.right, precedence)
            elif isinstance(expression, LogicalNotExpression):
                operand_str = _str(expression.right, PRECEDENCE_PREFIX)
                expr = f"not {operand_str}"
                if parent_precedence > PRECEDENCE_PREFIX:
                    return f"({expr})"
                return expr
            else:
                return str(expression)

            expr = f"{left} {op} {right}"
            if precedence < parent_precedence:
                return f"({expr})"
            return expr

        return _str(self.expression, 0)

    def evaluate(self, context: RenderContext) -> bool:
        return is_truthy(self.expression.evaluate(context))

    async def evaluate_async(self, context: RenderContext) -> bool:
        return is_truthy(await self.expression.evaluate_async(context))

    def children(self) -> list[Expression]:
        return [self.expression]

    @staticmethod
    def parse(
        env: Environment, tokens: TokenStream, *, inline: bool = False
    ) -> BooleanExpression:
        """Return a new BooleanExpression parsed from tokens in _tokens_.

        If _inline_ is `False`, we expect the stream to be empty after parsing
        a Boolean expression and will raise a syntax error if it's not.
        """
        expr = parse_boolean_primitive(env, tokens)
        if not inline:
            tokens.eat(TOKEN_EOF)
        return BooleanExpression(expr.token, expr)


class LogicalNotExpression(Expression):
    __slots__ = ("right",)

    def __init__(self, token: Token, right: Expression):
        super().__init__(token=token)
        self.right = right

    def __eq__(self, other: object) -> bool:
        return isinstance(other, LogicalNotExpression) and self.right == other.right

    def __str__(self) -> str:
        return f"not {self.right}"

    def evaluate(self, context: RenderContext) -> object:
        return not is_truthy(self.right.evaluate(context))

    async def evaluate_async(self, context: RenderContext) -> object:
        return not is_truthy(await self.right.evaluate_async(context))

    def children(self) -> list[Expression]:
        return [self.right]

    @staticmethod
    def parse(env: Environment, tokens: TokenStream) -> LogicalNotExpression:
        """Parse a not expression from _tokens_."""
        if not env.logical_not_operator:
            raise LiquidSyntaxError(
                "disallowed not operator in logical expression", token=tokens.current
            )

        tokens.eat(TOKEN_NOT)
        expr = parse_boolean_primitive(env, tokens)
        return LogicalNotExpression(expr.token, expr)


class LogicalAndExpression(Expression):
    __slots__ = ("left", "right")

    def __init__(self, token: Token, left: Expression, right: Expression) -> None:
        super().__init__(token=token)
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{self.left} and {self.right}"

    def evaluate(self, context: RenderContext) -> object:
        return is_truthy(self.left.evaluate(context)) and is_truthy(
            self.right.evaluate(context)
        )

    async def evaluate_async(self, context: RenderContext) -> object:
        return is_truthy(await self.left.evaluate_async(context)) and is_truthy(
            await self.right.evaluate_async(context)
        )

    def children(self) -> list[Expression]:
        return [self.left, self.right]


class LogicalOrExpression(Expression):
    __slots__ = ("left", "right")

    def __init__(self, token: Token, left: Expression, right: Expression) -> None:
        super().__init__(token=token)
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{self.left} or {self.right}"

    def evaluate(self, context: RenderContext) -> object:
        return is_truthy(self.left.evaluate(context)) or is_truthy(
            self.right.evaluate(context)
        )

    async def evaluate_async(self, context: RenderContext) -> object:
        return is_truthy(await self.left.evaluate_async(context)) or is_truthy(
            await self.right.evaluate_async(context)
        )

    def children(self) -> list[Expression]:
        return [self.left, self.right]


class EqExpression(Expression):
    __slots__ = ("left", "right")

    def __init__(self, token: Token, left: Expression, right: Expression) -> None:
        super().__init__(token=token)
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{self.left} == {self.right}"

    def evaluate(self, context: RenderContext) -> object:
        return _eq(self.left.evaluate(context), self.right.evaluate(context))

    async def evaluate_async(self, context: RenderContext) -> object:
        return _eq(
            await self.left.evaluate_async(context),
            await self.right.evaluate_async(context),
        )

    def children(self) -> list[Expression]:
        return [self.left, self.right]


class NeExpression(Expression):
    __slots__ = ("left", "right")

    def __init__(self, token: Token, left: Expression, right: Expression) -> None:
        super().__init__(token=token)
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{self.left} != {self.right}"

    def evaluate(self, context: RenderContext) -> object:
        return not _eq(self.left.evaluate(context), self.right.evaluate(context))

    async def evaluate_async(self, context: RenderContext) -> object:
        return not _eq(
            await self.left.evaluate_async(context),
            await self.right.evaluate_async(context),
        )

    def children(self) -> list[Expression]:
        return [self.left, self.right]


class LeExpression(Expression):
    __slots__ = ("left", "right")

    def __init__(self, token: Token, left: Expression, right: Expression) -> None:
        super().__init__(token=token)
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{self.left} <= {self.right}"

    def evaluate(self, context: RenderContext) -> object:
        left = self.left.evaluate(context)
        right = self.right.evaluate(context)
        return _eq(left, right) or _lt(self.token, left, right)

    async def evaluate_async(self, context: RenderContext) -> object:
        left = await self.left.evaluate_async(context)
        right = await self.right.evaluate_async(context)
        return _eq(left, right) or _lt(self.token, left, right)

    def children(self) -> list[Expression]:
        return [self.left, self.right]


class GeExpression(Expression):
    __slots__ = ("left", "right")

    def __init__(self, token: Token, left: Expression, right: Expression) -> None:
        super().__init__(token=token)
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{self.left} >= {self.right}"

    def evaluate(self, context: RenderContext) -> object:
        left = self.left.evaluate(context)
        right = self.right.evaluate(context)
        return _eq(left, right) or _lt(self.token, right, left)

    async def evaluate_async(self, context: RenderContext) -> object:
        left = await self.left.evaluate_async(context)
        right = await self.right.evaluate_async(context)
        return _eq(left, right) or _lt(self.token, right, left)

    def children(self) -> list[Expression]:
        return [self.left, self.right]


class LtExpression(Expression):
    __slots__ = ("left", "right")

    def __init__(self, token: Token, left: Expression, right: Expression) -> None:
        super().__init__(token=token)
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{self.left} < {self.right}"

    def evaluate(self, context: RenderContext) -> object:
        return _lt(
            self.token, self.left.evaluate(context), self.right.evaluate(context)
        )

    async def evaluate_async(self, context: RenderContext) -> object:
        return _lt(
            self.token,
            await self.left.evaluate_async(context),
            await self.right.evaluate_async(context),
        )

    def children(self) -> list[Expression]:
        return [self.left, self.right]


class GtExpression(Expression):
    __slots__ = ("left", "right")

    def __init__(self, token: Token, left: Expression, right: Expression) -> None:
        super().__init__(token=token)
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{self.left} > {self.right}"

    def evaluate(self, context: RenderContext) -> object:
        return _lt(
            self.token, self.right.evaluate(context), self.left.evaluate(context)
        )

    async def evaluate_async(self, context: RenderContext) -> object:
        return _lt(
            self.token,
            await self.right.evaluate_async(context),
            await self.left.evaluate_async(context),
        )

    def children(self) -> list[Expression]:
        return [self.left, self.right]


class ContainsExpression(Expression):
    __slots__ = ("left", "right")

    def __init__(self, token: Token, left: Expression, right: Expression) -> None:
        super().__init__(token=token)
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{self.left} contains {self.right}"

    def evaluate(self, context: RenderContext) -> object:
        return _contains(
            self.token, self.left.evaluate(context), self.right.evaluate(context)
        )

    async def evaluate_async(self, context: RenderContext) -> object:
        return _contains(
            self.token,
            await self.left.evaluate_async(context),
            await self.right.evaluate_async(context),
        )

    def children(self) -> list[Expression]:
        return [self.left, self.right]


def parse_boolean_primitive(  # noqa: PLR0912
    env: Environment, tokens: TokenStream, precedence: int = PRECEDENCE_LOWEST
) -> Expression:
    """Parse a Boolean expression from tokens in _stream_."""
    left: Expression
    token = tokens.current
    kind = token.kind

    if kind == TOKEN_TRUE:
        left = TrueLiteral(token)
        next(tokens)
    elif kind == TOKEN_FALSE:
        left = FalseLiteral(token)
        next(tokens)
    elif kind in (TOKEN_NIL, TOKEN_NULL):
        left = Nil(token)
        next(tokens)
    elif kind == TOKEN_INTEGER:
        left = IntegerLiteral(token, to_int(token.value))
        next(tokens)
    elif kind == TOKEN_FLOAT:
        left = FloatLiteral(token, float(token.value))
        next(tokens)
    elif kind == TOKEN_STRING:
        left = StringLiteral(token, token.value)
        next(tokens)
    elif kind == TOKEN_RANGE_LITERAL:
        left = RangeLiteral.parse(env, tokens)
    elif kind == TOKEN_BLANK:
        left = Blank(token)
        next(tokens)
    elif kind == TOKEN_EMPTY:
        left = Empty(token)
        next(tokens)
    elif kind in (TOKEN_WORD, TOKEN_IDENTSTRING, TOKEN_LBRACKET):
        left = Path.parse(env, tokens)
    elif kind == TOKEN_LPAREN:
        left = parse_grouped_expression(env, tokens)
    elif kind == TOKEN_NOT:
        left = LogicalNotExpression.parse(env, tokens)
    else:
        raise LiquidSyntaxError(
            f"expected a primitive expression, found {token.kind}",
            token=tokens.current,
        )

    while True:
        token = tokens.current
        if (
            token == tokens.eof
            or PRECEDENCES.get(token.kind, PRECEDENCE_LOWEST) < precedence
        ):
            break

        if token.kind not in BINARY_OPERATORS:
            return left

        left = parse_infix_expression(env, tokens, left)

    return left


def parse_infix_expression(  # noqa: PLR0911
    env: Environment, stream: TokenStream, left: Expression
) -> Expression:  # noqa: PLR0911
    """Return a logical, comparison, or membership expression parsed from _stream_."""
    token = next(stream)
    assert token is not None
    precedence = PRECEDENCES.get(token.kind, PRECEDENCE_LOWEST)

    if token.kind == TOKEN_EQ:
        return EqExpression(
            token, left, parse_boolean_primitive(env, stream, precedence)
        )
    if token.kind == TOKEN_LT:
        return LtExpression(
            token, left, parse_boolean_primitive(env, stream, precedence)
        )
    if token.kind == TOKEN_GT:
        return GtExpression(
            token, left, parse_boolean_primitive(env, stream, precedence)
        )
    if token.kind in (TOKEN_NE, TOKEN_LG):
        return NeExpression(
            token, left, parse_boolean_primitive(env, stream, precedence)
        )
    if token.kind == TOKEN_LE:
        return LeExpression(
            token, left, parse_boolean_primitive(env, stream, precedence)
        )
    if token.kind == TOKEN_GE:
        return GeExpression(
            token, left, parse_boolean_primitive(env, stream, precedence)
        )
    if token.kind == TOKEN_CONTAINS:
        return ContainsExpression(
            token, left, parse_boolean_primitive(env, stream, precedence)
        )
    # if token.kind == TOKEN_IN:
    #     return InExpression(
    #         token, left, parse_boolean_primitive(env, stream, precedence)
    #     )
    if token.kind == TOKEN_AND:
        return LogicalAndExpression(
            token, left, parse_boolean_primitive(env, stream, precedence)
        )
    if token.kind == TOKEN_OR:
        return LogicalOrExpression(
            token, left, parse_boolean_primitive(env, stream, precedence)
        )

    raise LiquidSyntaxError(
        f"expected an infix expression, found {token.kind}",
        token=token,
    )


def parse_grouped_expression(env: Environment, tokens: TokenStream) -> Expression:
    """Parse an expression from tokens in _tokens_ until the next right parenthesis."""
    if not env.logical_parentheses:
        raise LiquidSyntaxError(
            "disallowed parentheses in logical expression", token=tokens.current
        )

    tokens.eat(TOKEN_LPAREN)
    expr = parse_boolean_primitive(env, tokens)
    token = next(tokens)

    while token.kind != TOKEN_RPAREN:
        if token is None:
            raise LiquidSyntaxError("unbalanced parentheses", token=token)

        if token.kind not in BINARY_OPERATORS:
            raise LiquidSyntaxError(
                f"expected an infix expression, found {tokens.current.kind}",
                token=token,
            )

        expr = parse_infix_expression(env, tokens, expr)

    if token.kind != TOKEN_RPAREN:
        raise LiquidSyntaxError("unbalanced parentheses", token=token)

    return expr


def is_truthy(obj: object) -> bool:
    """Return _True_ if _obj_ is considered Liquid truthy."""
    if hasattr(obj, "__liquid__"):
        obj = obj.__liquid__()
    if is_undefined(obj):
        return False
    return not (obj is False or obj is None)


def _eq(left: object, right: object) -> bool:
    if hasattr(left, "__liquid__"):
        left = left.__liquid__()

    if hasattr(right, "__liquid__"):
        right = right.__liquid__()

    if isinstance(right, (Empty, Blank)):
        left, right = right, left

    # Remember 1 == True and 0 == False in Python
    if isinstance(right, bool):
        left, right = right, left

    if isinstance(left, bool):
        return isinstance(right, bool) and left == right

    return left == right


def _lt(token: Token, left: object, right: object) -> bool:
    if hasattr(left, "__liquid__"):
        left = left.__liquid__()

    if hasattr(right, "__liquid__"):
        right = right.__liquid__()

    if isinstance(left, str) and isinstance(right, str):
        return left < right

    if isinstance(left, bool) or isinstance(right, bool):
        return False

    if isinstance(left, (int, float, Decimal)) and isinstance(
        right, (int, float, Decimal)
    ):
        return left < right

    raise LiquidTypeError(
        f"'<' and '>' are not supported between '{left.__class__.__name__}' "
        f"and '{right.__class__.__name__}'",
        token=token,
    )


def _contains(token: Token, left: object, right: object) -> bool:
    if not is_truthy(left) or not is_truthy(right):
        return False
    if isinstance(left, str):
        return str(right) in left
    if isinstance(left, Collection):
        return right in left

    raise LiquidTypeError(
        f"'in' and 'contains' are not supported between '{left.__class__.__name__}' "
        f"and '{right.__class__.__name__}'",
        token=token,
    )
