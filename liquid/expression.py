"""Liquid expression objects."""
from __future__ import annotations
import sys

from abc import ABC
from abc import abstractmethod

from collections import abc
from decimal import Decimal
from itertools import islice

from typing import Any
from typing import Dict
from typing import Generic
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Mapping
from typing import Optional
from typing import Tuple
from typing import TypeVar
from typing import Union

from liquid.context import Context
from liquid.context import FutureContext

from liquid import Markup

from liquid.exceptions import LiquidTypeError
from liquid.exceptions import Error
from liquid.exceptions import NoSuchFilterFunc
from liquid.exceptions import FilterValueError

from liquid.limits import to_int

# pylint: disable=missing-class-docstring too-few-public-methods too-many-lines


class Expression(ABC):
    __slots__ = ()

    @abstractmethod
    def evaluate(self, context: Context) -> object:
        """Evaluate the expression with the given context."""

    async def evaluate_async(self, context: Context) -> object:
        """An async version of :meth:`liquid.expression.Expression.evaluate`."""
        return self.evaluate(context)

    def children(self) -> List[Expression]:
        """Return a list of child expressions."""
        raise NotImplementedError(f"{self.__class__.__name__}.children")


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

    def children(self) -> List[Expression]:
        return []


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

    def children(self) -> List[Expression]:
        return []


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

    def children(self) -> List[Expression]:
        return []


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

    def children(self) -> List[Expression]:
        return []


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

    def __sizeof__(self) -> int:
        return sys.getsizeof(self.value)

    def evaluate(self, context: Context) -> object:
        return self.value

    def children(self) -> List[Expression]:
        return []


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

    def __sizeof__(self) -> int:
        return sys.getsizeof(self.value)

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
        return f"({self.start}..{self.stop})"

    def __repr__(self) -> str:  # pragma: no cover
        return f"RangeLiteral(start={self.start}, stop={self.stop})"

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

    def evaluate(self, context: Context) -> range:
        return self._make_range(
            self.start.evaluate(context), self.stop.evaluate(context)
        )

    async def evaluate_async(self, context: Context) -> range:
        return self._make_range(
            await self.start.evaluate_async(context),
            await self.stop.evaluate_async(context),
        )

    def children(self) -> List[Expression]:
        return [self.start, self.stop]


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
IdentifierTuple = Tuple[Union[str, "IdentifierTuple"], ...]


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
                _str = str(elem)
                if "." in _str:
                    buf.append(f'["{elem}"]')
                else:
                    buf.append(str(elem))
        return ".".join(buf).replace(".[", "[")

    def as_tuple(self) -> IdentifierTuple:
        """Return this identifier's path as a tuple."""
        parts: List[Union[str, IdentifierTuple]] = []
        for elem in self.path:
            if isinstance(elem, Identifier):
                parts.append(elem.as_tuple())
            else:
                parts.append(str(elem))
        return tuple(parts)

    def __hash__(self) -> int:
        return hash(tuple(self.path))

    def __sizeof__(self) -> int:
        return super().__sizeof__() + sys.getsizeof(self.path)

    def evaluate(self, context: Context) -> object:
        path: List[Any] = [elem.evaluate(context) for elem in self.path]
        return context.get(path)

    async def evaluate_async(self, context: Context) -> object:
        path: List[Any] = [await elem.evaluate_async(context) for elem in self.path]
        return await context.get_async(path)

    def children(self) -> List[Expression]:
        return [el for el in self.path if isinstance(el, Expression)]


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
        if self.operator == "not":
            return not is_truthy(right)
        if self.operator == "-":
            if isinstance(right, (int, float)):
                return -right
            raise LiquidTypeError(f"unknown operator {self.operator}{self.right}")

        raise LiquidTypeError(f"unknown operator {self.operator}")

    def evaluate(self, context: Context) -> object:
        return self._evaluate(self.right.evaluate(context))

    async def evaluate_async(self, context: Context) -> object:
        return self._evaluate(await self.right.evaluate_async(context))

    def children(self) -> List[Expression]:
        return [self.right]


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
        return compare(
            self.left.evaluate(context), self.operator, self.right.evaluate(context)
        )

    async def evaluate_async(self, context: Context) -> object:
        return compare(
            await self.left.evaluate_async(context),
            self.operator,
            await self.right.evaluate_async(context),
        )

    def children(self) -> List[Expression]:
        return [self.left, self.right]


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
        # Shortcut for the common case. Most filters do not use named parameters.
        if not self.kwargs:
            return {}
        return {k: v.evaluate(context) for k, v in self.kwargs.items()}

    async def evaluate_kwargs_async(self, context: Context) -> Dict[str, object]:
        """An async version of `evaluate_kwargs`."""
        # Shortcut for the common case. Most filters do not use named parameters.
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

    def children(self) -> List[Expression]:
        return [self.expression]


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
            f"filters={self.filters})"
        )

    def apply_filters(
        self,
        left: object,
        filters: Iterable[Filter],
        context: Context,
    ) -> object:
        """Return the result of applying all filters in this expression to an object."""
        rv = left
        for _filter in filters:
            try:
                func = context.filter(_filter.name)
            except NoSuchFilterFunc:
                if context.env.strict_filters:
                    raise
                continue

            # Any exception causes us to abort the filter chain and discard the result.
            # Nothing will be rendered.
            try:
                if not _filter.args and not _filter.kwargs:
                    rv = func(rv)
                elif _filter.args and not _filter.kwargs:
                    rv = func(rv, *_filter.evaluate_args(context))
                else:
                    rv = func(
                        rv,
                        *_filter.evaluate_args(context),
                        **_filter.evaluate_kwargs(context),
                    )
            except FilterValueError:
                # Pass over filtered expressions who's left value is not allowed.
                continue
            except Error:
                raise
            except Exception as err:
                raise Error(
                    f"filter '{_filter.name}': unexpected error: {err}"
                ) from err

        return rv

    async def apply_filters_async(
        self,
        left: object,
        filters: Iterable[Filter],
        context: Context,
    ) -> object:
        """Return the result of applying all filters in this expression to an object."""
        rv = left
        for _filter in filters:
            try:
                func = context.filter(_filter.name)
            except NoSuchFilterFunc:
                if context.env.strict_filters:
                    raise
                continue

            # Any exception causes us to abort the filter chain and discard the result.
            # Nothing will be rendered.
            try:
                if not _filter.args and not _filter.kwargs:
                    rv = func(rv)
                elif _filter.args and not _filter.kwargs:
                    rv = func(
                        rv,
                        *(await _filter.evaluate_args_async(context)),
                    )
                else:
                    rv = func(
                        rv,
                        *(await _filter.evaluate_args_async(context)),
                        **(await _filter.evaluate_kwargs_async(context)),
                    )
            except FilterValueError:
                # Pass over filtered expressions who's left value is not allowed.
                continue
            except Error:
                raise
            except Exception as err:
                raise Error(
                    f"filter '{_filter.name}': unexpected error: {err}"
                ) from err

        return rv

    def evaluate(self, context: Context) -> object:
        return self.apply_filters(
            self.expression.evaluate(context),
            self.filters,
            context,
        )

    async def evaluate_async(self, context: Context) -> object:
        return await self.apply_filters_async(
            await self.expression.evaluate_async(context),
            self.filters,
            context,
        )

    def children(self) -> List[Expression]:
        _children = [self.expression]
        for _filter in self.filters:
            _children.extend(_filter.args)
            _children.extend(_filter.kwargs.values())
        return _children


