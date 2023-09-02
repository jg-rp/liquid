"""Liquid template parser.

As of Python Liquid 1.2.0 we are transitioning away from the expression parser defined
here. Instead opting for separate, specialized parsers (and lexers) for each of the
three built-in expression types.

The `ExpressionParser` class will become depreciated as we approach version 2.0 and then
removed. At which time this module will be reserved for parsing templates (not
expressions), possibly with some explicit re-exports of the expression parsers found in
`liquid.expressions`.

Developers of custom tags are encouraged to use or follow the example of:

- `liquid.expressions.parse_boolean_expression`
- `liquid.expressions.parse_filtered_expression`
- `liquid.expressions.parse_loop_expression`

And make use of `liquid.expressions.common` and `liquid.expressions.TokenStream`.
"""

from __future__ import annotations

from enum import IntEnum
from enum import auto
from functools import lru_cache
from typing import TYPE_CHECKING
from typing import Container
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple
from typing import Union

from liquid import ast
from liquid import expression
from liquid.exceptions import Error
from liquid.exceptions import LiquidSyntaxError
from liquid.expression import IdentifierPathElement
from liquid.lex import tokenize_boolean_expression
from liquid.lex import tokenize_filtered_expression
from liquid.lex import tokenize_loop_expression
from liquid.limits import to_int
from liquid.stream import TokenStream
from liquid.token import TOKEN_AND
from liquid.token import TOKEN_ASSIGN
from liquid.token import TOKEN_BLANK
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COLS
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_CONTAINS
from liquid.token import TOKEN_CONTINUE
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_EMPTY
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_EQ
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_GE
from liquid.token import TOKEN_GT
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_ILLEGAL
from liquid.token import TOKEN_IN
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_LE
from liquid.token import TOKEN_LG
from liquid.token import TOKEN_LIMIT
from liquid.token import TOKEN_LITERAL
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_LT
from liquid.token import TOKEN_NE
from liquid.token import TOKEN_NEGATIVE
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_NULL
from liquid.token import TOKEN_OFFSET
from liquid.token import TOKEN_OR
from liquid.token import TOKEN_PIPE
from liquid.token import TOKEN_RANGE
from liquid.token import TOKEN_RBRACKET
from liquid.token import TOKEN_REVERSED
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_STATEMENT
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_TRUE
from liquid.token import Token
from liquid.token import reverse_operators

if TYPE_CHECKING:
    from liquid import Environment


class Parser:
    """A Liquid template parser. Create a parse tree from a stream of tokens."""

    __slots__ = ("tags", "illegal", "literal", "statement", "env")

    def __init__(self, env: Environment):
        self.tags = env.tags
        self.env = env

        self.illegal = self.tags[TOKEN_ILLEGAL]
        self.literal = self.tags[TOKEN_LITERAL]
        self.statement = self.tags[TOKEN_STATEMENT]

    def parse(self, stream: TokenStream) -> ast.ParseTree:
        """Parse the given stream of tokens into a tree."""
        root = ast.ParseTree()
        statements = root.statements

        while stream.current.type != TOKEN_EOF:
            try:
                statements.append(self.parse_statement(stream))
            except Error as err:
                self.env.error(err, linenum=stream.current.linenum)

            stream.next_token()

        return root

    def parse_statement(self, stream: TokenStream) -> ast.Node:
        """Parse a node from a stream of tokens."""
        if stream.current.type == TOKEN_STATEMENT:
            node = self.statement.get_node(stream)
        elif stream.current.type == TOKEN_TAG:
            tag = self.tags.get(stream.current.value, self.illegal)
            node = tag.get_node(stream)

            # Tag parse functions can choose to return an IllegalNode.
            if isinstance(node, ast.IllegalNode):
                raise LiquidSyntaxError(
                    f"unexpected tag '{node.token().value}'",
                    linenum=node.token().linenum,
                )
        else:
            node = self.literal.get_node(stream)

        return node

    def parse_block(self, stream: TokenStream, end: Container[str]) -> ast.BlockNode:
        """Parse multiple nodes from a stream of tokens.

        Stop parsing nodes when we find a token in `end` or we reach the end of the
        stream.
        """
        block = ast.BlockNode(stream.current)
        statements = block.statements

        while stream.current.type != TOKEN_EOF:
            if stream.current.type == TOKEN_TAG and stream.current.value in end:
                break
            stmt = self.parse_statement(stream)
            statements.append(stmt)
            # Detect output nodes in any of this block's children. This is used by
            # some tags to automatically suppress whitespace when no other output is
            # present.
            if (
                self.env.render_whitespace_only_blocks
                or stmt.force_output
                or getattr(stmt, "forced_output", False)
            ):
                block.forced_output = True
            stream.next_token()

        return block


