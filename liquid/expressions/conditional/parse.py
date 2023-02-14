"""Functions for parsing non-standard conditional expressions."""
from functools import partial

from typing import Dict
from typing import List
from typing import Iterator
from typing import Iterable
from typing import Optional
from typing import Tuple

from liquid.expression import Expression
from liquid.expression import FALSE
from liquid.expression import Filter
from liquid.expression import ConditionalExpression
from liquid.expression import FilteredExpression

from liquid.expressions.boolean.parse import parse_obj as parse_boolean_obj
from liquid.expressions.boolean.parse import (
    parse_obj_with_parens as parse_boolean_obj_with_parens,
)
from liquid.expressions.common import Token
from liquid.expressions.conditional.lex import tokenize
from liquid.expressions.conditional.lex import tokenize_with_parens
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
    """Split tokens into lists, using TOKEN_PIPE as the delimiter."""
    buf: List[Token] = []
    for token in tokens:
        if token[1] == TOKEN_PIPE:
            yield buf
            buf = []
        else:
            buf.append(token)
    yield buf


def _split_at_first(
    tokens: Iterator[Token],
    _type: str,
) -> Tuple[List[Token], Optional[Iterator[Token]]]:
    buf: List[Token] = []
    for token in tokens:
        if token[1] == _type:
            return (buf, tokens)
        buf.append(token)
    return (buf, None)


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
    standard_tokens, _conditional_tokens = split_at_first_if(tokens)

    # This expression includes filters.
    _expr = parse_standard_filtered(iter(standard_tokens), linenum)

    if not _conditional_tokens:
        # A standard filtered expression
        return _expr

    conditional_tokens, _filter_tokens = split_at_first_dpipe(_conditional_tokens)
    conditional_tokens, _alternative_tokens = split_at_first_else(
        iter(conditional_tokens)
    )

    if conditional_tokens:
        condition = parse_boolean_obj(TokenStream(iter(conditional_tokens)), linenum)

    else:
        # A missing condition (an `if` with nothing after it).
        condition = FALSE

    if _alternative_tokens:
        # Handle TOKEN_ELSE followed by nothing.
        alternative_tokens: List[Token] = list(_alternative_tokens)

        if alternative_tokens:
            alternative: Optional[Expression] = parse_standard_filtered(
                iter(alternative_tokens), linenum
            )
        else:
            alternative = None
    else:
        alternative = None

    if _filter_tokens:
        tail_filters = [
            _parse_filter(_tokens, linenum)
            for _tokens in split_at_pipe(iter(_filter_tokens))
        ]
    else:
        tail_filters = []

    return ConditionalExpression(_expr, tail_filters, condition, alternative)


def parse_with_parens(expr: str, linenum: int = 1) -> FilteredExpression:
    """Parse a conditional expression string that supports logical `not` and
    grouping terms with parentheses."""
    tokens = tokenize_with_parens(expr, linenum)
    standard_tokens, _conditional_tokens = split_at_first_if(tokens)

    # This expression includes filters.
    _expr = parse_standard_filtered(iter(standard_tokens), linenum)

    if not _conditional_tokens:
        # A standard filtered expression
        return _expr

    conditional_tokens, _filter_tokens = split_at_first_dpipe(_conditional_tokens)
    conditional_tokens, _alternative_tokens = split_at_first_else(
        iter(conditional_tokens)
    )

    if conditional_tokens:
        condition = parse_boolean_obj_with_parens(
            TokenStream(iter(conditional_tokens)), linenum
        )
    else:
        # A missing condition (an `if` with nothing after it).
        condition = FALSE

    if _alternative_tokens:
        # Handle TOKEN_ELSE followed by nothing.
        alternative_tokens: List[Token] = list(_alternative_tokens)

        if alternative_tokens:
            alternative: Optional[Expression] = parse_standard_filtered(
                iter(alternative_tokens), linenum
            )
        else:
            alternative = None
    else:
        alternative = None

    if _filter_tokens:
        tail_filters = [
            _parse_filter(_tokens, linenum)
            for _tokens in split_at_pipe(iter(_filter_tokens))
        ]
    else:
        tail_filters = []

    return ConditionalExpression(_expr, tail_filters, condition, alternative)