class ConditionalExpression(FilteredExpression):
    __slots__ = (
        "condition",
        "alternative",
    )

    def __init__(
        self,
        expression: Expression,
        filters: Optional[List[Filter]] = None,
        condition: Optional[Expression] = None,
        alternative: Optional[Expression] = None,
    ):
        super().__init__(expression, filters)
        self.expression = expression
        self.condition = condition
        self.alternative = alternative
        self.filters = filters or []  # These are "tail" filters

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ConditionalExpression)
            and self.expression == other.expression
            and self.condition == other.condition
            and self.alternative == other.alternative
            and self.filters == other.filters
        )

    def __str__(self) -> str:
        buf = [str(self.expression)]

        if self.condition:
            buf.append("if")
            buf.append(str(self.condition))

        if self.alternative:
            buf.append("else")
            buf.append(str(self.alternative))

        if self.filters:
            buf.append("|")
            buf.append(" | ".join([str(filter) for filter in self.filters]))

        return " ".join(buf)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ConditionalExpression(expression={self.expression!r}, "
            f"condition={self.condition}, "
            f"alternative={self.alternative}, "
            f"filters={self.filters})"
        )

    def evaluate(self, context: Context) -> object:
        if self.condition:
            if is_truthy(self.condition.evaluate(context)):
                result = self.expression.evaluate(context)

            elif self.alternative:
                result = self.alternative.evaluate(context)
            else:
                result = context.env.undefined("")
        else:
            result = self.expression.evaluate(context)

        if self.filters:
            result = self.apply_filters(result, self.filters, context)

        return result

    async def evaluate_async(self, context: Context) -> object:
        if self.condition:
            if is_truthy(await self.condition.evaluate_async(context)):
                result = await self.expression.evaluate_async(context)

            elif self.alternative:
                result = await self.alternative.evaluate_async(context)
            else:
                result = context.env.undefined("")
        else:
            result = await self.expression.evaluate_async(context)

        if self.filters:
            result = await self.apply_filters_async(result, self.filters, context)

        return result

    def children(self) -> List[Expression]:
        _children = [self.expression]

        if self.condition is not None:
            _children.append(self.condition)

        if self.alternative is not None:
            _children.append(self.alternative)

        for _filter in self.filters:
            _children.extend(_filter.args)
            _children.extend(_filter.kwargs.values())

        return _children


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
        context.assign(key=self.name, val=self.expression.evaluate(context))
        return ""

    async def evaluate_async(self, context: Context) -> str:
        context.assign(
            key=self.name,
            val=(await self.expression.evaluate_async(context)),
        )
        return ""

    def children(self) -> List[Expression]:
        return [self.expression]


