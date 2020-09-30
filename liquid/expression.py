"""Tag and output statement expression objects."""

from __future__ import annotations
from abc import ABC, abstractmethod
from itertools import islice
from typing import Union, List, Optional, Any, Iterator

from liquid.context import Context
from liquid.token import Token
from liquid.exceptions import LiquidTypeError, Error

Number = Union[int, float]


class Expression(ABC):
    __slots__ = ("tok",)

    expression_statement = True

    def __init__(self, tok: Token):
        self.tok = tok

    @abstractmethod
    def evaluate(self, context: Context) -> Any:
        """Evaluate the expression with the given context."""

    def token(self):
        return self.tok


class Boolean(Expression):
    __slots__ = ("tok", "value")

    def __init__(self, tok: Token, value: bool):
        super().__init__(tok)
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Boolean), self.value == other.value

    def __repr__(self):  # pragma: no cover
        return f"Boolean(tok={self.tok}, value={self.value})"

    def __str__(self):
        return str(self.value)

    def evaluate(self, context: Context) -> bool:
        return self.value


class Nil(Expression):
    __slots__ = ("tok",)

    def __eq__(self, other):
        return isinstance(other, Nil)

    def __repr__(self):  # pragma: no cover
        return f"Nil(tok={self.tok})"

    def __str__(self):  # pragma: no cover
        return "nil"

    def evaluate(self, context: Context) -> None:
        return None


class Empty(Expression):
    __slots__ = ("tok",)

    def __eq__(self, other):
        if isinstance(other, Empty):
            return True
        if isinstance(other, (list, dict, str)) and not other:
            return True
        return False

    def __repr__(self):  # pragma: no cover
        return f"Empty(tok={self.tok})"

    def __str__(self):  # pragma: no cover
        return "empty"

    def evaluate(self, context: Context) -> Empty:
        return self


class Literal(Expression):
    __slots__ = ("tok", "value")

    def __init__(self, tok: Token, value: Any):
        super().__init__(tok)
        self.value = value

    def __str__(self):
        return repr(self.value)

    def evaluate(self, context: Context) -> Any:
        return self.value


class StringLiteral(Literal):
    __slots__ = ()

    def __eq__(self, other):
        return isinstance(other, StringLiteral) and self.value == other.value

    def __repr__(self):  # pragma: no cover
        return f"StringLiteral(tok={self.tok}, value='{self.value}')"


class IntegerLiteral(Literal):
    __slots__ = ()

    def __eq__(self, other):
        return isinstance(other, IntegerLiteral) and self.value == other.value

    def __repr__(self):  # pragma: no cover
        return f"IntegerLiteral(tok={self.tok}, value={self.value})"


class FloatLiteral(Literal):
    __slots__ = ()

    def __eq__(self, other):
        return isinstance(other, FloatLiteral) and self.value == other.value

    def __repr__(self):  # pragma: no cover
        return f"FloatLiteral(tok={self.tok}, value={self.value})"


class IdentifierPathElement(Literal):
    __slots__ = ()

    def __eq__(self, other):
        return isinstance(other, IdentifierPathElement) and self.value == other.value

    def __repr__(self):  # pragma: no cover
        return f"IdentifierPathElement(tok={self.tok}, value={self.value})"

    def __str__(self):
        return str(self.value)


IdentifierPath = List[Union[IdentifierPathElement, "Identifier"]]


class Identifier(Expression):
    __slots__ = ("tok", "path")

    def __init__(self, tok: Token, path: IdentifierPath = None):
        super().__init__(tok)
        self.path = path or []

    def __eq__(self, other):
        return isinstance(other, Identifier) and self.path == other.path

    def __repr__(self):  # pragma: no cover
        return f"Identifier(tok={self.tok}, path={self.path})"

    def __str__(self):
        return ".".join(str(elem) for elem in self.path)

    def __hash__(self):
        return hash(str(self))

    def evaluate(self, context: Context) -> Any:
        path: List[Any] = [elem.evaluate(context) for elem in self.path]
        return context.get(path)


class PrefixExpression(Expression):
    __slots__ = ("tok", "operator", "right")

    def __init__(self, tok: Token, operator: str, right: Expression = None):
        super().__init__(tok)
        self.operator = operator
        self.right = right

    def __eq__(self, other):
        return (
            isinstance(other, PrefixExpression)
            and self.operator == other.operator
            and self.right == other.right
        )

    def __repr__(self):  # pragma: no cover
        return f"PrefixExpression(tok={self.tok}, operator='{self.operator}', right={self.right!r})"

    def __str__(self):
        return f"({self.operator}{self.right})"

    def evaluate(self, context: Context):
        right = self.right.evaluate(context)

        if self.operator == "-":
            if isinstance(right, (int, float)):
                return -right
            raise LiquidTypeError(
                f"unknown operator {self.operator}{self.right.tok.type}"
            )

        raise LiquidTypeError(f"unknown operator {self.operator}")


