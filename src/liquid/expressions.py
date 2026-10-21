from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

import markupsafe

from ._filter import FilterContext
from ._nothing import NOTHING
from .drops import BLANK, EMPTY, Range
from .exceptions import (
    LiquidFilterInterrupt,
    LiquidNameError,
    LiquidTypeError,
    LiquidZeroDivisionError,
)
from .tokens import span

if TYPE_CHECKING:
    from ._context import RenderContext
    from ._markup import Expression
    from .tokens import Token


@dataclass(slots=True)
class Filtered:
    token: Token
    left: Expression
    name: Name
    args: list[Expression | KeywordArgument]
    span: Token = field(init=False)

    def __post_init__(self) -> None:
        self.span = (
            span(self.left.token, self.name.token)
            if not self.args
            else span(self.left.token, self.args[-1].span)
        )

    def evaluate(self, context: RenderContext) -> object:
        func = context.env.filters.get(self.name.value)

        # Like Shopify/liquid, filter strictness is applied at render time,
        # and only on rendered markup. Unknown filters in unreached markup will
        # not throw an error.
        if func is None:
            if context.env.strict_filters:
                raise LiquidNameError(
                    f"unknown filter {self.name.value!r}",
                    token=self.name.token,
                    source=context.template.source,
                    name=context.template.name,
                )

            # Pass the input value through.
            return self.left.evaluate(context)

        left = self.left.evaluate(context)

        if not self.args:
            try:
                return func(FilterContext(context, self.span), left)
            except LiquidFilterInterrupt:
                return None
            except (TypeError, ValueError) as err:
                raise LiquidTypeError(
                    str(err),
                    token=self.span,
                    source=context.template.source,
                    name=context.template.name,
                ) from err

        args: list[object] = []
        kwargs: dict[str, object] = {}

        for arg in self.args:
            if isinstance(arg, KeywordArgument):
                kwargs[arg.name.value] = arg.expr.evaluate(context)
            else:
                args.append(arg.evaluate(context))

        try:
            return func(FilterContext(context, self.span), left, *args, **kwargs)
        except LiquidFilterInterrupt:
            return None
        except (TypeError, ValueError) as err:
            raise LiquidTypeError(
                str(err),
                token=self.span,
                source=context.template.source,
                name=context.template.name,
            ) from err

    async def evaluate_async(self, context: RenderContext) -> object:
        func = context.env.filters.get(self.name.value)

        # Like Shopify/liquid, filter strictness is applied at render time,
        # and only on rendered markup. Unknown filters in unreached markup will
        # not throw an error.
        if func is None:
            if context.env.strict_filters:
                raise LiquidNameError(
                    f"unknown filter {self.name.value!r}",
                    token=self.name.token,
                    source=context.template.source,
                    name=context.template.name,
                )

            # Pass the input value through.
            return await self.left.evaluate_async(context)

        left = await self.left.evaluate_async(context)

        if not self.args:
            try:
                return func(FilterContext(context, self.span), left)
            except LiquidFilterInterrupt:
                return None
            except (TypeError, ValueError) as err:
                raise LiquidTypeError(
                    str(err),
                    token=self.span,
                    source=context.template.source,
                    name=context.template.name,
                ) from err

        args: list[object] = []
        kwargs: dict[str, object] = {}

        for arg in self.args:
            if isinstance(arg, KeywordArgument):
                kwargs[arg.name.value] = await arg.expr.evaluate_async(context)
            else:
                args.append(await arg.evaluate_async(context))

        try:
            return func(FilterContext(context, self.span), left, *args, **kwargs)
        except LiquidFilterInterrupt:
            return None
        except (TypeError, ValueError) as err:
            raise LiquidTypeError(
                str(err),
                token=self.span,
                source=context.template.source,
                name=context.template.name,
            ) from err

    def children(self) -> list[Expression]:
        return [
            self.left,
            *(a.expr if isinstance(a, KeywordArgument) else a for a in self.args),
        ]

    def __str__(self) -> str:
        if self.args:
            args = ": " + ", ".join(
                f"{a.name.value}: {a.expr}"
                if isinstance(a, KeywordArgument)
                else str(a)
                for a in self.args
            )
        else:
            args = ""

        return f"{self.left} | {self.name.value}{args}"