LoopArgument = Union[
    IntegerLiteral,
    FloatLiteral,
    Identifier,
    Continue,
    Nil,
]

# An identifier that resolves to an iterable or a range expression.
LoopIterable = Union[Identifier, RangeLiteral, StringLiteral]


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
        limit: LoopArgument = NIL,
        offset: LoopArgument = NIL,
        cols: LoopArgument = NIL,
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

        if self.limit != NIL:
            buf.append(f"limit:{self.limit}")

        if self.offset != NIL:
            buf.append(f"offset:{self.offset}")

        if self.cols != NIL:
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

    def _limit_and_offset(
        self,
        it: Iterator[Any],
        size: int,
        limit: Optional[int],
        offset: Optional[int | Continue],
        context: Context,
    ) -> Tuple[Iterator[Any], int]:
        """Slice iterable `it` according to `limit` and `offset`."""
        length = size

        # For the sake of the special for loop offset `continue`, we need to derive an
        # identifier for this loop and store the theoretical stop index on the render
        # context using that identifier.
        #
        # For compatibility with the reference implementation, we'll key loop stop
        # indexes on the loop item name and the name of the iterable. Not the contents
        # of the iterable. In the case of a range expression, we'll use a string
        # representation of the expression.
        offset_key = "-".join([self.name, str(self.iterable)])

        if limit is None and offset is None:
            context.stopindex(key=offset_key, index=length)
            if self.reversed:
                return reversed(list(it)), length
            return it, length

        if offset == CONTINUE:
            offset = context.stopindex(key=offset_key)
            length = max(length - offset, 0)
        elif offset is not None:
            assert isinstance(offset, int), f"found {offset!r}"
            length = max(length - offset, 0)

        if limit is not None:
            length = min(length, limit)

        if offset:
            stop = offset + length
        else:
            stop = length

        context.stopindex(key=offset_key, index=stop)
        it = islice(it, offset, stop)

        if self.reversed:
            return reversed(list(it)), length
        return it, length

    def _obj_to_iter(self, obj: object, context: Context) -> Tuple[Iterator[Any], int]:
        if isinstance(obj, abc.Mapping):
            return iter(obj.items()), len(obj)
        if isinstance(obj, range):
            return iter(obj), len(obj)
        if isinstance(obj, str) and isinstance(context, FutureContext):  # Bit of a hack
            return (iter([obj]), 1)
        if isinstance(obj, abc.Sequence):
            return iter(obj), len(obj)

        raise LiquidTypeError(
            f"expected array or hash at '{self.iterable}', found '{str(obj)}'"
        )

    def _raise_for_invalid_argument(self, arg: object) -> None:
        if arg is not None and not isinstance(arg, int):
            raise LiquidTypeError(f"expected an integer argument, found {arg!r}")

    def evaluate(self, context: Context) -> Tuple[Iterator[Any], int]:
        obj = self.iterable.evaluate(context)
        it, length = self._obj_to_iter(obj, context)

        limit = self.limit.evaluate(context)
        self._raise_for_invalid_argument(limit)
        assert isinstance(limit, int) or limit is None

        if self.offset != CONTINUE:
            offset = self.offset.evaluate(context)
            self._raise_for_invalid_argument(offset)
            assert isinstance(offset, int) or offset is None
        else:
            offset = self.offset
            assert isinstance(offset, Continue)

        return self._limit_and_offset(
            it,
            size=length,
            limit=limit,
            offset=offset,
            context=context,
        )

    async def evaluate_async(self, context: Context) -> Tuple[Iterator[Any], int]:
        obj = await self.iterable.evaluate_async(context)
        it, length = self._obj_to_iter(obj, context)

        limit = await self.limit.evaluate_async(context)
        self._raise_for_invalid_argument(limit)
        assert isinstance(limit, int) or limit is None

        if self.offset != CONTINUE:
            offset = await self.offset.evaluate_async(context)
            self._raise_for_invalid_argument(offset)
            assert isinstance(offset, int) or offset is None
        else:
            offset = self.offset
            assert isinstance(offset, Continue)

        return self._limit_and_offset(
            it,
            size=length,
            limit=limit,
            offset=offset,
            context=context,
        )

    def children(self) -> List[Expression]:
        return [
            self.iterable,
            self.limit,
            self.offset,
            self.cols,
        ]


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


