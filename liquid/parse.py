"""Liquid template parser."""

from collections import namedtuple
from enum import IntEnum, auto
from functools import lru_cache
from typing import Tuple, List, Union

from liquid.exceptions import LiquidSyntaxError, Error
from liquid import expression
from liquid.token import (
    TOKEN_EOF,
    TOKEN_IDENTIFIER,
    TOKEN_INTEGER,
    TOKEN_DOT,
    TOKEN_LBRACKET,
    TOKEN_LITERAL,
    TOKEN_STRING,
    TOKEN_EQ,
    TOKEN_LT,
    TOKEN_GT,
    TOKEN_NE,
    TOKEN_LG,
    TOKEN_LE,
    TOKEN_GE,
    TOKEN_CONTAINS,
    TOKEN_AND,
    TOKEN_OR,
    TOKEN_PIPE,
    TOKEN_TRUE,
    TOKEN_FALSE,
    TOKEN_COMMA,
    TOKEN_COLON,
    TOKEN_LIMIT,
    TOKEN_OFFSET,
    TOKEN_COLS,
    TOKEN_RBRACKET,
    TOKEN_NIL,
    TOKEN_EMPTY,
    TOKEN_NEGATIVE,
    TOKEN_FLOAT,
    TOKEN_REVERSED,
    TOKEN_ASSIGN,
    TOKEN_IN,
    TOKEN_RANGE,
    TOKEN_LPAREN,
    TOKEN_RPAREN,
    Token,
    TOKEN_STATEMENT,
    TOKEN_TAG_NAME,
    TOKEN_ILLEGAL,
    reverse_operators,
)
from liquid import ast
from liquid.lex import TokenStream


class Parser:
    __slots__ = ("env", "illegal", "literal", "statement")

    def __init__(self, env):
        self.env = env
        self.illegal = self.env.tags[TOKEN_ILLEGAL]
        self.literal = self.env.tags[TOKEN_LITERAL]
        self.statement = self.env.tags[TOKEN_STATEMENT]

    def parse(self, stream: TokenStream) -> ast.ParseTree:
        root = ast.ParseTree()

        while stream.current.type != TOKEN_EOF:
            try:
                if node := self.parse_statement(stream):
                    root.statements.append(node)
            except Error as err:
                self.env.error(err, linenum=stream.current.linenum)

            stream.next_token()

        return root

    def parse_statement(self, stream) -> ast.Node:
        """"""

        if stream.current.test(TOKEN_STATEMENT):
            node = self.statement.get_node(stream)
        elif stream.current.test(TOKEN_TAG_NAME):
            tag = self.env.tags.get(stream.current.value, self.illegal)

            if tag.block:
                stream.balancing_stack.append(tag)

            node = tag.get_node(stream)

            # Tag parse functions can choose to return an IllegalNode.
            if node.__class__ == "IllegalNode":
                raise LiquidSyntaxError(
                    f"unexpected tag '{node.tok.value}'", linenum=node.tok.linenum
                )

            if tag.block:
                popped = stream.balancing_stack.pop()
                if stream.current.value != popped.end:
                    raise LiquidSyntaxError(
                        f"expected {popped.end}, found {stream.current.value}",
                        linenum=stream.current.linenum,
                    )
        else:
            expect(stream, TOKEN_LITERAL)
            node = self.literal.get_node(stream)

        return node

    def parse_block(self, stream, end: Tuple[str, ...]) -> ast.BlockNode:
        block = ast.BlockNode(stream.current)

        while stream.current.type != TOKEN_EOF:
            if stream.current.type == TOKEN_TAG_NAME and stream.current.value in end:
                break
            stmt = self.parse_statement(stream)
            if stmt:
                block.statements.append(stmt)
            stream.next_token()

        return block


def _expect(tok: Token, typ: str, value: str = None) -> None:
    if tok.type != typ or (value is not None and tok.value != value):
        _typ = reverse_operators.get(tok.type, tok.type)
        _expected_typ = reverse_operators.get(typ, typ)
        if value is not None:
            msg = f"expected {_expected_typ} with value '{value}', found {_typ} with value '{tok.value}'"
        else:
            msg = f"expected '{_expected_typ}', found '{_typ}'"
        raise LiquidSyntaxError(msg, linenum=tok.linenum)


def expect(stream: TokenStream, typ: str, value: str = None) -> None:
    _expect(stream.current, typ, value)


def expect_peek(stream: TokenStream, typ: str, value: str = None) -> None:
    _expect(stream.peek, typ, value)


def is_end_tag(tok: Token) -> bool:
    return tok.value.startswith("end")


