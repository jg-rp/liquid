"""Built-in filtered expressions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from liquid.exceptions import LiquidTypeError
from liquid.exceptions import NoSuchFilterFunc
from liquid.expression import Expression

if TYPE_CHECKING:
    from liquid import Environment
    from liquid import RenderContext
    from liquid.token import Token

    from .arguments import KeywordArgument
    from .arguments import PositionalArgument


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
            return f"{self.name}: {''.join(str(arg) for arg in self.args)}"
        return self.name

    def validate_filter_arguments(self, env: Environment) -> None:
        try:
            func = env.filters[self.name]
        except KeyError as err:
            raise NoSuchFilterFunc(
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
            raise LiquidTypeError(str(err), token=self.token) from err
        except LiquidTypeError as err:
            err.token = self.token
            raise err

    async def evaluate_async(self, left: object, context: RenderContext) -> object:
        func = context.filter(self.name, token=self.token)
        positional_args, keyword_args = await self.evaluate_args_async(context)

        try:
            return func(left, *positional_args, **keyword_args)
        except TypeError as err:
            raise LiquidTypeError(f"{self.name}: {err}", token=self.token) from err
        except LiquidTypeError as err:
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