def _is_py_falsy_number(obj: object) -> bool:
    # Liquid 0, 0.0, 0b0, 0X0, 0o0 and Decimal("0") are not falsy.
    return not isinstance(obj, bool) and isinstance(obj, (int, float, Decimal))


def is_truthy(obj: Any) -> bool:
    """Return True if the given object is Liquid truthy."""
    if hasattr(obj, "__liquid__"):
        obj = obj.__liquid__()
    return _is_py_falsy_number(obj) or obj not in (False, None)


# pylint: disable=too-many-return-statements
def compare_bool(left: Any, operator: str, right: Any) -> bool:
    """Compare an object to a boolean value."""
    if (isinstance(left, bool) and _is_py_falsy_number(right)) or (
        isinstance(right, bool) and _is_py_falsy_number(left)
    ):
        if operator in ("==", "<", ">", "<=", ">="):
            return False
        if operator in ("!=", "<>"):
            return True
        raise LiquidTypeError(
            f"unknown operator: {type(left)} {operator} {type(right)}"
        )

    if operator == "==":
        return bool(left == right)
    if operator in ("!=", "<>"):
        return bool(left != right)
    if operator in ("<", ">", "<=", ">="):
        return False

    raise LiquidTypeError(f"unknown operator: {type(left)} {operator} {type(right)}")


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

    if isinstance(left, bool) or isinstance(right, bool):
        return compare_bool(left, operator, right)

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
