"""Functions for parsing boolean expressions. Like those found in `if` and
unless` tags.
"""
from typing import Dict
from typing import Callable

from liquid.expression import Expression
from liquid.expression import BooleanExpression
from liquid.expression import InfixExpression
from liquid.expression import PrefixExpression

from liquid.expressions.common import make_parse_range
from liquid.expressions.common import parse_blank
from liquid.expressions.common import parse_boolean
from liquid.expressions.common import parse_empty
from liquid.expressions.common import parse_float_literal
from liquid.expressions.common import parse_identifier
from liquid.expressions.common import parse_integer_literal
from liquid.expressions.common import parse_nil
from liquid.expressions.common import parse_string_literal

from liquid.expressions.filtered.parse import parse_obj as parse_simple_obj
from liquid.expressions.boolean.lex import tokenize
from liquid.expressions.boolean.lex import tokenize_with_parens
from liquid.expressions.stream import TokenStream

from liquid.exceptions import LiquidSyntaxError

from liquid.token import TOKEN_BLANK
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
from liquid.token import TOKEN_RANGE_LITERAL
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_TRUE

from liquid.token import TOKEN_AND
from liquid.token import TOKEN_CONTAINS
from liquid.token import TOKEN_EQ
from liquid.token import TOKEN_GE
from liquid.token import TOKEN_GT
from liquid.token import TOKEN_LE
from liquid.token import TOKEN_LG
from liquid.token import TOKEN_LT
from liquid.token import TOKEN_NE
from liquid.token import TOKEN_NOT
from liquid.token import TOKEN_OR

# Note that PREFIX and LOGICAL are not used in any "standard" expressions.
PRECEDENCE_LOWEST = 1
PRECEDENCE_LOGICALRIGHT = 3
PRECEDENCE_LOGICAL = 4
PRECEDENCE_RELATIONAL = 5
PRECEDENCE_MEMBERSHIP = 6
PRECEDENCE_PREFIX = 7

PRECEDENCES = {
    TOKEN_IDENTIFIER: PRECEDENCE_LOWEST,
    TOKEN_EQ: PRECEDENCE_RELATIONAL,
    TOKEN_LT: PRECEDENCE_RELATIONAL,
    TOKEN_GT: PRECEDENCE_RELATIONAL,
    TOKEN_NE: PRECEDENCE_RELATIONAL,
    TOKEN_LG: PRECEDENCE_RELATIONAL,
    TOKEN_LE: PRECEDENCE_RELATIONAL,
    TOKEN_GE: PRECEDENCE_RELATIONAL,
    TOKEN_CONTAINS: PRECEDENCE_MEMBERSHIP,
    TOKEN_AND: PRECEDENCE_LOGICALRIGHT,
    TOKEN_OR: PRECEDENCE_LOGICALRIGHT,
    TOKEN_NOT: PRECEDENCE_LOGICALRIGHT,
    TOKEN_RPAREN: PRECEDENCE_LOWEST,
}