def eat_block(stream: TokenStream, end: Container[str]) -> None:
    """Advance the stream pointer past the next end tag.

    This is used to discard blocks after a syntax error is found, in the hope
    that we can continue to parse more of the stream after the offending block.
    """
    while stream.current.type != TOKEN_EOF:
        if stream.current.type == TOKEN_TAG and stream.current.value in end:
            break
        stream.next_token()


@lru_cache(maxsize=128)
def get_parser(env: Environment) -> Parser:
    """Return a template parser for the given environment."""
    return Parser(env)


# NOTE: Everything from here on is flagged for future depreciation. See the comments at
# the top of this module.


def _expect(tok: Token, typ: str, value: Optional[str] = None) -> None:
    if tok.type != typ or (value is not None and tok.value != value):
        _typ = reverse_operators.get(tok.type, tok.type)
        _expected_typ = reverse_operators.get(typ, typ)
        if value is not None:
            msg = (
                f"expected {_expected_typ} with value '{value}', "
                f"found {_typ} with value '{tok.value}'"
            )
        else:
            msg = f"expected '{_expected_typ}', found '{_typ}'"
        raise LiquidSyntaxError(msg, linenum=tok.linenum)


def expect(stream: TokenStream, typ: str, value: Optional[str] = None) -> None:
    """Check the current token in the stream matches the given type and value.

    Raises a `LiquidSyntaxError` if they don't.
    """
    _expect(stream.current, typ, value)


def expect_peek(stream: TokenStream, typ: str, value: Optional[str] = None) -> None:
    """Check the next token in the stream matches the given type and value.

    Raises a `LiquidSyntaxError` if they don't.
    """
    _expect(stream.peek, typ, value)


def is_end_tag(tok: Token) -> bool:
    """Return `True` if the current token looks like an end tag."""
    return tok.value.startswith("end")


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

LOOP_TOKENS = frozenset(
    (
        TOKEN_LIMIT,
        TOKEN_OFFSET,
        TOKEN_COLS,
        TOKEN_REVERSED,
    )
)

FILTER_END_TOKENS = frozenset((TOKEN_PIPE, TOKEN_EOF))


def parse_boolean(stream: TokenStream) -> expression.Boolean:
    """Read a boolean literal (true or false) from the token stream."""
    if stream.current.type == TOKEN_TRUE:
        return expression.TRUE
    return expression.FALSE


def parse_nil(_: TokenStream) -> expression.Nil:
    """Read a 'nil' keyword from the token stream."""
    return expression.NIL


def parse_empty(_: TokenStream) -> expression.Empty:
    """Read a 'empty' keyword from the token stream."""
    return expression.EMPTY


def parse_blank(_: TokenStream) -> expression.Blank:
    """Read a 'blank' keyword from the token stream."""
    return expression.BLANK


def parse_string_literal(stream: TokenStream) -> expression.StringLiteral:
    """Read a string from the token stream."""
    return expression.StringLiteral(value=stream.current.value)


def parse_integer_literal(stream: TokenStream) -> expression.IntegerLiteral:
    """Read an integer from the token stream."""
    return expression.IntegerLiteral(value=to_int(stream.current.value))


def parse_float_literal(stream: TokenStream) -> expression.FloatLiteral:
    """Read a float from the token stream."""
    return expression.FloatLiteral(value=float(stream.current.value))


