"""Functions for parsing loop expressions. Like those found in `for` and `tablerow`
tags."""
from typing import Callable
from typing import Dict
from typing import Tuple

from liquid.limits import to_int

from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COLS
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_CONTINUE
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_IN
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_LIMIT
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_OFFSET
from liquid.token import TOKEN_REVERSED
from liquid.token import TOKEN_STRING

from liquid.expression import Continue
from liquid.expression import CONTINUE
from liquid.expression import IntegerLiteral
from liquid.expression import LoopArgument
from liquid.expression import LoopExpression
from liquid.expression import LoopIterable

from liquid.expressions.common import make_parse_range
from liquid.expressions.common import parse_float_literal
from liquid.expressions.common import parse_identifier
from liquid.expressions.common import parse_integer_literal
from liquid.expressions.common import parse_string_literal

from liquid.expressions.filtered.parse import parse_obj as parse_simple_obj
from liquid.expressions.stream import TokenStream
from liquid.expressions.loop.lex import tokenize

from liquid.exceptions import LiquidSyntaxError

LOOP_ARGS = frozenset(
    (
        TOKEN_LIMIT,
        TOKEN_OFFSET,
        TOKEN_COLS,
    )
)

parse_range = make_parse_range(parse_simple_obj)


def parse_continue(_: TokenStream) -> Continue:
    """Parse the special `continue` value for the `offset` argument."""
    return CONTINUE


def parse_string_argument(stream: TokenStream) -> LoopArgument:
    """Try to parse a string literal as an integer."""
    try:
        return IntegerLiteral(to_int(stream.current[2]))
    except ValueError as err:
        raise LiquidSyntaxError(
            f"invalid integer argument {stream.current[2]!r}"
        ) from err


TOKEN_MAP: Dict[str, Callable[[TokenStream], LoopArgument]] = {
    TOKEN_IDENTIFIER: parse_identifier,
    TOKEN_LBRACKET: parse_identifier,
    TOKEN_INTEGER: parse_integer_literal,
    TOKEN_FLOAT: parse_float_literal,
    TOKEN_CONTINUE: parse_continue,
    TOKEN_STRING: parse_string_argument,
}


def parse_loop_argument(stream: TokenStream) -> LoopArgument:
    """Parse a object from the stream of tokens as a loop argument."""
    try:
        return TOKEN_MAP[stream.current[1]](stream)
    except KeyError as err:
        raise LiquidSyntaxError(f"unexpected {stream.current[2]!r}") from err


def parse_loop_arguments(stream: TokenStream) -> Tuple[Dict[str, LoopArgument], bool]:
    """Parse zero or more arguments from the stream of tokens until the end of the
    stream."""
    arguments: Dict[str, LoopArgument] = {}
    _reversed = False

    while True:
        _, typ, val = stream.current
        if typ == TOKEN_EOF:
            break

        if typ in LOOP_ARGS:
            next(stream)
            stream.expect(TOKEN_COLON)
            next(stream)
            arguments[val] = parse_loop_argument(stream)
            next(stream)
        elif typ == TOKEN_REVERSED:
            next(stream)
            _reversed = True
        elif typ == TOKEN_COMMA:
            next(stream)
        else:
            raise LiquidSyntaxError(f"unexpected {val!r}")

    return arguments, _reversed


def parse(expr: str, linenum: int = 1) -> LoopExpression:
    """Parse a loop expression string."""
    stream = TokenStream(tokenize(expr, linenum))
    stream.expect(TOKEN_IDENTIFIER)
    name = next(stream)[2]

    # Eat TOKEN_IN
    stream.expect(TOKEN_IN)
    next(stream)

    if stream.current[1] == TOKEN_IDENTIFIER:
        expression: LoopIterable = parse_identifier(stream)
        next(stream)
    elif stream.current[1] == TOKEN_STRING:
        expression = parse_string_literal(stream)
        next(stream)
    elif stream.current[1] == TOKEN_LPAREN:
        expression = parse_range(stream)
        next(stream)
    else:
        raise LiquidSyntaxError("invalid loop expression", linenum=stream.current[0])

    args, reversed_ = parse_loop_arguments(stream)
    return LoopExpression(name=name, iterable=expression, reversed_=reversed_, **args)