TOKEN_MAP: Dict[str, Callable[[TokenStream], Expression]] = {
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

BINARY_OPERATORS = frozenset(
    (
        TOKEN_EQ,
        TOKEN_OR,
        TOKEN_AND,
        TOKEN_LT,
        TOKEN_GT,
        TOKEN_NE,
        TOKEN_LG,
        TOKEN_LE,
        TOKEN_GE,
        TOKEN_CONTAINS,
    )
)

PREFIX_OPERATORS = frozenset(
    [
        TOKEN_NOT,
    ]
)


def parse_prefix_expression(stream: TokenStream) -> Expression:
    """Parse a prefix expression from a stream of tokens.

    Note that "standard" Liquid boolean expressions do not have any prefix expressions.
    """
    tok = next(stream)
    assert tok[2] == TOKEN_NOT
    return PrefixExpression(
        operator=tok[2],
        right=parse_obj_with_parens(
            stream,
            precedence=PRECEDENCE_LOGICALRIGHT,
        ),
    )


def parse_infix_expression(stream: TokenStream, left: Expression) -> InfixExpression:
    """Parse an infix expression from a stream of tokens."""
    tok = stream.current
    precedence = PRECEDENCES.get(tok[1], PRECEDENCE_LOWEST)
    stream.next_token()

    exp = InfixExpression(
        left=left,
        operator=tok[2],
        right=parse_obj(stream, precedence),
    )
    return exp


def parse_infix_expression_with_parens(
    stream: TokenStream,
    left: Expression,
) -> InfixExpression:
    """Parse an infix expression from a stream of tokens."""
    tok = next(stream)
    precedence = PRECEDENCES.get(tok[1], PRECEDENCE_LOWEST)
    return InfixExpression(
        left=left,
        operator=tok[2],
        right=parse_obj_with_parens(stream, precedence),
    )


def parse_obj(
    stream: TokenStream,
    precedence: int = PRECEDENCE_LOWEST,
) -> Expression:
    """Parse the next object from the stream of tokens.

    This object parser is for "standard" boolean expressions. It does not
    handle logical `not` or grouping with parentheses.
    """
    try:
        left = TOKEN_MAP[stream.current[1]](stream)
    except KeyError as err:
        raise LiquidSyntaxError(
            f"unexpected {stream.current[2]!r}",
            linenum=stream.current[0],
        ) from err

    while True:
        peek_typ = stream.peek[1]
        if (
            peek_typ == TOKEN_EOF
            or PRECEDENCES.get(peek_typ, PRECEDENCE_LOWEST) < precedence
        ):
            break

        if peek_typ not in BINARY_OPERATORS:
            return left

        next(stream)
        left = parse_infix_expression(stream, left)

    return left


parse_range = make_parse_range(parse_simple_obj)
TOKEN_MAP[TOKEN_LPAREN] = parse_range


def parse(expr: str, linenum: int = 1) -> BooleanExpression:
    """Parse a string as a "standard" boolean expression."""
    return BooleanExpression(parse_obj(TokenStream(tokenize(expr, linenum))))


def parse_grouped_expression(stream: TokenStream) -> Expression:
    """Parse a group of logical expressions."""
    next(stream)  # Eat left paren
    expr = parse_obj_with_parens(stream)
    next(stream)

    while stream.current[1] != TOKEN_RPAREN:
        if stream.current[1] == TOKEN_EOF:
            raise LiquidSyntaxError("unbalanced parentheses", linenum=stream.current[0])
        expr = parse_infix_expression_with_parens(stream, left=expr)

    stream.expect(TOKEN_RPAREN)
    return expr


def parse_range_with_parens(stream: TokenStream) -> Expression:
    """Like `parse_range` but consumes the extra `RANGE_LPAREN` token first."""
    stream.expect(TOKEN_RANGE_LITERAL)
    next(stream)  # Eat extra token
    return parse_range(stream)


TOKEN_MAP_WITH_PARENS = {
    **TOKEN_MAP,
    TOKEN_NOT: parse_prefix_expression,
    TOKEN_LPAREN: parse_grouped_expression,
    TOKEN_RANGE_LITERAL: parse_range_with_parens,
}


def parse_obj_with_parens(
    stream: TokenStream,
    precedence: int = PRECEDENCE_LOWEST,
) -> Expression:
    """Parse the next object from the stream of tokens.

    This object parser is for the non-standard boolean expression, which does handle
    the logical `not` operator and grouping terms with parentheses.
    """
    try:
        left = TOKEN_MAP_WITH_PARENS[stream.current[1]](stream)
    except KeyError as err:
        if stream.current[1] == TOKEN_EOF:
            msg = "end of expression"
        else:
            msg = repr(stream.current[2])
        raise LiquidSyntaxError(
            f"unexpected {msg}",
            linenum=stream.current[0],
        ) from err

    while True:
        peek_typ = stream.peek[1]
        if (
            peek_typ == TOKEN_EOF
            or PRECEDENCES.get(peek_typ, PRECEDENCE_LOWEST) < precedence
        ):
            break

        if peek_typ not in BINARY_OPERATORS:
            return left

        next(stream)
        left = parse_infix_expression_with_parens(stream, left)

    return left


def parse_with_parens(expr: str, linenum: int = 1) -> BooleanExpression:
    """Parse a string as a boolean expression, possibly containing the logical `not`
    operator and parentheses for grouping terms.
    """
    stream = TokenStream(tokenize_with_parens(expr, linenum))
    rv = BooleanExpression(parse_obj_with_parens(stream))
    peek_typ = stream.peek[1]
    if peek_typ == TOKEN_RPAREN:
        raise LiquidSyntaxError("unmatched ')'", linenum=stream.peek[0])
    if peek_typ != TOKEN_EOF:
        raise LiquidSyntaxError(
            f"unexpected {stream.peek[2]!r}", linenum=stream.peek[0]
        )
    return rv