def eat_block(stream: TokenStream, end: Tuple[str, ...]) -> None:
    """Advance the stream pointer past the next end tag.

    This is used to discard blocks after a syntax error is found, in the hope
    that we can continue to parse more of the stream after the offending block.
    """
    while stream.current.type != TOKEN_EOF:
        if stream.current.type == TOKEN_TAG_NAME and stream.current.value in end:
            break
        stream.next_token()


class Precedence(IntEnum):
    """Operator precedence."""

    LOWEST = 1
    LOGICALRIGHT = 49
    LOGICAL = 50
    RELATIONAL = auto()
    MEMBERSHIP = auto()
    PREFIX = auto()


PRECEDENCES = {
    TOKEN_IDENTIFIER: Precedence.LOWEST,
    TOKEN_EQ: Precedence.RELATIONAL,
    TOKEN_LT: Precedence.RELATIONAL,
    TOKEN_GT: Precedence.RELATIONAL,
    TOKEN_NE: Precedence.RELATIONAL,
    TOKEN_LG: Precedence.RELATIONAL,
    TOKEN_LE: Precedence.RELATIONAL,
    TOKEN_GE: Precedence.RELATIONAL,
    TOKEN_CONTAINS: Precedence.MEMBERSHIP,
    TOKEN_AND: Precedence.LOGICAL,
    TOKEN_OR: Precedence.LOGICAL,
}

RIGHT_ASSOCIATIVE = frozenset((TOKEN_AND, TOKEN_OR))

IDENTIFIER_TOKENS = frozenset(
    (TOKEN_IDENTIFIER, TOKEN_INTEGER, TOKEN_DOT, TOKEN_LBRACKET, TOKEN_STRING)
)


def peek_precedence(stream: TokenStream) -> Precedence:
    """Return the precedence of the next token in the stream."""
    try:
        precedence = PRECEDENCES[stream.peek.type]
    except KeyError as err:
        raise LiquidSyntaxError(f"unknown operator '{stream.peek.value}'") from err
    return precedence


def current_precedence(stream: TokenStream) -> Precedence:
    """Return the precedence of the current token in the stream."""
    precedence = PRECEDENCES.get(stream.current.type, Precedence.LOWEST)
    if stream.current.type in RIGHT_ASSOCIATIVE:
        precedence -= 1
    return Precedence(precedence)


def parse_filters(stream: TokenStream) -> List[expression.Filter]:
    """Keep reading filters from the token stream until end of expression."""
    filters = []
    while stream.current.type != TOKEN_EOF:
        filters.append(parse_filter(stream))
    return filters


def parse_filter(stream: TokenStream) -> expression.Filter:
    """Read a single filter with optional arguments from the token stream."""
    # Eat the pipe token
    expect(stream, TOKEN_PIPE)
    stream.next_token()

    # Read the filter's name
    expect(stream, TOKEN_IDENTIFIER)
    filter_name = stream.current.value
    stream.next_token()

    #
    args = []
    if stream.current.type == TOKEN_COLON:
        stream.next_token()

        while stream.current.type not in (TOKEN_PIPE, TOKEN_EOF):
            args.append(parse_expression(stream))
            stream.next_token()

            if stream.current.type == TOKEN_COMMA:
                stream.next_token()

    return expression.Filter(filter_name, args)


def parse_boolean(stream: TokenStream) -> expression.Boolean:
    """Read a boolean literal (true or false) from the token stream."""
    return expression.Boolean(stream.current, value=stream.current.type == TOKEN_TRUE)


def parse_nil(stream: TokenStream) -> expression.Nil:
    """Read a 'nil' keyword from the token stream."""
    return expression.Nil(stream.current)


def parse_empty(stream: TokenStream) -> expression.Empty:
    """Read a 'empty' keyword from the token stream."""
    return expression.Empty(stream.current)


def parse_string_literal(stream: TokenStream) -> expression.StringLiteral:
    """Read a string from the token stream."""
    return expression.StringLiteral(stream.current, value=stream.current.value)


def parse_integer_literal(stream: TokenStream) -> expression.IntegerLiteral:
    """Read an integer from the token stream."""
    return expression.IntegerLiteral(stream.current, value=int(stream.current.value))


def parse_float_literal(stream: TokenStream) -> expression.FloatLiteral:
    """Read a float from the token stream."""
    return expression.FloatLiteral(stream.current, value=float(stream.current.value))