@dataclass(slots=True)
class Group:
    token: Token
    expr: Expression
    segments: list[PathSegment] | None
    end_token: InitVar[Token]
    span: Token = field(init=False)

    def __post_init__(self, end_token: Token) -> None:
        if self.segments:
            self.span = span(self.token, self.segments[-1].span)
        else:
            self.span = span(self.token, end_token)

    def evaluate(self, context: RenderContext) -> object:
        obj = self.expr.evaluate(context)

        if not self.segments:
            return obj

        obj, index = context.resolve_path(
            obj,
            [s if isinstance(s, Name) else s.evaluate(context) for s in self.segments],
        )

        if obj is NOTHING:
            return context.env.undefined(
                self._path(self.segments[: index + 1]),
                self.span,
                context.template.source,
                context.template.name,
            )

        return obj

    async def evaluate_async(self, context: RenderContext) -> object:
        obj = await self.expr.evaluate_async(context)

        if not self.segments:
            return obj

        obj, index = context.resolve_path(
            obj,
            [
                s if isinstance(s, Name) else await s.evaluate_async(context)
                for s in self.segments
            ],
        )

        if obj is NOTHING:
            return context.env.undefined(
                self._path(self.segments[: index + 1]),
                self.span,
                context.template.source,
                context.template.name,
            )

        return obj

    def __str__(self) -> str:
        return f"({self.expr}){self._path(self.segments)}"

    def children(self) -> list[Expression]:
        if not self.segments:
            return [self.expr]
        return [
            self.expr,
            *(s.var for s in self.segments if isinstance(s, VariableSegment)),
        ]

    def _path(self, segments: list[PathSegment] | None) -> str:
        if not segments:
            return ""

        return "".join(f".{s}" if isinstance(s, Name) else str(s) for s in segments)


@dataclass(slots=True)
class Ternary:
    token: Token
    consequence: Expression
    condition: Expression
    alternative: Expression | None
    span: Token = field(init=False)

    def __post_init__(self) -> None:
        self.span = span(self.token, (self.alternative or self.condition).span)

    def evaluate(self, context: RenderContext) -> object:
        if context.env.truthy(self.condition.evaluate(context), context):
            return self.consequence.evaluate(context)

        if self.alternative:
            return self.alternative.evaluate(context)

        return NOTHING

    async def evaluate_async(self, context: RenderContext) -> object:
        if context.env.truthy(await self.condition.evaluate_async(context), context):
            return await self.consequence.evaluate_async(context)

        if self.alternative:
            return await self.alternative.evaluate_async(context)

        return NOTHING

    def __str__(self) -> str:
        if self.alternative:
            return f"{self.consequence} if {self.condition} else {self.alternative}"
        return f"{self.consequence} if {self.condition}"

    def children(self) -> list[Expression]:
        result: list[Expression] = [self.consequence, self.condition]
        if self.alternative:
            result.append(self.alternative)
        return result


@dataclass(slots=True)
class PrefixExpression:
    token: Token
    right: Expression
    span: Token = field(init=False)

    def __post_init__(self) -> None:
        self.span = span(self.token, self.right.span)

    def children(self) -> list[Expression]:
        return [self.right]


@dataclass(slots=True)
class LogicalNot(PrefixExpression):
    def evaluate(self, context: RenderContext) -> object:
        return not context.env.truthy(self.right.evaluate(context), context)

    async def evaluate_async(self, context: RenderContext) -> object:
        return not context.env.truthy(await self.right.evaluate_async(context), context)

    def __str__(self) -> str:
        return f"not {self.right}"


@dataclass(slots=True)
class Pos(PrefixExpression):
    def evaluate(self, context: RenderContext) -> object:
        return context.env.to_numeric(self.right.evaluate(context), context, 0)

    async def evaluate_async(self, context: RenderContext) -> object:
        return context.env.to_numeric(
            await self.right.evaluate_async(context), context, 0
        )

    def __str__(self) -> str:
        return f"+{self.right}"


