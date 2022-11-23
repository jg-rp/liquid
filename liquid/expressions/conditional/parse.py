"""Functions for parsing non-standard conditional expressions."""
from functools import partial

from typing import Dict
from typing import List
from typing import Iterator
from typing import Iterable
from typing import Optional

from liquid.expression import Expression
from liquid.expression import Filter
from liquid.expression import ConditionalExpression
from liquid.expression import FilteredExpression

from liquid.expressions.boolean.parse import parse_obj as parse_boolean_obj
from liquid.expressions.common import Token
from liquid.expressions.conditional.lex import tokenize
from liquid.expressions.filtered.parse import (
    parse_from_tokens as parse_standard_filtered,
)
from liquid.expressions.filtered.parse import parse_obj
from liquid.expressions.stream import TokenStream

from liquid.exceptions import LiquidSyntaxError

from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_PIPE
from liquid.token import TOKEN_DPIPE
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_IF
from liquid.token import TOKEN_ELSE


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


def _split_at_first(tokens: Iterable[Token], _type: str) -> Iterator[List[Token]]:
    buf: List[Token] = []
    for token in tokens:
        if token[1] == _type:
            yield buf
            yield list(tokens)
            return
        buf.append(token)
    yield buf
    yield []


split_at_first_pipe = partial(_split_at_first, _type=TOKEN_PIPE)
split_at_first_dpipe = partial(_split_at_first, _type=TOKEN_DPIPE)
split_at_first_if = partial(_split_at_first, _type=TOKEN_IF)
split_at_first_else = partial(_split_at_first, _type=TOKEN_ELSE)


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


def parse(expr: str, linenum: int = 1) -> FilteredExpression:
    """Parse a conditional expression string."""
    tokens = tokenize(expr, linenum)
    filtered_tokens, conditional_tokens = tuple(split_at_first_if(tokens))

    # This expression includes filters.
    _expr = parse_standard_filtered(iter(filtered_tokens), linenum)

    if not conditional_tokens:
        # A standard filtered expression
        return _expr

    conditional_tokens, filter_tokens = tuple(
        split_at_first_dpipe(iter(conditional_tokens))
    )
    conditional_tokens, alternative_tokens = tuple(
        split_at_first_else(iter(conditional_tokens))
    )

    # Note: Might need to define `parse_boolean_obj` here if they diverge.
    condition = parse_boolean_obj(TokenStream(iter(conditional_tokens)), linenum)
    alternative: Optional[Expression] = None

    if alternative_tokens:
        alternative_tokens, alternative_filter_tokens = tuple(
            split_at_first_pipe(iter(alternative_tokens))
        )

        alternative_left = parse_obj(TokenStream(iter(alternative_tokens)))
        alternative_filters = [
            _parse_filter(_tokens, linenum)
            for _tokens in split_at_pipe(alternative_filter_tokens)
        ]

        alternative = FilteredExpression(alternative_left, alternative_filters)

    tail_filters = [
        _parse_filter(_tokens, linenum)
        for _tokens in split_at_pipe(iter(filter_tokens))
    ]

    return ConditionalExpression(_expr, tail_filters, condition, alternative)


# TODO: parse_with_parens
