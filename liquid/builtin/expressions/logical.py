"""Built-in logical expressions."""

from decimal import Decimal
from typing import Collection

from liquid import RenderContext
from liquid.exceptions import LiquidTypeError
from liquid.expression import Expression
from liquid.token import Token

from .primitive import Blank
from .primitive import Empty


class BooleanExpression(Expression):
    """An expression that evaluates to true or false."""

    __slots__ = ("expression",)

    def __init__(self, expression: Expression):
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


# TODO: parse_boolean_primitive(env: Environment, stream: TokenStream, precedence: int=PRECEDENCE_LOWEST)


def is_truthy(obj: object) -> bool:
    """Return _True_ if _obj_ is considered Liquid truthy."""
    if hasattr(obj, "__liquid__"):
        obj = obj.__liquid__()
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
    if isinstance(left, str):
        return str(right) in left
    if isinstance(left, Collection):
        return right in left

    raise LiquidTypeError(
        f"'in' and 'contains' are not supported between '{left.__class__.__name__}' "
        f"and '{right.__class__.__name__}'",
        token=token,
    )