@dataclass(slots=True)
class Neg(PrefixExpression):
    def evaluate(self, context: RenderContext) -> object:
        return -context.env.to_numeric(self.right.evaluate(context), context, 0)

    async def evaluate_async(self, context: RenderContext) -> object:
        return -context.env.to_numeric(
            await self.right.evaluate_async(context), context, 0
        )

    def __str__(self) -> str:
        return f"-{self.right}"


@dataclass(slots=True)
class InfixExpression:
    token: Token
    left: Expression
    right: Expression
    span: Token = field(init=False)

    def __post_init__(self) -> None:
        self.span = span(self.left.span, self.right.span)

    def children(self) -> list[Expression]:
        return [self.left, self.right]


@dataclass(slots=True)
class LogicalOr(InfixExpression):
    def evaluate(self, context: RenderContext) -> object:
        left = self.left.evaluate(context)
        return (
            left if context.env.truthy(left, context) else self.right.evaluate(context)
        )

    async def evaluate_async(self, context: RenderContext) -> object:
        left = await self.left.evaluate_async(context)
        return (
            left
            if context.env.truthy(left, context)
            else await self.right.evaluate_async(context)
        )

    def __str__(self) -> str:
        return f"{self.left} or {self.right}"


@dataclass(slots=True)
class LogicalAnd(InfixExpression):
    def evaluate(self, context: RenderContext) -> object:
        left = self.left.evaluate(context)
        return (
            self.right.evaluate(context) if context.env.truthy(left, context) else left
        )

    async def evaluate_async(self, context: RenderContext) -> object:
        left = await self.left.evaluate_async(context)
        return (
            await self.right.evaluate_async(context)
            if context.env.truthy(left, context)
            else left
        )

    def __str__(self) -> str:
        return f"{self.left} and {self.right}"


@dataclass(slots=True)
class Eq(InfixExpression):
    def evaluate(self, context: RenderContext) -> object:
        return context.env.eq(
            self.left.evaluate(context),
            self.right.evaluate(context),
            context,
            self.span,
        )

    async def evaluate_async(self, context: RenderContext) -> object:
        return context.env.eq(
            await self.left.evaluate_async(context),
            await self.right.evaluate_async(context),
            context,
            self.span,
        )

    def __str__(self) -> str:
        return f"{self.left} == {self.right}"


@dataclass(slots=True)
class Ne(InfixExpression):
    def evaluate(self, context: RenderContext) -> object:
        return not context.env.eq(
            self.left.evaluate(context),
            self.right.evaluate(context),
            context,
            self.span,
        )

    async def evaluate_async(self, context: RenderContext) -> object:
        return not context.env.eq(
            await self.left.evaluate_async(context),
            await self.right.evaluate_async(context),
            context,
            self.span,
        )

    def __str__(self) -> str:
        return f"{self.left} != {self.right}"


@dataclass(slots=True)
class Lt(InfixExpression):
    def evaluate(self, context: RenderContext) -> object:
        return context.env.lt(
            self.left.evaluate(context),
            self.right.evaluate(context),
            context,
            self.span,
        )

    async def evaluate_async(self, context: RenderContext) -> object:
        return context.env.lt(
            await self.left.evaluate_async(context),
            await self.right.evaluate_async(context),
            context,
            self.span,
        )

    def __str__(self) -> str:
        return f"{self.left} < {self.right}"


@dataclass(slots=True)
class Le(InfixExpression):
    def evaluate(self, context: RenderContext) -> object:
        return context.env.le(
            self.left.evaluate(context),
            self.right.evaluate(context),
            context,
            self.span,
        )

    async def evaluate_async(self, context: RenderContext) -> object:
        return context.env.le(
            await self.left.evaluate_async(context),
            await self.right.evaluate_async(context),
            context,
            self.span,
        )

    def __str__(self) -> str:
        return f"{self.left} <= {self.right}"


