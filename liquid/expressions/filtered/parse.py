"""Functions for parsing filtered expressions. Like those found in output statements and
assign tags.
"""
from itertools import islice

from typing import Dict
from typing import List
from typing import Iterator
from typing import Iterable
from typing import Tuple

from liquid.expression import Expression
from liquid.expression import Filter
from liquid.expression import FilteredExpression

from liquid.expressions.common import Token
from liquid.expressions.common import parse_blank
from liquid.expressions.common import parse_boolean
from liquid.expressions.common import parse_empty
from liquid.expressions.common import parse_float_literal
from liquid.expressions.common import parse_identifier
from liquid.expressions.common import parse_integer_literal
from liquid.expressions.common import parse_nil
from liquid.expressions.common import parse_string_literal
from liquid.expressions.common import make_parse_range

from liquid.expressions.filtered.lex import tokenize
from liquid.expressions.stream import TokenStream

from liquid.exceptions import LiquidSyntaxError

from liquid.token import TOKEN_BLANK
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_EMPTY
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_NULL
from liquid.token import TOKEN_PIPE
from liquid.token import TOKEN_RANGE_LITERAL
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_TRUE


TOKEN_MAP = {
    TOKEN_FALSE: parse_boolean,
    TOKEN_TRUE: parse_boolean,
    TOKEN_NIL: parse_nil,
    TOKEN_NULL: parse_nil,
    TOKEN_EMPTY: parse_empty,
    TOKEN_BLANK: parse_blank,
    TOKEN_STRING: parse_string_literal,
    TOKEN_INTEGER: parse_integer_literal,
    TOKEN_FLOAT: parse_float_literal,
    TOKEN_IDENTIFIER: parse_identifier,
    TOKEN_LBRACKET: parse_identifier,
}


def parse_obj(stream: TokenStream) -> Expression:
    """Parse an object from the stream of tokens.

    An object could be a constant, like `true` or `nil`, a range literal or an
    identifier. An identifier could be chained, possibly with nested identifiers
    between square brackets.
    """
    try:
        return TOKEN_MAP[stream.current[1]](stream)
    except KeyError as err:
        raise LiquidSyntaxError(
            f"unexpected {stream.current[2]!r}", linenum=stream.current[0]
        ) from err


parse_range = make_parse_range(parse_obj)


def parse_range_with_parens(stream: TokenStream) -> Expression:
    """Like `parse_range` but consumes the extra `RANGE_LPAREN` token first."""
    stream.expect(TOKEN_RANGE_LITERAL)
    next(stream)  # Eat extra token
    return parse_range(stream)


TOKEN_MAP[TOKEN_LPAREN] = parse_range
TOKEN_MAP[TOKEN_RANGE_LITERAL] = parse_range_with_parens


def split_at_pipe(tokens: Iterable[Token]) -> Iterator[List[Token]]:
    """Split tokens on into lists, using TOKEN_PIPE as the delimiter."""
    buf: List[Token] = []
    for token in tokens:
        if token[1] == TOKEN_PIPE:
            yield buf
            buf = []
        else:
            buf.append(token)
    yield buf


def split_at_first_pipe(tokens: Iterable[Token]) -> Iterator[List[Token]]:
    """Like split_at_pipe, but stops splitting after the first TOKEN_PIPE is found."""
    buf: List[Token] = []
    for token in tokens:
        if token[1] == TOKEN_PIPE:
            yield buf
            yield list(tokens)
            return
        buf.append(token)
    yield buf


def split_at_comma(
    tokens: Iterable[Token],
) -> Iterator[List[Token]]:  # pragma: no cover
    """Split tokens into lists, using TOKEN_COMMA as the delimiter."""
    buf: List[Token] = []
    for token in tokens:
        if token[1] == TOKEN_COMMA:
            yield buf
            buf = []
        else:
            buf.append(token)
    yield buf