class InfixExpression(Expression):
    __slots__ = ("tok", "left", "operator", "right")

    def __init__(
        self, tok: Token, left: Expression, operator: str, right: Expression = None
    ):
        super().__init__(tok)
        self.left = left
        self.operator = operator
        self.right = right

    def __eq__(self, other):
        return (
            isinstance(other, InfixExpression)
            and self.left == other.left
            and self.operator == other.operator
            and self.right == other.right
        )

    def __repr__(self):  # pragma: no cover
        return (
            f"InfixExpression(tok={self.tok}, left={self.left!r}, "
            f"operator='{self.operator}', right={self.right!r})"
        )

    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"

    def evaluate(self, context: Context):
        left = self.left.evaluate(context)
        right = self.right.evaluate(context)
        return compare(left, self.operator, right)


class Filter:
    __slots__ = ("name", "args")

    def __init__(self, name: str, args: List[Expression]):
        self.name = name
        self.args = args

    def __eq__(self, other):
        return self.name == other.name and self.args == other.args

    def __repr__(self):  # pragma: no cover
        return f"Filter(name='{self.name}', args={self.args})"

    def __str__(self):
        args_str = ", ".join([str(arg) for arg in self.args])
        if args_str:
            return f"{self.name}: {args_str})"
        return f"{self.name}"

    def evaluate_args(self, context: Context):
        return [arg.evaluate(context) for arg in self.args]


class BooleanExpression(Expression):
    __slots__ = ("expression",)

    def __init__(self, tok: Token, expression: Expression):
        super().__init__(tok)
        self.expression = expression

    def __eq__(self, other):
        return self.expression == other.expression

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

    def __init__(self, expression: Expression, filters: List[Filter] = None):
        self.expression = expression
        self.filters = filters or []

    def __eq__(self, other):
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
        return f"FilteredExpression(expression={self.expression!r}, filters={self.filters})"

    def evaluate(self, context: Context) -> str:
        result = self.expression.evaluate(context)

        for fltr in self.filters:
            func = context.filter(fltr.name)
            try:
                result = func(result, *fltr.evaluate_args(context))
            except Exception as err:
                # Any exception causes us to abort the filter chain and discard the result.
                # Nothing will be rendered.
                if not issubclass(type(err), Error):
                    raise Error(
                        f"filter '{fltr.name}': unexpected error: {err}"
                    ) from err
                raise

        return result


class AssignmentExpression(Expression):
    __slots__ = ("name", "expression")

    def __init__(self, tok: Token, name: Identifier, expression: Expression = None):
        super().__init__(tok)
        self.name = name
        self.expression = expression

    def __eq__(self, other):
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
        # XXX:
        assert len(self.name.path) == 1
        name = self.name.path[0].evaluate(context)
        assert isinstance(name, str)
        result = self.expression.evaluate(context)
        context.assign(key=name, val=result)
        return ""


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
        identifier: Optional[Identifier] = None,
        start: Optional[Union[IntegerLiteral, Identifier]] = None,
        stop: Optional[Union[IntegerLiteral, Identifier]] = None,
        limit: Optional[Union[IntegerLiteral, Identifier]] = None,
        offset: Optional[Union[IntegerLiteral, Identifier]] = None,
        cols: Optional[Union[IntegerLiteral, Identifier]] = None,
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

    def __eq__(self, other):
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

    def evaluate(self, context: Context) -> Iterator[Any]:
        if self.identifier:
            # An identifier that must resolve to a list or dict in the current
            # global or local namespaces.
            obj = self.identifier.evaluate(context)
            if isinstance(obj, dict):
                loop_iter = obj.items()
            elif isinstance(obj, list):
                loop_iter = iter(obj)
            else:
                raise LiquidTypeError(
                    f"expected array or hash at '{self.identifier}', found '{str(obj)}'"
                )
        else:
            assert self.start is not None
            assert self.stop is not None
            loop_iter = range(
                self.start.evaluate(context), self.stop.evaluate(context) + 1
            )

        limit = self.limit
        offset = self.offset

        if limit:
            limit = limit.evaluate(context)

        if offset:
            offset = offset.evaluate(context)

        loop_iter = islice(loop_iter, offset, limit)

        if self.reversed:
            loop_iter = reversed(list(loop_iter))

        return loop_iter


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

    if type(left) in (int, float) and type(right) in (int, float):
        return eval_number_expression(left, operator, right)

    if type(left) != type(right):
        raise LiquidTypeError(
            f"invalid operator for types '{str(left)} {operator} {str(right)}'"
        )

    raise LiquidTypeError(f"unknown operator: {type(left)} {operator} {type(right)}")