@dataclass(slots=True)
class Gt(InfixExpression):
    def evaluate(self, context: RenderContext) -> object:
        return context.env.lt(
            self.right.evaluate(context),
            self.left.evaluate(context),
            context,
            self.span,
        )

    async def evaluate_async(self, context: RenderContext) -> object:
        return context.env.lt(
            await self.right.evaluate_async(context),
            await self.left.evaluate_async(context),
            context,
            self.span,
        )

    def __str__(self) -> str:
        return f"{self.left} > {self.right}"


@dataclass(slots=True)
class Ge(InfixExpression):
    def evaluate(self, context: RenderContext) -> object:
        return context.env.le(
            self.right.evaluate(context),
            self.left.evaluate(context),
            context,
            self.span,
        )

    async def evaluate_async(self, context: RenderContext) -> object:
        return context.env.le(
            await self.right.evaluate_async(context),
            await self.left.evaluate_async(context),
            context,
            self.span,
        )

    def __str__(self) -> str:
        return f"{self.left} >= {self.right}"


@dataclass(slots=True)
class Contains(InfixExpression):
    def evaluate(self, context: RenderContext) -> object:
        return context.env.contains(
            self.left.evaluate(context),
            self.right.evaluate(context),
            context,
            self.span,
        )

    async def evaluate_async(self, context: RenderContext) -> object:
        return context.env.contains(
            await self.left.evaluate_async(context),
            await self.right.evaluate_async(context),
            context,
            self.span,
        )

    def __str__(self) -> str:
        return f"{self.left} contains {self.right}"


@dataclass(slots=True)
class Add(InfixExpression):
    def evaluate(self, context: RenderContext) -> object:
        left = context.env.to_numeric(self.left.evaluate(context), context, 0)
        right = context.env.to_numeric(self.right.evaluate(context), context, 0)

        if isinstance(left, int) and isinstance(right, int):
            return left + right

        return float(Decimal(str(left)) + Decimal(str(right)))

    async def evaluate_async(self, context: RenderContext) -> object:
        left = context.env.to_numeric(
            await self.left.evaluate_async(context), context, 0
        )
        right = context.env.to_numeric(
            await self.right.evaluate_async(context), context, 0
        )

        if isinstance(left, int) and isinstance(right, int):
            return left + right

        return float(Decimal(str(left)) + Decimal(str(right)))

    def __str__(self) -> str:
        return f"{self.left} + {self.right}"


@dataclass(slots=True)
class Sub(InfixExpression):
    def evaluate(self, context: RenderContext) -> object:
        left = context.env.to_numeric(self.left.evaluate(context), context, 0)
        right = context.env.to_numeric(self.right.evaluate(context), context, 0)

        if isinstance(left, int) and isinstance(right, int):
            return left - right

        return float(Decimal(str(left)) - Decimal(str(right)))

    async def evaluate_async(self, context: RenderContext) -> object:
        left = context.env.to_numeric(
            await self.left.evaluate_async(context), context, 0
        )
        right = context.env.to_numeric(
            await self.right.evaluate_async(context), context, 0
        )

        if isinstance(left, int) and isinstance(right, int):
            return left - right

        return float(Decimal(str(left)) - Decimal(str(right)))

    def __str__(self) -> str:
        return f"{self.left} - {self.right}"


@dataclass(slots=True)
class Mul(InfixExpression):
    def evaluate(self, context: RenderContext) -> object:
        left = context.env.to_numeric(self.left.evaluate(context), context, 0)
        right = context.env.to_numeric(self.right.evaluate(context), context, 0)

        if isinstance(left, int) and isinstance(right, int):
            return left * right

        return float(Decimal(str(left)) * Decimal(str(right)))

    async def evaluate_async(self, context: RenderContext) -> object:
        left = context.env.to_numeric(
            await self.left.evaluate_async(context), context, 0
        )
        right = context.env.to_numeric(
            await self.right.evaluate_async(context), context, 0
        )

        if isinstance(left, int) and isinstance(right, int):
            return left * right

        return float(Decimal(str(left)) * Decimal(str(right)))

    def __str__(self) -> str:
        return f"{self.left} * {self.right}"


