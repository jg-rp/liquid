from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ._filter import FilterContext
from ._nothing import NOTHING
from .drops import BLANK, EMPTY, Range
from .exceptions import LiquidNameError
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
            else span(self.left.token, self.args[-1].token)
        )

    def evaluate(self, context: RenderContext) -> object:
        func = context.env.filters.get(self.name.value)

        # Like Shopify/liquid, filter strictness is applied at render time,
        # and only on rendered markup. Unknown filters in unreached markup will
        # not throw an error.
        if func is None:
            if context.env.strict_filters:
                raise LiquidNameError(
                    repr(self.name.value),
                    token=self.name.token,
                    source=context.template.source,
                    name=context.template.name,
                )

            # Pass the input value through.
            return self.left.evaluate(context)

        left = self.left.evaluate(context)

        if not self.args:
            return func(FilterContext(context, self.span), left)

        args: list[object] = []
        kwargs: dict[str, object] = {}

        for arg in self.args:
            if isinstance(arg, KeywordArgument):
                kwargs[arg.name.value] = arg.expr.evaluate(context)
            else:
                args.append(arg.evaluate(context))

        return func(FilterContext(context, self.span), left, *args, **kwargs)

    async def evaluate_async(self, context: RenderContext) -> object:
        func = context.env.filters.get(self.name.value)

        # Like Shopify/liquid, filter strictness is applied at render time,
        # and only on rendered markup. Unknown filters in unreached markup will
        # not throw an error.
        if func is None:
            if context.env.strict_filters:
                raise LiquidNameError(
                    repr(self.name.value),
                    token=self.name.token,
                    source=context.template.source,
                    name=context.template.name,
                )

            # Pass the input value through.
            return await self.left.evaluate_async(context)

        left = await self.left.evaluate_async(context)

        if not self.args:
            return func(FilterContext(context, self.span), left)

        args: list[object] = []
        kwargs: dict[str, object] = {}

        for arg in self.args:
            if isinstance(arg, KeywordArgument):
                kwargs[arg.name.value] = await arg.expr.evaluate_async(context)
            else:
                args.append(await arg.evaluate_async(context))

        return func(FilterContext(context, self.span), left, *args, **kwargs)

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


# TODO: prefix expressions


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
class Variable:
    token: Token
    root: Name | StringLiteral | Variable
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
            if isinstance(self.root, Variable)
            else self.root.value
        )

        index = 0
        obj = context.resolve(selector)

        if self.selectors:
            obj, index = context.resolve_path(
                obj,
                [
                    s.evaluate(context) if isinstance(s, Variable) else s.value
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
            if isinstance(self.root, Variable)
            else self.root.value
        )

        index = 0
        obj = context.resolve(selector)

        if self.selectors:
            obj, index = await context.resolve_path_async(
                obj,
                [
                    await s.evaluate_async(context)
                    if isinstance(s, Variable)
                    else s.value
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

        if isinstance(self.root, Variable):
            exprs.append(self.root)

        if self.selectors:
            exprs.extend(s for s in self.selectors if isinstance(s, Variable))

        return exprs

    def path(self, selectors: list[PathSegment] | None) -> str:
        def serialize(selector: PathSegment, *, root: bool) -> str:
            if isinstance(selector, Name):
                return selector.value if root else f".{selector.value}"

            if isinstance(selector, Variable):
                return f"[{selector}]"

            return f"[{selector.value}]"

        root = serialize(self.root, root=True)

        if selectors:
            _selectors = "".join(serialize(s, root=False) for s in selectors)
            return f"{root}{_selectors}"

        return root

    def __str__(self) -> str:
        return self.path(self.selectors)


@dataclass(slots=True)
class IndexSelector:
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
class StringLiteral:
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
        start = context.env.to_int(self.start.evaluate(context), context, self.span)
        stop = context.env.to_int(self.stop.evaluate(context), context, self.span)
        return Range(start, stop)

    async def evaluate_async(self, context: RenderContext) -> object:
        start = context.env.to_int(
            await self.start.evaluate_async(context), context, self.span
        )
        stop = context.env.to_int(
            await self.stop.evaluate_async(context), context, self.span
        )
        return Range(start, stop)

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


@dataclass(slots=True)
class KeywordArgument:
    token: Token
    name: Name
    expr: Expression


type PathSegment = Name | StringLiteral | IndexSelector | Variable | RangeLiteral


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