def parse_range_literal(stream: TokenStream) -> expression.RangeLiteral:
    """Read a range literal from the token stream."""
    # Start of a range expression (<int or id>..<int or id>)
    expect(stream, TOKEN_LPAREN)
    stream.next_token()
    start = parse_range_argument(stream)

    expect_peek(stream, TOKEN_RANGE)
    stream.next_token()
    stream.next_token()  # Eat TOKEN_RANGE

    stop = parse_range_argument(stream)
    expect_peek(stream, TOKEN_RPAREN)

    assert isinstance(
        start,
        (expression.Identifier, expression.IntegerLiteral, expression.FloatLiteral),
    )
    assert isinstance(
        stop,
        (expression.Identifier, expression.IntegerLiteral, expression.FloatLiteral),
    )

    expr = expression.RangeLiteral(start, stop)
    stream.next_token()
    return expr


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
    path: expression.IdentifierPath = []

    while stream.current.type in IDENTIFIER_TOKENS:
        if stream.current.type == TOKEN_IDENTIFIER:
            path.append(IdentifierPathElement(stream.current.value))

        elif stream.current.type == TOKEN_INTEGER:
            path.append(IdentifierPathElement(to_int(stream.current.value)))

        elif stream.current.type == TOKEN_LBRACKET:
            stream.next_token()  # Eat open bracket

            if stream.current.type == TOKEN_STRING:
                path.append(IdentifierPathElement(stream.current.value))
            elif stream.current.type == TOKEN_NEGATIVE:
                expect_peek(stream, TOKEN_INTEGER)
                stream.next_token()
                path.append(IdentifierPathElement(-to_int(stream.current.value)))
            elif stream.current.type == TOKEN_INTEGER:
                path.append(IdentifierPathElement(to_int(stream.current.value)))

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
    return expression.Identifier(path)


def parse_string_or_identifier(  # pragma: no cover
    stream: TokenStream,
    linenum: Optional[int] = None,
) -> expression.Expression:
    """Parse an expression from a stream of tokens.

    If the stream is not at a string or identifier expression, raise a syntax error.
    """
    if stream.current.type == TOKEN_IDENTIFIER:
        expr: expression.Expression = parse_identifier(stream)
    elif stream.current.type == TOKEN_STRING:
        expr = parse_string_literal(stream)
    else:
        _typ = reverse_operators.get(stream.current.type, stream.current.type)
        msg = f"expected {TOKEN_IDENTIFIER} or {TOKEN_STRING}, found {_typ}"
        raise LiquidSyntaxError(msg, linenum=linenum or stream.current.linenum)

    return expr


def parse_unchained_identifier(
    stream: TokenStream,
    linenum: Optional[int] = None,
) -> expression.Identifier:
    """Parse an identifier from a stream of tokens.

    If the stream is not at an identifier or the identifier is chained, raise a
    syntax error
    """
    expect(stream, TOKEN_IDENTIFIER)
    tok = stream.current
    ident = parse_identifier(stream)

    if len(ident.path) != 1:
        raise LiquidSyntaxError(
            f"invalid identifier '{ident}'", linenum=linenum or tok.linenum
        )

    return ident


# NOTE: These names are misleading. The args and options in question can apply to any
# iterable in a loop expression, not just ranges.

RangeArg = Union[
    expression.Identifier,
    expression.IntegerLiteral,
    expression.FloatLiteral,
    expression.Continue,
    expression.Nil,
]


class RangeOption(NamedTuple):
    """A token and value representing a keyword argument in a loop expression."""

    tok: Token
    arg: RangeArg


def parse_range_argument(stream: TokenStream) -> RangeArg:
    """Parse a loop argument value from a stream of tokens.

    If the stream is not at a valid token for a loop argument value, raise a syntax
    error.
    """
    if stream.current.type == TOKEN_IDENTIFIER:
        arg: RangeArg = parse_identifier(stream)
    elif stream.current.type == TOKEN_INTEGER:
        arg = parse_integer_literal(stream)
    elif stream.current.type == TOKEN_FLOAT:
        arg = parse_float_literal(stream)
    elif stream.current.type == TOKEN_CONTINUE:
        arg = expression.CONTINUE
    else:
        raise LiquidSyntaxError(
            "invalid range expression, expected an integer, "
            f"found a {stream.current.type}"
        )
    return arg


def parse_range_option(stream: TokenStream) -> RangeOption:
    """Parse a loop keyword argument from a stream of tokens.

    If the stream is not at a valid loop keyword argument, raise a syntax error.
    """
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
        opt = RangeOption(tok=tok, arg=expression.NIL)

    return opt


def parse_loop_expression_value(value: str) -> expression.LoopExpression:
    """Parse the given string as a loop expression."""
    return parse_loop_expression(TokenStream(tokenize_loop_expression(value)))


def parse_loop_expression(stream: TokenStream) -> expression.LoopExpression:
    """Parse a liquid loop expression, as one might find in a `for` tag.

    If any of the optional parameters are duplicated, the last (right most) is
    used.
    """
    expect(stream, TOKEN_IDENTIFIER)
    expect_peek(stream, TOKEN_IN)

    # Loop variable name
    name = stream.current.value

    stream.next_token()
    stream.next_token()  # Eat TOKEN_IN

    if stream.current.type == TOKEN_IDENTIFIER:
        # Identifier should resolve to an array or hash/map at render time.
        iterable: expression.LoopIterable = parse_identifier(stream)
        stream.next_token()
    elif stream.current.type == TOKEN_LPAREN:
        iterable = parse_range_literal(stream)
        stream.next_token()
    else:
        raise LiquidSyntaxError("invalid loop expression")

    expr = expression.LoopExpression(name=name, iterable=iterable)

    # Optional range modifiers can appear in any order.
    while stream.current.type in LOOP_TOKENS:
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