@dataclass(slots=True)
class Div(InfixExpression):
    def evaluate(self, context: RenderContext) -> object:
        left = context.env.to_numeric(self.left.evaluate(context), context, 0)
        right = context.env.to_numeric(self.right.evaluate(context), context, 0)

        if right == 0:
            raise LiquidZeroDivisionError(
                "divide by zero",
                token=self.right.span,
                source=context.template.source,
                name=context.template.name,
            )

        if isinstance(left, int) and isinstance(right, int):
            return left // right

        if isinstance(left, Decimal) or isinstance(right, Decimal):
            return float(Decimal(str(left)) / Decimal(str(right)))

        return left / right

    async def evaluate_async(self, context: RenderContext) -> object:
        left = context.env.to_numeric(
            await self.left.evaluate_async(context), context, 0
        )
        right = context.env.to_numeric(
            await self.right.evaluate_async(context), context, 0
        )

        if right == 0:
            raise LiquidZeroDivisionError(
                "divide by zero",
                token=self.right.span,
                source=context.template.source,
                name=context.template.name,
            )

        if isinstance(left, int) and isinstance(right, int):
            return left // right

        if isinstance(left, Decimal) or isinstance(right, Decimal):
            return float(Decimal(str(left)) / Decimal(str(right)))

        return left / right

    def __str__(self) -> str:
        return f"{self.left} / {self.right}"


@dataclass(slots=True)
class Mod(InfixExpression):
    def evaluate(self, context: RenderContext) -> object:
        left = context.env.to_numeric(self.left.evaluate(context), context, 0)
        right = context.env.to_numeric(self.right.evaluate(context), context, 0)

        if right == 0:
            raise LiquidZeroDivisionError(
                "divide by zero",
                token=self.right.span,
                source=context.template.source,
                name=context.template.name,
            )

        if isinstance(left, int) and isinstance(right, int):
            return left % right

        return float(Decimal(str(left)) % Decimal(str(right)))

    async def evaluate_async(self, context: RenderContext) -> object:
        left = context.env.to_numeric(
            await self.left.evaluate_async(context), context, 0
        )
        right = context.env.to_numeric(
            await self.right.evaluate_async(context), context, 0
        )

        if right == 0:
            raise LiquidZeroDivisionError(
                "divide by zero",
                token=self.right.span,
                source=context.template.source,
                name=context.template.name,
            )

        if isinstance(left, int) and isinstance(right, int):
            return left % right

        return float(Decimal(str(left)) % Decimal(str(right)))

    def __str__(self) -> str:
        return f"{self.left} / {self.right}"


