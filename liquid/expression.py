"""Tag and output statement expression objects."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from collections import abc
from itertools import islice

from typing import Union
from typing import List
from typing import Optional
from typing import Any
from typing import Iterator
from typing import Mapping
from typing import Tuple
from typing import Generic
from typing import TypeVar

from liquid.context import Context
from liquid.exceptions import LiquidTypeError, Error

# pylint: disable=missing-class-docstring too-few-public-methods


class Expression(ABC):
    __slots__ = ()

    expression_statement = True

    @abstractmethod
    def evaluate(self, context: Context) -> object:
        """Evaluate the expression with the given context."""


class Nil(Expression):
    __slots__ = ()

    def __eq__(self, other: object):
        return isinstance(other, Nil)

    def __repr__(self):  # pragma: no cover
        return "Nil()"

    def __str__(self):  # pragma: no cover
        return "nil"

    def evaluate(self, context: Context) -> None:
        return None


NIL = Nil()


class Empty(Expression):
    __slots__ = ()

    def __eq__(self, other: object):
        if isinstance(other, (Empty, Blank)):
            return True
        if isinstance(other, (list, dict, str)) and not other:
            return True
        return False

    def __repr__(self):  # pragma: no cover
        return "Empty()"

    def __str__(self):  # pragma: no cover
        return "empty"

    def evaluate(self, context: Context) -> Empty:
        return self


EMPTY = Empty()

# As far as I'm able to tell, the reference implementation treats `empty`
# and `blank` as an alias for the empty string. Are they simply converting
# empty collections to strings (empty strings in the case of empty collections)
# before comparing they to `blank` and/or `empty`?


class Blank(Empty):
    __slots__ = ()

    def __repr__(self):  # pragma: no cover
        return "Blank()"

    def __str__(self):  # pragma: no cover
        return "blank"


BLANK = Blank()


T = TypeVar("T")  # pylint: disable=invalid-name


class Literal(Expression, Generic[T]):
    __slots__ = "value"

    def __init__(self, value: T):
        self.value = value

    def __str__(self):
        return repr(self.value)

    def __hash__(self):
        return hash(self.value)

    def evaluate(self, context: Context) -> object:
        return self.value


class Boolean(Literal):
    __slots__ = ()

    def __init__(self, value: bool):
        super().__init__(value)

    def __eq__(self, other: object):
        return isinstance(other, Boolean) and self.value == other.value

    def __repr__(self):  # pragma: no cover
        return f"Boolean(value={self.value})"


TRUE = Boolean(True)
FALSE = Boolean(False)


class StringLiteral(Literal):
    __slots__ = ()

    def __init__(self, value: str):
        super().__init__(value)

    def __eq__(self, other: object):
        return isinstance(other, StringLiteral) and self.value == other.value

    def __repr__(self):  # pragma: no cover
        return f"StringLiteral(value='{self.value}')"


class IntegerLiteral(Literal):
    __slots__ = ()

    def __init__(self, value: int):
        super().__init__(value)

    def __eq__(self, other: object):
        return isinstance(other, IntegerLiteral) and self.value == other.value

    def __repr__(self):  # pragma: no cover
        return f"IntegerLiteral(value={self.value})"


class FloatLiteral(Literal):
    __slots__ = ()

    def __init__(self, value: float):
        super().__init__(value)

    def __eq__(self, other: object):
        return isinstance(other, FloatLiteral) and self.value == other.value

    def __repr__(self):  # pragma: no cover
        return f"FloatLiteral(value={self.value})"


class IdentifierPathElement(Literal):
    __slots__ = ()

    def __eq__(self, other: object):
        return isinstance(other, IdentifierPathElement) and self.value == other.value

    def __repr__(self):  # pragma: no cover
        return f"IdentifierPathElement(value={self.value})"

    def __str__(self):
        return str(self.value)


IdentifierPath = List[Union[IdentifierPathElement, "Identifier"]]


class Identifier(Expression):
    __slots__ = "path"

    def __init__(self, path: IdentifierPath):
        self.path = path

    def __eq__(self, other: object):
        return isinstance(other, Identifier) and self.path == other.path

    def __repr__(self):  # pragma: no cover
        return f"Identifier(path={self.path})"

    def __str__(self):
        buf = []

        for elem in self.path:
            if isinstance(elem, Identifier):
                buf.append(f"[{elem}]")
            else:
                buf.append(str(elem))
        return ".".join(buf)

    def __hash__(self):
        return hash(str(self))

    def evaluate(self, context: Context) -> object:
        path: List[Any] = [elem.evaluate(context) for elem in self.path]
        return context.get(path)


class PrefixExpression(Expression):
    __slots__ = ("operator", "right")

    def __init__(self, operator: str, right: Expression):
        self.operator = operator
        self.right = right

    def __eq__(self, other: object):
        return (
            isinstance(other, PrefixExpression)
            and self.operator == other.operator
            and self.right == other.right
        )

    def __repr__(self):  # pragma: no cover
        return f"PrefixExpression(operator='{self.operator}', right={self.right!r})"

    def __str__(self):
        return f"({self.operator}{self.right})"

    def evaluate(self, context: Context):
        right = self.right.evaluate(context)

        if self.operator == "-":
            if isinstance(right, (int, float)):
                return -right
            raise LiquidTypeError(f"unknown operator {self.operator}{self.right}")

        raise LiquidTypeError(f"unknown operator {self.operator}")


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

    def __eq__(self, other: object):
        return (
            isinstance(other, InfixExpression)
            and self.left == other.left
            and self.operator == other.operator
            and self.right == other.right
        )

    def __repr__(self):  # pragma: no cover
        return (
            f"InfixExpression(left={self.left!r}, "
            f"operator='{self.operator}', right={self.right!r})"
        )

    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"

    def evaluate(self, context: Context):
        left = self.left.evaluate(context)
        right = self.right.evaluate(context)
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

    def __eq__(self, other: object):
        return (
            isinstance(other, Filter)
            and self.name == other.name
            and self.args == other.args
            and self.kwargs == other.kwargs
        )

    def __repr__(self):  # pragma: no cover
        return f"Filter(name='{self.name}', args={self.args}, kwargs={self.kwargs})"

    def __str__(self):
        buf = [self.name]

        args_str = ", ".join([str(arg) for arg in self.args])
        if args_str:
            buf.append(f": {args_str}")
            # return f"{self.name}: {args_str})"

        kwargs_str = ", ".join([f"{k}: {v}" for k, v in self.kwargs.items()])
        if kwargs_str:
            if len(buf) == 1:
                buf.append(f": {kwargs_str}")
            else:
                buf.append(f", {kwargs_str}")

        return "".join(buf)

    def evaluate_args(self, context: Context):
        return [arg.evaluate(context) for arg in self.args]

    def evaluate_kwargs(self, context: Context):
        # Shortcut for the common case. Most filters do not use named
        # parameters.
        if not self.kwargs:
            return {}
        return {k: v.evaluate(context) for k, v in self.kwargs.items()}


class BooleanExpression(Expression):
    __slots__ = ("expression",)

    def __init__(self, expression: Expression):
        self.expression = expression

    def __eq__(self, other: object):
        return (
            isinstance(other, BooleanExpression) and self.expression == other.expression
        )

    def __str__(self):
        expr_str = str(self.expression)
        if not expr_str.startswith("("):
            return f"({expr_str})"
        return expr_str

    def __repr__(self):  # pragma: no cover
        return f"BooleanExpression(expression={self.expression!r})"

    def evaluate(self, context: Context) -> bool:
        return is_truthy(self.expression.evaluate(context))


class FilteredExpression(Expression):
    __slots__ = ("expression", "filters")

    def __init__(self, expression: Expression, filters: Optional[List[Filter]] = None):
        self.expression = expression
        self.filters = filters or []

    def __eq__(self, other: object):
        return (
            isinstance(other, FilteredExpression)
            and self.expression == other.expression
            and self.filters == other.filters
        )

    def __str__(self):
        filter_str = " | ".join([str(filter) for filter in self.filters])

        if filter_str:
            return f"{self.expression} | {filter_str}"
        return str(self.expression)

    def __repr__(self):  # pragma: no cover
        return (
            f"FilteredExpression(expression={self.expression!r}, "
            "filters={self.filters})"
        )

    def evaluate(self, context: Context) -> object:
        result = self.expression.evaluate(context)

        for fltr in self.filters:
            func = context.filter(fltr.name)
            try:
                args = fltr.evaluate_args(context)
                kwargs = fltr.evaluate_kwargs(context)
                result = func(result, *args, **kwargs)
            except Exception as err:
                # Any exception causes us to abort the filter chain and discard the
                # result. Nothing will be rendered.
                if not issubclass(type(err), Error):
                    raise Error(
                        f"filter '{fltr.name}': unexpected error: {err}"
                    ) from err
                raise

        return result


class AssignmentExpression(Expression):
    __slots__ = ("name", "expression")

    def __init__(self, name: str, expression: Expression):
        self.name = name
        self.expression = expression

    def __eq__(self, other: object):
        return (
            isinstance(other, AssignmentExpression)
            and self.name == other.name
            and self.expression == other.expression
        )

    def __str__(self):
        return f"{self.name} = {self.expression}"

    def __repr__(self):  # pragma: no cover
        return (
            f"AssignmentExpression(name='{self.name}', expression={self.expression!r})"
        )

    def evaluate(self, context: Context) -> str:
        result = self.expression.evaluate(context)
        context.assign(key=self.name, val=result)
        return ""


LoopArgument = Optional[Union[IntegerLiteral, Identifier]]


class LoopExpression(Expression):
    """Loop expression tree/object model, as returned by parse_loop_expression.

    Start, stop, limit and offset can be integer literals or identifiers
    that resolve to an integer at render time.

    `cols` is used by the built-in tag `tablerow` only. It will be ignored
    by the `for` tag.
    """

    __slots__ = (
        "name",
        "identifier",
        "start",
        "stop",
        "limit",
        "offset",
        "cols",
        "reversed",
    )

    def __init__(
        self,
        name: str,
        identifier: LoopArgument = None,
        start: LoopArgument = None,
        stop: LoopArgument = None,
        limit: LoopArgument = None,
        offset: LoopArgument = None,
        cols: LoopArgument = None,
        reversed_: bool = False,
    ):
        self.name = name
        self.identifier = identifier
        self.start = start
        self.stop = stop
        self.limit = limit
        self.offset = offset
        self.cols = cols
        self.reversed = reversed_

    def __eq__(self, other: object):
        return (
            isinstance(other, LoopExpression)
            and self.name == other.name
            and self.identifier == other.identifier
            and self.start == other.start
            and self.stop == other.stop
            and self.limit == other.limit
            and self.offset == other.offset
            and self.cols == other.cols
            and self.reversed == other.reversed
        )

    def __str__(self):
        buf = [f"{self.name} in"]

        if self.identifier:
            buf.append(str(self.identifier))
        elif self.start and self.stop:
            buf.append(f"({self.start}..{self.stop})")

        if self.limit:
            buf.append(f"limit:{self.limit}")

        if self.offset:
            buf.append(f"offset:{self.offset}")

        if self.cols:
            buf.append(f"cols:{self.cols}")

        if self.reversed:
            buf.append("reversed")

        return " ".join(buf)

    def __repr__(self):  # pragma: no cover
        return (
            f"LoopExpression(name='{self.name}', identifier={self.identifier}, "
            f"start={self.start}, stop={self.stop}, limit={self.limit}, "
            f"offset={self.offset}, cols={self.cols}, reversed={self.reversed})"
        )

    def evaluate(self, context: Context) -> Tuple[Iterator[Any], int]:
        if self.identifier:
            # An identifier that must resolve to a list or dict in the current
            # global or local namespaces.
            obj = self.identifier.evaluate(context)

            if isinstance(obj, abc.Mapping):
                length = len(obj)
                loop_iter = obj.items()
            elif isinstance(obj, abc.Sequence):
                length = len(obj)
                loop_iter = iter(obj)

            else:
                raise LiquidTypeError(
                    f"expected array or hash at '{self.identifier}', found '{str(obj)}'"
                )
        else:
            assert self.start is not None
            assert self.stop is not None

            start = self.start.evaluate(context)
            stop = self.stop.evaluate(context)

            assert isinstance(start, int)
            assert isinstance(stop, int)

            stop = stop + 1

            loop_iter = range(start, stop)
            length = stop - start

        limit = self.limit
        offset = self.offset

        if limit:
            limit = limit.evaluate(context)
            assert isinstance(limit, int)
            length = min(length, limit)

        if offset:
            offset = offset.evaluate(context)
            assert isinstance(offset, int)
            length = max(length - offset, 0)

        loop_iter = islice(loop_iter, offset, limit)

        if self.reversed:
            loop_iter = reversed(list(loop_iter))

        return loop_iter, length


Number = Union[int, float]


def eval_number_expression(left: Number, operator: str, right: Number) -> bool:
    if operator == "<=":
        return left <= right
    if operator == ">=":
        return left >= right
    if operator == "<":
        return left < right
    if operator == ">":
        return left > right

    raise LiquidTypeError(f"unknown operator {left} {operator} {right}")


def eval_empty_expression(left: Any, operator: str, right: Any) -> bool:
    if not isinstance(left, Empty):
        left, right = right, left

    if operator == "==":
        return left == right
    if operator in ("!=", "<>"):
        return left != right

    raise LiquidTypeError(f"unknown operator {left} {operator} {right}")


def is_truthy(obj: Any) -> bool:
    """Return True if the given object is Liquid truthy."""
    if obj in (False, None):
        return False
    return True


def compare(left: Any, operator: str, right: Any) -> bool:
    if isinstance(left, Empty) or isinstance(right, Empty):
        return eval_empty_expression(left, operator, right)

    if operator == "and":
        return is_truthy(left) and is_truthy(right)
    if operator == "or":
        return is_truthy(left) or is_truthy(right)
    if operator == "==":
        return left == right
    if operator in ("!=", "<>"):
        return left != right

    if operator == "contains":
        if isinstance(left, str):
            return str(right) in left
        if isinstance(left, (list, dict)):
            return right in left

    # FIXME: It appears that shopify will convert any illegal comparison into something
    # falsey, at least in lax mode.

    if None in (left, right):
        return False

    if type(left) in (int, float) and type(right) in (int, float):
        return eval_number_expression(left, operator, right)

    if type(left) != type(right):
        raise LiquidTypeError(
            f"invalid operator for types '{str(left)} {operator} {str(right)}'"
        )

    raise LiquidTypeError(f"unknown operator: {type(left)} {operator} {type(right)}")
