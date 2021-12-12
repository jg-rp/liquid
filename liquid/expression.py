"""Tag and output statement expression objects."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from collections import abc
from itertools import islice

from typing import Dict
from typing import Union
from typing import List
from typing import Optional
from typing import Any
from typing import Iterator
from typing import Mapping
from typing import Tuple
from typing import Generic
from typing import TypeVar

try:
    from markupsafe import Markup
except ImportError:
    from liquid.exceptions import Markup  # type: ignore

from liquid.context import Context

from liquid.exceptions import LiquidTypeError
from liquid.exceptions import Error
from liquid.exceptions import NoSuchFilterFunc
from liquid.exceptions import FilterValueError

# pylint: disable=missing-class-docstring too-few-public-methods


class Expression(ABC):
    __slots__ = ()

    @abstractmethod
    def evaluate(self, context: Context) -> object:
        """Evaluate the expression with the given context."""

    async def evaluate_async(self, context: Context) -> object:
        """An async version of :meth:`liquid.expression.Expression.evaluate`."""
        return self.evaluate(context)


class Nil(Expression):
    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        return other is None or isinstance(other, Nil)

    def __repr__(self) -> str:  # pragma: no cover
        return "NIL()"

    def __str__(self) -> str:  # pragma: no cover
        return ""

    def evaluate(self, context: Context) -> None:
        return None


NIL = Nil()


class Empty(Expression):
    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Empty):
            return True
        if isinstance(other, (list, dict, str)) and not other:
            return True
        return False

    def __repr__(self) -> str:  # pragma: no cover
        return "Empty()"

    def __str__(self) -> str:  # pragma: no cover
        return "empty"

    def evaluate(self, context: Context) -> Empty:
        return self


EMPTY = Empty()


class Blank(Expression):
    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str) and (not other or other.isspace()):
            return True
        if isinstance(other, (list, dict)) and not other:
            return True
        if isinstance(other, Blank):
            return True

        return False

    def __repr__(self) -> str:  # pragma: no cover
        return "Blank()"

    def __str__(self) -> str:  # pragma: no cover
        return "blank"

    def evaluate(self, context: Context) -> Blank:
        return self


BLANK = Blank()


class Continue(Expression):
    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Continue):
            return True
        return False

    def __repr__(self) -> str:  # pragma: no cover
        return "Continue()"

    def __str__(self) -> str:  # pragma: no cover
        return "continue"

    def evaluate(self, context: Context) -> int:
        return 0


CONTINUE = Continue()


T = TypeVar("T")  # pylint: disable=invalid-name


class Literal(Expression, Generic[T]):
    __slots__ = ("value",)

    def __init__(self, value: T):
        self.value = value

    def __str__(self) -> str:
        return repr(self.value)

    def __eq__(self, other: object) -> bool:
        return self.value == other

    def __hash__(self) -> int:
        return hash(self.value)

    def evaluate(self, context: Context) -> object:
        return self.value


class Boolean(Literal[bool]):
    __slots__ = ()

    def __init__(self, value: bool):
        super().__init__(value)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Boolean) and self.value == other.value

    def __repr__(self) -> str:  # pragma: no cover
        return f"Boolean(value={self.value})"


TRUE = Boolean(True)
FALSE = Boolean(False)


class StringLiteral(Literal[str]):
    __slots__ = ()

    def __init__(self, value: str):
        super().__init__(value)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, StringLiteral) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:  # pragma: no cover
        return f"StringLiteral(value='{self.value}')"

    def evaluate(self, context: Context) -> Union[str, Markup]:
        if context.autoescape:
            return Markup(self.value)
        return self.value


class IntegerLiteral(Literal[int]):
    __slots__ = ()

    def __init__(self, value: int):
        super().__init__(value)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, IntegerLiteral) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:  # pragma: no cover
        return f"IntegerLiteral(value={self.value})"


class FloatLiteral(Literal[float]):
    __slots__ = ()

    def __init__(self, value: float):
        super().__init__(value)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, FloatLiteral) and self.value == other.value

    def __repr__(self) -> str:  # pragma: no cover
        return f"FloatLiteral(value={self.value})"


class RangeLiteral(Expression):
    __slots__ = ("start", "stop")

    def __init__(self, start: Expression, stop: Expression):
        self.start = start
        self.stop = stop

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, RangeLiteral)
            and self.start == other.start
            and self.stop == other.stop
        )

    def __str__(self) -> str:
        return f"{self.start}..{self.stop}"

    def __repr__(self) -> str:  # pragma: no cover
        return f"RangeLiteral(start={self.start}, stop={self.stop})"

    def __hash__(self) -> int:
        return hash((self.start, self.stop))

    def evaluate(self, context: Context) -> range:
        start: Any = self.start.evaluate(context)
        stop: Any = self.stop.evaluate(context)

        # Floats get cast to integers

        try:
            start = int(start)
        except ValueError as err:
            raise LiquidTypeError(f"expected an int or float, found '{start}'") from err

        try:
            stop = int(stop)
        except ValueError as err:
            raise LiquidTypeError(f"expected an int or float, found '{stop}'") from err

        # Decending ranges don't work
        if start > stop:
            return range(0)

        return range(start, stop + 1)

    async def evaluate_async(self, context: Context) -> range:
        start: Any = await self.start.evaluate_async(context)
        stop: Any = await self.stop.evaluate_async(context)

        # Floats get cast to integers

        try:
            start = int(start)
        except ValueError as err:
            raise LiquidTypeError(f"expected an int or float, found {start}") from err

        try:
            stop = int(stop)
        except ValueError as err:
            raise LiquidTypeError(f"expected an int or float, found {stop}") from err

        if start > stop:
            return range(0)

        return range(start, stop + 1)


class IdentifierPathElement(Literal[Union[int, str]]):
    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, IdentifierPathElement) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:  # pragma: no cover
        return f"IdentifierPathElement(value={self.value})"

    def __str__(self) -> str:
        return str(self.value)


IdentifierPath = List[Union[IdentifierPathElement, "Identifier"]]


class Identifier(Expression):
    __slots__ = ("path",)

    def __init__(self, path: IdentifierPath):
        self.path = path

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Identifier) and self.path == other.path

    def __repr__(self) -> str:  # pragma: no cover
        return f"Identifier(path={self.path})"

    def __str__(self) -> str:
        buf = []

        for elem in self.path:
            if isinstance(elem, Identifier):
                buf.append(f"[{elem}]")
            else:
                buf.append(str(elem))
        return ".".join(buf)

    def __hash__(self) -> int:
        return hash(tuple(self.path))

    def evaluate(self, context: Context) -> object:
        path: List[Any] = [elem.evaluate(context) for elem in self.path]
        return context.get(path)

    async def evaluate_async(self, context: Context) -> object:
        path: List[Any] = [await elem.evaluate_async(context) for elem in self.path]
        return await context.get_async(path)


class PrefixExpression(Expression):
    __slots__ = ("operator", "right")

    def __init__(self, operator: str, right: Expression):
        self.operator = operator
        self.right = right

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, PrefixExpression)
            and self.operator == other.operator
            and self.right == other.right
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"PrefixExpression(operator='{self.operator}', right={self.right!r})"

    def __str__(self) -> str:
        return f"({self.operator}{self.right})"

    def _evaluate(self, right: object) -> Union[int, float]:
        if self.operator == "-":
            if isinstance(right, (int, float)):
                return -right
            raise LiquidTypeError(f"unknown operator {self.operator}{self.right}")

        raise LiquidTypeError(f"unknown operator {self.operator}")

    def evaluate(self, context: Context) -> object:
        right = self.right.evaluate(context)
        return self._evaluate(right)

    async def evaluate_async(self, context: Context) -> object:
        right = await self.right.evaluate_async(context)
        return self._evaluate(right)


class InfixExpression(Expression):
    __slots__ = ("left", "operator", "right")

    def __init__(
        self,
        left: Expression,
        operator: str,
        right: Expression,
    ):
        self.left = left
        self.operator = operator
        self.right = right

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, InfixExpression)
            and self.left == other.left
            and self.operator == other.operator
            and self.right == other.right
        )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"InfixExpression(left={self.left!r}, "
            f"operator='{self.operator}', right={self.right!r})"
        )

    def __str__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"

    def evaluate(self, context: Context) -> object:
        left = self.left.evaluate(context)
        right = self.right.evaluate(context)
        return compare(left, self.operator, right)

    async def evaluate_async(self, context: Context) -> object:
        left = await self.left.evaluate_async(context)
        right = await self.right.evaluate_async(context)
        return compare(left, self.operator, right)


class Filter:
    __slots__ = ("name", "args", "kwargs")

    def __init__(
        self,
        name: str,
        args: List[Expression],
        kwargs: Optional[Mapping[str, Expression]] = None,
    ):
        self.name = name
        self.args = args
        self.kwargs = kwargs or {}

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Filter)
            and self.name == other.name
            and self.args == other.args
            and self.kwargs == other.kwargs
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"Filter(name='{self.name}', args={self.args}, kwargs={self.kwargs})"

    def __str__(self) -> str:
        buf = [self.name]

        args_str = ", ".join([str(arg) for arg in self.args])
        if args_str:
            buf.append(f": {args_str}")
            # return f"{self.name}: {args_str})"

        kwargs_str = ", ".join([f"{k}: {v}" for k, v in self.kwargs.items()])
        if kwargs_str:
            buf.append(f", {kwargs_str}")

        return "".join(buf)

    def evaluate_args(self, context: Context) -> List[object]:
        """Return a list of filter arguments evaluated with the given context."""
        return [arg.evaluate(context) for arg in self.args]

    async def evaluate_args_async(self, context: Context) -> List[object]:
        """An async version of `evaluate_args`."""
        return [await arg.evaluate_async(context) for arg in self.args]

    def evaluate_kwargs(self, context: Context) -> Dict[str, object]:
        """Return a dictionary of filter keyword arguments evaluated with the given
        context."""
        # Shortcut for the common case. Most filters do not use named
        # parameters.
        if not self.kwargs:
            return {}
        return {k: v.evaluate(context) for k, v in self.kwargs.items()}

    async def evaluate_kwargs_async(self, context: Context) -> Dict[str, object]:
        """An async version of `evaluate_kwargs`."""
        # Shortcut for the common case. Most filters do not use named
        # parameters.
        if not self.kwargs:
            return {}
        return {k: await v.evaluate_async(context) for k, v in self.kwargs.items()}


class BooleanExpression(Expression):
    __slots__ = ("expression",)

    def __init__(self, expression: Expression):
        self.expression = expression

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, BooleanExpression) and self.expression == other.expression
        )

    def __str__(self) -> str:
        expr_str = str(self.expression)
        if not expr_str.startswith("("):
            return f"({expr_str})"
        return expr_str

    def __repr__(self) -> str:  # pragma: no cover
        return f"BooleanExpression(expression={self.expression!r})"

    def evaluate(self, context: Context) -> bool:
        return is_truthy(self.expression.evaluate(context))

    async def evaluate_async(self, context: Context) -> bool:
        return is_truthy(await self.expression.evaluate_async(context))


class FilteredExpression(Expression):
    __slots__ = ("expression", "filters")

    def __init__(self, expression: Expression, filters: Optional[List[Filter]] = None):
        self.expression = expression
        self.filters = filters or []

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, FilteredExpression)
            and self.expression == other.expression
            and self.filters == other.filters
        )

    def __str__(self) -> str:
        filter_str = " | ".join([str(filter) for filter in self.filters])

        if filter_str:
            return f"{self.expression} | {filter_str}"
        return str(self.expression)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"FilteredExpression(expression={self.expression!r}, "
            "filters={self.filters})"
        )

    def evaluate(self, context: Context) -> object:
        result = self.expression.evaluate(context)

        for _filter in self.filters:
            try:
                func = context.filter(_filter.name)
            except NoSuchFilterFunc:
                if context.env.strict_filters:
                    raise
                continue

            # Any exception causes us to abort the filter chain and discard the result.
            # Nothing will be rendered.
            try:
                args = _filter.evaluate_args(context)
                kwargs = _filter.evaluate_kwargs(context)
                result = func(result, *args, **kwargs)
            except FilterValueError:
                # Pass over filtered expressions who's left value is not allowed.
                continue
            except Error:
                raise
            except Exception as err:
                raise Error(
                    f"filter '{_filter.name}': unexpected error: {err}"
                ) from err

        return result

    async def evaluate_async(self, context: Context) -> object:
        result = await self.expression.evaluate_async(context)

        for _filter in self.filters:
            try:
                func = context.filter(_filter.name)
            except NoSuchFilterFunc:
                if context.env.strict_filters:
                    raise
                continue

            # Any exception causes us to abort the filter chain and discard the result.
            # Nothing will be rendered.
            try:
                args = await _filter.evaluate_args_async(context)
                kwargs = await _filter.evaluate_kwargs_async(context)
                result = func(result, *args, **kwargs)
            except FilterValueError:
                # Pass over filtered expressions who's left value is not allowed.
                continue
            except Error:
                raise
            except Exception as err:
                raise Error(
                    f"filter '{_filter.name}': unexpected error: {err}"
                ) from err

        return result


class AssignmentExpression(Expression):
    __slots__ = ("name", "expression")

    def __init__(self, name: str, expression: Expression):
        self.name = name
        self.expression = expression

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, AssignmentExpression)
            and self.name == other.name
            and self.expression == other.expression
        )

    def __str__(self) -> str:
        return f"{self.name} = {self.expression}"

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"AssignmentExpression(name='{self.name}', expression={self.expression!r})"
        )

    def evaluate(self, context: Context) -> str:
        result = self.expression.evaluate(context)
        context.assign(key=self.name, val=result)
        return ""

    async def evaluate_async(self, context: Context) -> str:
        result = await self.expression.evaluate_async(context)
        context.assign(key=self.name, val=result)
        return ""


LoopArgument = Optional[Union[IntegerLiteral, FloatLiteral, Identifier, Continue]]

# An identifier that resolves to an iterable or a range expression.
LoopIterable = Union[Identifier, RangeLiteral]


class LoopExpression(Expression):
    """Loop expression tree/object model, as returned by parse_loop_expression.

    Start, stop, limit and offset can be integer literals or identifiers
    that resolve to an integer at render time.

    `cols` is used by the built-in tag `tablerow` only. It will be ignored
    by the `for` tag.
    """

    __slots__ = (
        "name",
        "iterable",
        "limit",
        "offset",
        "cols",
        "reversed",
    )

    def __init__(
        self,
        name: str,
        iterable: LoopIterable,
        limit: LoopArgument = None,
        offset: LoopArgument = None,
        cols: LoopArgument = None,
        reversed_: bool = False,
    ):
        self.name = name
        self.iterable = iterable
        self.limit = limit
        self.offset = offset
        self.cols = cols
        self.reversed = reversed_

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, LoopExpression)
            and self.name == other.name
            and self.iterable == other.iterable
            and self.limit == other.limit
            and self.offset == other.offset
            and self.cols == other.cols
            and self.reversed == other.reversed
        )

    def __str__(self) -> str:
        buf = [f"{self.name} in", str(self.iterable)]

        if self.limit:
            buf.append(f"limit:{self.limit}")

        if self.offset:
            buf.append(f"offset:{self.offset}")

        if self.cols:
            buf.append(f"cols:{self.cols}")

        if self.reversed:
            buf.append("reversed")

        return " ".join(buf)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"LoopExpression(name='{self.name}', iterable={self.iterable}, "
            f"limit={self.limit}, offset={self.offset}, "
            f"cols={self.cols}, reversed={self.reversed})"
        )

    def evaluate(self, context: Context) -> Tuple[Iterator[Any], int]:
        # For the sake of the special for loop offset `continue`, we need to derive an
        # identifier for this loop and store the theoretical stop index on the render
        # context using that identifier.
        #
        # For compatibility with the reference implementation, we'll key loop stop
        # indexes on the loop item name and the name of the iterable. Not the contents
        # of the iterable. In the case of a range expression, we'll use a string
        # representation of the expression.
        _offset_key = [self.name, str(self.iterable)]
        obj = self.iterable.evaluate(context)

        if isinstance(obj, abc.Mapping):
            length = len(obj)
            loop_iter: Iterator[Any] = iter(obj.items())
        elif isinstance(obj, range):
            length = obj.stop - obj.start
            loop_iter = iter(obj)
        elif isinstance(obj, abc.Sequence):
            length = len(obj)
            loop_iter = iter(obj)
        else:
            raise LiquidTypeError(
                f"expected array or hash at '{self.iterable}', found '{str(obj)}'"
            )

        limit: Optional[int] = None
        offset: Optional[int] = None
        offset_key = "-".join(_offset_key)

        if self.offset:
            if self.offset == CONTINUE:
                offset = context.stopindex(key=offset_key)
            else:
                _offset = self.offset.evaluate(context)
                assert isinstance(_offset, int)
                offset = _offset

            length = max(length - offset, 0)

        if self.limit:
            _limit = self.limit.evaluate(context)
            assert isinstance(_limit, int)
            limit = _limit
            length = min(length, limit)

        context.stopindex(key=offset_key, index=length)
        loop_iter = islice(loop_iter, offset, limit)

        if self.reversed:
            loop_iter = reversed(list(loop_iter))

        return loop_iter, length

    async def evaluate_async(self, context: Context) -> Tuple[Iterator[Any], int]:
        _offset_key = [self.name, str(self.iterable)]
        obj = await self.iterable.evaluate_async(context)

        if isinstance(obj, abc.Mapping):
            length = len(obj)
            loop_iter: Iterator[Any] = iter(obj.items())
        elif isinstance(obj, range):
            length = obj.stop - obj.start + 1
            loop_iter = iter(obj)
        elif isinstance(obj, abc.Sequence):
            length = len(obj)
            loop_iter = iter(obj)
        else:
            raise LiquidTypeError(
                f"expected array or hash at '{self.iterable}', found '{str(obj)}'"
            )

        limit: Optional[int] = None
        offset: Optional[int] = None
        offset_key = "-".join(_offset_key)

        if self.offset:
            if self.offset == CONTINUE:
                offset = context.stopindex(key=offset_key)
            else:
                _offset = await self.offset.evaluate_async(context)
                assert isinstance(_offset, int)
                offset = _offset

            length = max(length - offset, 0)

        if self.limit:
            _limit = await self.limit.evaluate_async(context)
            assert isinstance(_limit, int)
            limit = _limit
            length = min(length, limit)

        context.stopindex(key=offset_key, index=length)
        loop_iter = islice(loop_iter, offset, limit)

        if self.reversed:
            loop_iter = reversed(list(loop_iter))

        return loop_iter, length


Number = Union[int, float]


def eval_number_expression(left: Number, operator: str, right: Number) -> bool:
    """Return the result of comparing two numbers with the given operator."""
    if operator == "<=":
        return left <= right
    if operator == ">=":
        return left >= right
    if operator == "<":
        return left < right
    if operator == ">":
        return left > right

    raise LiquidTypeError(f"unknown operator {left} {operator} {right}")


def is_truthy(obj: Any) -> bool:
    """Return True if the given object is Liquid truthy."""
    if hasattr(obj, "__liquid__"):
        obj = obj.__liquid__()

    if obj in (False, None):
        return False
    return True


# pylint: disable=too-many-return-statements,too-many-branches
def compare(left: Any, operator: str, right: Any) -> bool:
    """Return the result of a comparison operation between two objects."""
    if operator == "and":
        return is_truthy(left) and is_truthy(right)
    if operator == "or":
        return is_truthy(left) or is_truthy(right)

    if hasattr(left, "__liquid__"):
        left = left.__liquid__()
    if hasattr(right, "__liquid__"):
        right = right.__liquid__()

    if isinstance(right, (Empty, Blank)):
        left, right = right, left

    if operator == "==":
        return bool(left == right)
    if operator in ("!=", "<>"):
        return bool(left != right)

    if operator == "contains":
        if isinstance(left, str):
            return str(right) in left
        if isinstance(left, (list, dict)):
            return right in left

    if None in (left, right):
        return False

    if type(left) in (int, float) and type(right) in (int, float):
        return eval_number_expression(left, operator, right)

    # pylint: disable=unidiomatic-typecheck
    if type(left) != type(right):
        raise LiquidTypeError(
            f"invalid operator for types '{str(left)} {operator} {str(right)}'"
        )

    raise LiquidTypeError(f"unknown operator: {type(left)} {operator} {type(right)}")