@dataclass(slots=True)
class Variable:
    token: Token
    root: Name | NameSegment | VariableSegment
    selectors: list[PathSegment] | None
    span: Token = field(init=False)

    def __post_init__(self) -> None:
        self.span = (
            self.root.span
            if not self.selectors
            else span(self.root.span, self.selectors[-1].span)
        )

    def evaluate(self, context: RenderContext) -> object:
        selector = (
            self.root.evaluate(context)
            if isinstance(self.root, VariableSegment)
            else self.root.value
        )

        index = 0
        obj = context.resolve(selector)

        if self.selectors:
            obj, index = context.resolve_path(
                obj,
                [
                    s if isinstance(s, (Name, IntegerLiteral)) else s.evaluate(context)
                    for s in self.selectors
                ],
            )

        if obj is NOTHING:
            return context.env.undefined(
                self.path(self.selectors[: index + 1] if self.selectors else None),
                self.span,
                context.template.source,
                context.template.name,
            )

        return obj

    async def evaluate_async(self, context: RenderContext) -> object:
        selector = (
            await self.root.evaluate_async(context)
            if isinstance(self.root, VariableSegment)
            else self.root.value
        )

        index = 0
        obj = context.resolve(selector)

        if self.selectors:
            obj, index = await context.resolve_path_async(
                obj,
                [
                    s
                    if isinstance(s, (Name, IntegerLiteral))
                    else await s.evaluate_async(context)
                    for s in self.selectors
                ],
            )

        if obj is NOTHING:
            return context.env.undefined(
                self.path(self.selectors[: index + 1] if self.selectors else None),
                self.span,
                context.template.source,
                context.template.name,
            )

        return obj

    def children(self) -> list[Expression]:
        exprs: list[Expression] = []

        if isinstance(self.root, VariableSegment):
            exprs.append(self.root.var)

        if self.selectors:
            exprs.extend(
                s.var for s in self.selectors if isinstance(s, VariableSegment)
            )

        return exprs

    def path(self, selectors: list[PathSegment] | None) -> str:
        root = str(self.root)

        if selectors:
            _selectors = "".join(
                f".{s}" if isinstance(s, (Name, IntegerLiteral)) else str(s)
                for s in selectors
            )
            return f"{root}{_selectors}"

        return root

    def location(self) -> Location:
        def serialize(s: PathSegment) -> int | str | Location:
            if isinstance(s, (Name, NameSegment, IndexSegment, IntegerLiteral)):
                return s.value
            if isinstance(s, VariableSegment):
                return s.var.location()
            return str(s)

        segments: Location = [serialize(self.root)]
        if self.selectors:
            segments.extend(serialize(s) for s in self.selectors)

        return segments

    def __str__(self) -> str:
        return self.path(self.selectors)


@dataclass(slots=True)
class IndexSegment:
    token: Token
    value: int
    span: Token

    def evaluate(self, context: RenderContext) -> object:
        return self.value

    async def evaluate_async(self, context: RenderContext) -> object:
        return self.value

    def children(self) -> list[Expression]:
        return []

    def __str__(self) -> str:
        return f"[{self.value}]"


@dataclass(slots=True)
class NameSegment:
    token: Token
    value: str
    span: Token

    def evaluate(self, context: RenderContext) -> object:
        return self.value

    async def evaluate_async(self, context: RenderContext) -> object:
        return self.value

    def children(self) -> list[Expression]:
        return []

    def __str__(self) -> str:
        return f"[{self.value!r}]"


@dataclass(slots=True)
class VariableSegment:
    token: Token
    var: Variable
    span: Token

    def evaluate(self, context: RenderContext) -> object:
        return self.var.evaluate(context)

    async def evaluate_async(self, context: RenderContext) -> object:
        return await self.var.evaluate_async(context)

    def children(self) -> list[Expression]:
        return [self.var]

    def __str__(self) -> str:
        return f"[{self.var}]"


@dataclass(slots=True)
class StringLiteral:
    token: Token
    value: str
    span: Token

    def evaluate(self, context: RenderContext) -> object:
        return markupsafe.Markup(self.value) if context.env.autoescape else self.value

    async def evaluate_async(self, context: RenderContext) -> object:
        return markupsafe.Markup(self.value) if context.env.autoescape else self.value

    def children(self) -> list[Expression]:
        return []

    def __str__(self) -> str:
        return repr(self.value)


@dataclass(slots=True)
class IntegerLiteral:
    token: Token
    value: int
    span: Token = field(init=False)

    def __post_init__(self) -> None:
        self.span = self.token

    def evaluate(self, context: RenderContext) -> object:
        return self.value

    async def evaluate_async(self, context: RenderContext) -> object:
        return self.value

    def children(self) -> list[Expression]:
        return []

    def __str__(self) -> str:
        return str(self.value)


@dataclass(slots=True)
class FloatLiteral:
    token: Token
    value: float
    span: Token = field(init=False)

    def __post_init__(self) -> None:
        self.span = self.token

    def evaluate(self, context: RenderContext) -> object:
        return self.value

    async def evaluate_async(self, context: RenderContext) -> object:
        return self.value

    def children(self) -> list[Expression]:
        return []

    def __str__(self) -> str:
        return str(self.value)