def parse_identifier(stream: TokenStream) -> expression.Identifier:
    """Read an identifier from the token stream.

    <ident>.<ident>
    <ident>["<ident>"]
    <ident>["<ident>"].<ident>
    <ident>[<ident --> int/str>]
    <ident>[<ident>.<ident --> int/str>]
    <ident>[<int>]
    <ident>[<int>].<ident>
    """
    tok = stream.current
    path = []

    while stream.current.type in IDENTIFIER_TOKENS:
        if stream.current.type == TOKEN_IDENTIFIER:
            path.append(
                expression.IdentifierPathElement(stream.current, stream.current.value)
            )
        elif stream.current.type == TOKEN_INTEGER:
            path.append(
                expression.IdentifierPathElement(
                    stream.current, int(stream.current.value)
                )
            )
        elif stream.current.type == TOKEN_LBRACKET:
            stream.next_token()  # Eat open bracket

            if stream.current.type == TOKEN_STRING:
                path.append(
                    expression.IdentifierPathElement(
                        stream.current, stream.current.value
                    )
                )
            elif stream.current.type == TOKEN_INTEGER:
                path.append(
                    expression.IdentifierPathElement(
                        stream.current, int(stream.current.value)
                    )
                )
            elif stream.current.type == TOKEN_IDENTIFIER:
                # Recursive call to parse_identifier. If it's not a string or
                # integer, anything inside a pair of square brackets could be
                # another identifier that resolves to a string or integer.
                path.append(parse_identifier(stream))
            else:
                raise LiquidSyntaxError(
                    f"invalid identifier, found {stream.current.type}"
                )

            expect_peek(stream, TOKEN_RBRACKET)
            stream.next_token()  # Eat close bracket

        elif stream.current.type == TOKEN_DOT:
            pass
        else:
            raise LiquidSyntaxError(f"invalid identifier, found {stream.current.type}")

        stream.next_token()

    stream.push(stream.current)
    return expression.Identifier(tok, path)


RangeOption = namedtuple("RangeOption", ["tok", "arg"])


def parse_range_argument(
    stream: TokenStream,
) -> Union[expression.Identifier, expression.IntegerLiteral]:
    if stream.current.type == TOKEN_IDENTIFIER:
        arg = parse_identifier(stream)
    elif stream.current.type == TOKEN_INTEGER:
        arg = parse_integer_literal(stream)
    else:
        raise LiquidSyntaxError(
            f"invalid range expression, expected an integer, found a {stream.current.type}"
        )
    return arg


def parse_string_or_identifier(stream, linenum=None) -> ast.Expression:
    if stream.current.type == TOKEN_IDENTIFIER:
        expr = parse_identifier(stream)
    elif stream.current.type == TOKEN_STRING:
        expr = parse_string_literal(stream)
    else:
        _typ = reverse_operators.get(stream.current.type, stream.current.type)
        msg = f"expected {TOKEN_IDENTIFIER} or {TOKEN_STRING}, found {_typ}"
        raise LiquidSyntaxError(msg, linenum=linenum or stream.current.linenum)

    return expr


def parse_unchained_identifier(stream, linenum=None) -> ast.Expression:
    expect(stream, TOKEN_IDENTIFIER)
    tok = stream.current
    ident = parse_identifier(stream)

    if len(ident.path) != 1:
        raise LiquidSyntaxError(
            f"invalid identifier '{ident}'", linenum=linenum or tok.linenum
        )

    return ident


def parse_range_option(stream: TokenStream) -> RangeOption:
    tok = stream.current
    if stream.current.type in (TOKEN_LIMIT, TOKEN_OFFSET, TOKEN_COLS):
        expect_peek(stream, TOKEN_COLON)
        stream.next_token()
        stream.next_token()  # Eat COLON
        arg = parse_range_argument(stream)
        stream.next_token()
        opt = RangeOption(tok=tok, arg=arg)
    else:
        expect(stream, TOKEN_REVERSED)
        stream.next_token()  # Eat REVERSED
        opt = RangeOption(tok=tok, arg=None)

    return opt


def parse_prefix_expression(stream: TokenStream) -> expression.PrefixExpression:
    exp = expression.PrefixExpression(stream.current, stream.current.value)
    stream.next_token()
    exp.right = parse_expression(stream, precedence=Precedence.PREFIX)
    return exp


def parse_infix_expression(stream: TokenStream, left) -> expression.InfixExpression:
    exp = expression.InfixExpression(
        stream.current, left=left, operator=stream.current.value
    )
    precedence = current_precedence(stream)
    stream.next_token()
    exp.right = parse_expression(stream, precedence)
    return exp


prefix_funcs = {
    TOKEN_FALSE: parse_boolean,
    TOKEN_TRUE: parse_boolean,
    TOKEN_NIL: parse_nil,
    TOKEN_EMPTY: parse_empty,
    TOKEN_NEGATIVE: parse_prefix_expression,
    TOKEN_STRING: parse_string_literal,
    TOKEN_INTEGER: parse_integer_literal,
    TOKEN_FLOAT: parse_float_literal,
    TOKEN_IDENTIFIER: parse_identifier,
}