def bucket_args(
    arguments: Iterable[Tuple[str, Expression]]
) -> Tuple[List[Expression], Dict[str, Expression]]:  # pragma: no cover
    """Split filter arguments into positional and keyword arguments."""
    args = []
    kwargs = {}
    for name, expr in arguments:
        if not name:
            args.append(expr)
        else:
            kwargs[name] = expr
    return args, kwargs


def parse_filter(tokens: List[Token], linenum: int = 1) -> Filter:  # pragma: no cover
    """Parse a Liquid filter from a list of tokens."""
    if not tokens:
        raise LiquidSyntaxError(
            "unexpected pipe or missing filter name", linenum=linenum
        )

    name = tokens[0][2]

    if len(tokens) > 1:
        if tokens[1][1] != TOKEN_COLON:
            raise LiquidSyntaxError(
                f"expected a colon after {name!r}",
                linenum=tokens[1][0],
            )
        return Filter(name, *bucket_args(parse_args(islice(tokens, 2, None))))
    return Filter(name, [])


def parse_args(
    tokens: Iterator[Token],
) -> Iterator[Tuple[str, Expression]]:  # pragma: no cover
    """Parse a filter's arguments from the given token iterator."""
    for arg_tokens in split_at_comma(tokens):
        yield parse_arg(arg_tokens)


def parse_arg(tokens: List[Token]) -> Tuple[str, Expression]:  # pragma: no cover
    """Parse a single argument from a list of tokens."""
    if len(tokens) > 1 and tokens[1][1] == TOKEN_COLON:
        # A named/keyword parameter/argument
        return tokens[0][2], parse_obj(TokenStream(islice(tokens, 2, None)))
    return "", parse_obj(TokenStream(iter(tokens)))


# _parse_filter has replaced the parse_* functions above in the name of better syntax
# error handling. On the off chance someone is using them, the parse_* functions will
# be depreciated as we approach Python Liquid version 2 and then removed.


def _parse_filter(tokens: List[Token], linenum: int) -> Filter:
    if not tokens:
        raise LiquidSyntaxError(
            "unexpected pipe or missing filter name", linenum=linenum
        )

    stream = TokenStream(iter(tokens))
    stream.expect(TOKEN_IDENTIFIER)
    name = stream.current[2]

    next(stream)
    # Shortcut for filters with no arguments.
    if stream.current[1] == TOKEN_EOF:
        return Filter(name, [])

    # Eat colon
    stream.expect(TOKEN_COLON)
    next(stream)

    args: List[Expression] = []
    kwargs: Dict[str, Expression] = {}

    while stream.current[1] != TOKEN_EOF:
        if stream.peek[1] == TOKEN_COLON:
            # A keyword argument
            stream.expect(TOKEN_IDENTIFIER)
            key = next(stream)[2]
            # Eat colon
            next(stream)
            kwargs[key] = parse_obj(stream)
        else:
            # A positional argument
            args.append(parse_obj(stream))

        # Eat comma
        next(stream)
        if stream.current[1] != TOKEN_EOF:
            stream.expect(TOKEN_COMMA)
            next(stream)

    return Filter(name, args, kwargs)


def parse_from_tokens(tokens: Iterator[Token], linenum: int = 1) -> FilteredExpression:
    """Parse an expression with zero or more filters from a token iterator."""
    parts = tuple(split_at_first_pipe(tokens))
    stream = TokenStream(iter(parts[0]))
    left = parse_obj(stream)

    if stream.peek[1] != TOKEN_EOF:
        raise LiquidSyntaxError(
            f"expected a filter or end of expression, found {stream.peek[2]!r}",
            linenum=stream.current[0],
        )

    if len(parts) == 1:
        return FilteredExpression(left)

    filters = [_parse_filter(_tokens, linenum) for _tokens in split_at_pipe(parts[1])]
    return FilteredExpression(left, filters)


def parse(expr: str, linenum: int = 1) -> FilteredExpression:
    """Parse an expression string with zero or more filters."""
    return parse_from_tokens(tokenize(expr, linenum))