@dataclass(slots=True)
class BooleanLiteral:
    token: Token
    value: bool
    span: Token = field(init=False)

    def __post_init__(self) -> None:
        self.span = self.token

    def evaluate(self, context: RenderContext) -> object:
        return self.value

    async def evaluate_async(self, context: RenderContext) -> object:
        return self.value

    def children(self) -> list[Expression]:
        return []

    def __str__(self) -> str:
        return str(self.value).lower()


@dataclass(slots=True)
class NullLiteral:
    token: Token
    span: Token = field(init=False)

    def __post_init__(self) -> None:
        self.span = self.token

    def evaluate(self, context: RenderContext) -> object:
        return None

    async def evaluate_async(self, context: RenderContext) -> object:
        return None

    def children(self) -> list[Expression]:
        return []

    def __str__(self) -> str:
        return "null"


@dataclass(slots=True)
class Blank:
    token: Token
    span: Token = field(init=False)

    def __post_init__(self) -> None:
        self.span = self.token

    def evaluate(self, context: RenderContext) -> object:
        return BLANK

    async def evaluate_async(self, context: RenderContext) -> object:
        return BLANK

    def children(self) -> list[Expression]:
        return []

    def __str__(self) -> str:
        return ""


@dataclass(slots=True)
class Empty:
    token: Token
    span: Token = field(init=False)

    def __post_init__(self) -> None:
        self.span = self.token

    def evaluate(self, context: RenderContext) -> object:
        return EMPTY

    async def evaluate_async(self, context: RenderContext) -> object:
        return EMPTY

    def children(self) -> list[Expression]:
        return []

    def __str__(self) -> str:
        return ""


@dataclass(slots=True)
class RangeLiteral:
    token: Token
    start: Expression
    stop: Expression
    span: Token = field(init=False)
    value: str = field(init=False)

    def __post_init__(self) -> None:
        self.span = span(self.start.span, self.stop.span)
        self.value = ""

    def evaluate(self, context: RenderContext) -> object:
        start = context.env.to_numeric(self.start.evaluate(context), context)
        stop = context.env.to_numeric(self.stop.evaluate(context), context)
        return Range(int(start), int(stop))

    async def evaluate_async(self, context: RenderContext) -> object:
        start = context.env.to_numeric(
            await self.start.evaluate_async(context), context
        )
        stop = context.env.to_numeric(await self.stop.evaluate_async(context), context)
        return Range(int(start), int(stop))

    def children(self) -> list[Expression]:
        return [self.start, self.stop]

    def __str__(self) -> str:
        return f"({self.start}..{self.stop})"


@dataclass(slots=True)
class Name:
    token: Token
    value: str
    span: Token = field(init=False)

    def __post_init__(self) -> None:
        self.span = self.token

    def __str__(self) -> str:
        return self.value


@dataclass(slots=True)
class KeywordArgument:
    token: Token
    name: Name
    expr: Expression
    span: Token = field(init=False)

    def __post_init__(self) -> None:
        self.span = span(self.token, self.expr.token)


type PathSegment = (
    Name | NameSegment | IndexSegment | IntegerLiteral | VariableSegment | RangeLiteral
)

type Location = list[int | str | Location]


def tree_view(expr: Expression) -> str:
    """Return an ASCII tree representation of `expr`."""
    # (prefix, connector, class_name, inspect_value)
    nodes: list[tuple[str, str, str, str]] = []

    def visit(node: Expression, prefix: str, *, is_last: bool) -> None:
        if not prefix:
            connector = ""
        elif is_last:
            connector = "└── "
        else:
            connector = "├── "

        nodes.append((prefix, connector, node.__class__.__name__, str(node)))

        child_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(node.children()):
            last = i == len(node.children()) - 1
            visit(child, child_prefix, is_last=last)

    visit(expr, "", is_last=True)

    widths = [len(prefix + connector + name) for prefix, connector, name, _ in nodes]
    max_width = max(widths) if widths else 0

    lines: list[str] = []

    for node, width in zip(nodes, widths, strict=True):
        prefix, connector, name, value = node
        left = prefix + connector + name
        padding = " " * (max_width - width + 4)
        lines.append(left + padding + value)

    return "\n".join(lines)