infix_funcs = {
    TOKEN_EQ: parse_infix_expression,
    TOKEN_OR: parse_infix_expression,
    TOKEN_AND: parse_infix_expression,
    TOKEN_LT: parse_infix_expression,
    TOKEN_GT: parse_infix_expression,
    TOKEN_NE: parse_infix_expression,
    TOKEN_LG: parse_infix_expression,
    TOKEN_LE: parse_infix_expression,
    TOKEN_GE: parse_infix_expression,
    TOKEN_CONTAINS: parse_infix_expression,
}


def parse_expression(
    stream: TokenStream,
    precedence: Precedence = Precedence.LOWEST,
) -> expression.Expression:
    """Parse a literal or logical expression."""
    prefix = prefix_funcs.get(stream.current.type)
    if prefix is None:
        operator = reverse_operators.get(stream.current.type, stream.current.value)
        raise LiquidSyntaxError(f"unknown prefix operator '{operator}'")

    left = prefix(stream)

    while (
        stream.peek.type != TOKEN_EOF
        and stream.peek.type not in (TOKEN_PIPE, TOKEN_COMMA)
        and precedence < peek_precedence(stream)
    ):
        infix = infix_funcs.get(stream.peek.type)
        if infix is None:
            return left

        stream.next_token()
        left = infix(stream, left)

    return left


def parse_filtered_expression(stream: TokenStream) -> expression.FilteredExpression:
    """Parse a statement (output) expression with optional filters.

    A statement expression is assumed to start with exactly one identifier, followed by
    zero or more filters.
    """
    expr = parse_expression(stream)
    stream.next_token()
    filters = parse_filters(stream)
    return expression.FilteredExpression(expr, filters)


def parse_boolean_expression(stream) -> expression.Expression:
    """Parse a liquid expression that evaluates to a Boolean value.

    This is primarily used by control flow tags like `if`, `unless` and `case`/`when`.

    Logical operators (`and` and `or`) are right associative. They are evaluated from
    right to left. The use of parentheses to control operator precedence is not allowed.
    """
    if stream.current.type == TOKEN_EOF:
        # Empty expression.
        return expression.Nil(tok=stream.current.type)
    return expression.BooleanExpression(
        tok=stream.current.type, expression=parse_expression(stream)
    )


def parse_assignment_expression(stream) -> expression.AssignmentExpression:
    """Parse a liquid assignment expression, as one might find in an `assign` tag.

    This is essentially the same as a parse_filtered_expression, but with
    an additional name to bind the expression result to.
    """
    expect(stream, TOKEN_IDENTIFIER)
    expect_peek(stream, TOKEN_ASSIGN)

    tok = stream.current
    name = parse_unchained_identifier(stream)

    stream.next_token()
    stream.next_token()  # Eat ASSIGN TOKEN

    expr = parse_filtered_expression(stream)

    return expression.AssignmentExpression(tok=tok, name=str(name), expression=expr)


def parse_loop_expression(stream) -> expression.LoopExpression:
    """Parse a liquid loop expression, as one might find in a `for` tag.

    If any of the optional parameters are duplicated, the last (right most) is
    used.
    """
    expect(stream, TOKEN_IDENTIFIER)
    expect_peek(stream, TOKEN_IN)

    expr = expression.LoopExpression(name=stream.current.value)

    stream.next_token()
    stream.next_token()  # Eat TOKEN_IN

    if stream.current.type == TOKEN_IDENTIFIER:
        # Identifier should resolve to an array or hash/map at render time.
        expr.identifier = parse_identifier(stream)
        stream.next_token()
    elif stream.current.type == TOKEN_LPAREN:
        # Start of a range expression (<int or id>..<int or id>)
        stream.next_token()
        start = parse_range_argument(stream)

        # assert stream.peek.type == TOKEN_RANGE
        expect_peek(stream, TOKEN_RANGE)

        stream.next_token()
        stream.next_token()  # Eat TOKEN_RANGE
        stop = parse_range_argument(stream)

        # assert stream.peek.type == TOKEN_RPAREN
        expect_peek(stream, TOKEN_RPAREN)

        expr.start = start
        expr.stop = stop

        stream.next_token()
        stream.next_token()  # Eat TOKEN_RPAREN
    else:
        raise LiquidSyntaxError("invalid range expression")

    # Optional range modifiers can appear in any order.
    while stream.current.type in (
        TOKEN_LIMIT,
        TOKEN_OFFSET,
        TOKEN_COLS,
        TOKEN_REVERSED,
    ):
        opt = parse_range_option(stream)

        if opt.tok.type == TOKEN_REVERSED:
            expr.reversed = True
        elif opt.tok.type == TOKEN_LIMIT:
            expr.limit = opt.arg
        elif opt.tok.type == TOKEN_OFFSET:
            expr.offset = opt.arg
        elif opt.tok.type == TOKEN_COLS:
            expr.cols = opt.arg

    return expr


@lru_cache
def get_parser(env):
    return Parser(env)