class ExpressionParser:
    """The standard expression parser.

    Custom, non "standard" tags can subclass `ExpressionParser` to change expression
    parsing behavior. Such as adding a logical `NOT` operator.
    """

    END_EXPRESSION: Tuple[str, ...] = (
        TOKEN_PIPE,
        TOKEN_COMMA,
        TOKEN_EOF,
    )

    def __init__(self) -> None:
        self.precedences = PRECEDENCES.copy()
        self.right_associative = RIGHT_ASSOCIATIVE.copy()

        self.prefix_funcs = {
            TOKEN_FALSE: parse_boolean,
            TOKEN_TRUE: parse_boolean,
            TOKEN_NIL: parse_nil,
            TOKEN_NULL: parse_nil,
            TOKEN_EMPTY: parse_empty,
            TOKEN_BLANK: parse_blank,
            TOKEN_NEGATIVE: self.parse_prefix_expression,
            TOKEN_STRING: parse_string_literal,
            TOKEN_INTEGER: parse_integer_literal,
            TOKEN_FLOAT: parse_float_literal,
            TOKEN_IDENTIFIER: parse_identifier,
            TOKEN_LPAREN: parse_range_literal,
        }

        self.infix_funcs = {
            TOKEN_EQ: self.parse_infix_expression,
            TOKEN_OR: self.parse_infix_expression,
            TOKEN_AND: self.parse_infix_expression,
            TOKEN_LT: self.parse_infix_expression,
            TOKEN_GT: self.parse_infix_expression,
            TOKEN_NE: self.parse_infix_expression,
            TOKEN_LG: self.parse_infix_expression,
            TOKEN_LE: self.parse_infix_expression,
            TOKEN_GE: self.parse_infix_expression,
            TOKEN_CONTAINS: self.parse_infix_expression,
        }

    def peek_precedence(self, stream: TokenStream) -> Precedence:
        """Return the precedence of the next token in the stream."""
        try:
            precedence = self.precedences[stream.peek.type]
        except KeyError as err:
            raise LiquidSyntaxError(f"unknown operator '{stream.peek.value}'") from err
        return precedence

    def current_precedence(self, stream: TokenStream) -> Precedence:
        """Return the precedence of the current token in the stream."""
        precedence = self.precedences.get(stream.current.type, Precedence.LOWEST)
        if stream.current.type in self.right_associative:
            precedence = Precedence(precedence - 1)
        return Precedence(precedence)

    def parse_filters(self, stream: TokenStream) -> List[expression.Filter]:
        """Keep reading filters from the token stream until end of expression."""
        filters = []
        while stream.current.type != TOKEN_EOF:
            filters.append(self.parse_filter(stream))
        return filters

    def parse_filter(self, stream: TokenStream) -> expression.Filter:
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
        kwargs = {}

        if stream.current.type == TOKEN_COLON:
            stream.next_token()

            while stream.current.type not in FILTER_END_TOKENS:
                if stream.peek.type == TOKEN_COLON:
                    # A named parameter
                    param_name = stream.current.value
                    stream.next_token()

                    # Eat colon
                    stream.next_token()

                    param_value = self.parse_expression(stream)
                    kwargs[param_name] = param_value
                else:
                    # A positional argument/parameter
                    args.append(self.parse_expression(stream))
                stream.next_token()

                if stream.current.type == TOKEN_COMMA:
                    stream.next_token()

        return expression.Filter(filter_name, args, kwargs)

    def parse_prefix_expression(
        self, stream: TokenStream
    ) -> expression.PrefixExpression:
        """Parse a prefix expression from a stream of tokens."""
        tok = stream.current
        stream.next_token()

        return expression.PrefixExpression(
            tok.value,
            right=self.parse_expression(stream, precedence=Precedence.PREFIX),
        )

    def parse_infix_expression(
        self,
        stream: TokenStream,
        left: expression.Expression,
    ) -> expression.InfixExpression:
        """Parse an infix expression from a stream of tokens."""
        tok = stream.current
        precedence = self.current_precedence(stream)
        stream.next_token()

        return expression.InfixExpression(
            left=left,
            operator=tok.value,
            right=self.parse_expression(stream, precedence),
        )

    def parse_expression(
        self,
        stream: TokenStream,
        precedence: Precedence = Precedence.LOWEST,
    ) -> expression.Expression:
        """Parse a literal or logical expression."""
        end_expression = self.END_EXPRESSION
        infix_funcs = self.infix_funcs

        prefix = self.prefix_funcs.get(stream.current.type)
        if prefix is None:
            operator = reverse_operators.get(stream.current.type, stream.current.value)
            raise LiquidSyntaxError(f"unknown prefix operator '{operator}'")

        left = prefix(stream)

        while (
            stream.peek.type not in end_expression
            and precedence < self.peek_precedence(stream)
        ):
            infix = infix_funcs.get(stream.peek.type)
            if infix is None:
                return left

            stream.next_token()
            left = infix(stream, left)

        return left

    def parse_filtered_expression_value(
        self, value: str
    ) -> expression.FilteredExpression:
        """Parse the given value as a filtered expression."""
        return self.parse_filtered_expression(
            TokenStream(tokenize_filtered_expression(value))
        )

    def parse_filtered_expression(
        self, stream: TokenStream
    ) -> expression.FilteredExpression:
        """Parse a statement (output) expression with optional filters.

        A statement expression is assumed to start with exactly one identifier, followed
        by zero or more filters.
        """
        expr = self.parse_expression(stream)
        stream.next_token()
        filters = self.parse_filters(stream)
        return expression.FilteredExpression(expr, filters)

    def parse_boolean_expression_value(
        self, value: str
    ) -> expression.Expression:  # pragma: no cover
        """Parse the given string as a boolean expression."""
        return self.parse_boolean_expression(
            TokenStream(tokenize_boolean_expression(value))
        )

    def parse_boolean_expression(self, stream: TokenStream) -> expression.Expression:
        """Parse a liquid expression that evaluates to a Boolean value.

        This is primarily used by control flow tags like `if`, `unless` and `case`/
        `when`.

        Logical operators (`and` and `or`) are right associative. They are evaluated
        from right to left. The use of parentheses to control operator precedence is
        not allowed.
        """
        if stream.current.type == TOKEN_EOF:
            # Empty expression.
            return expression.NIL
        return expression.BooleanExpression(expression=self.parse_expression(stream))

    def parse_assignment_expression(
        self, stream: TokenStream
    ) -> expression.AssignmentExpression:
        """Parse a liquid assignment expression, as one might find in an `assign` tag.

        This is essentially the same as a parse_filtered_expression, but with
        an additional name to bind the expression result to.
        """
        expect(stream, TOKEN_IDENTIFIER)
        expect_peek(stream, TOKEN_ASSIGN)

        name = parse_unchained_identifier(stream)

        stream.next_token()
        stream.next_token()  # Eat ASSIGN TOKEN

        expr = self.parse_filtered_expression(stream)

        return expression.AssignmentExpression(name=str(name), expression=expr)


# For backwards compatibility.
STANDARD_EXPRESSION_PARSER = ExpressionParser()
peek_precedence = STANDARD_EXPRESSION_PARSER.peek_precedence
current_precedence = STANDARD_EXPRESSION_PARSER.current_precedence
parse_filters = STANDARD_EXPRESSION_PARSER.parse_filters
parse_filter = STANDARD_EXPRESSION_PARSER.parse_filter
parse_prefix_expression = STANDARD_EXPRESSION_PARSER.parse_prefix_expression
parse_infix_expression = STANDARD_EXPRESSION_PARSER.parse_infix_expression
parse_expression = STANDARD_EXPRESSION_PARSER.parse_expression
parse_filtered_expression = STANDARD_EXPRESSION_PARSER.parse_filtered_expression
parse_filtered_expression_value = (
    STANDARD_EXPRESSION_PARSER.parse_filtered_expression_value
)
parse_boolean_expression = STANDARD_EXPRESSION_PARSER.parse_boolean_expression
parse_boolean_expression_value = (
    STANDARD_EXPRESSION_PARSER.parse_boolean_expression_value
)
parse_assignment_expression = STANDARD_EXPRESSION_PARSER.parse_assignment_expression


@lru_cache(maxsize=128)
def get_expression_parser(_: Environment) -> ExpressionParser:
    """Return an expression parser for the given environment."""
    # Future proofing.
    return STANDARD_EXPRESSION_PARSER
