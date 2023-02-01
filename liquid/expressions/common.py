"""Patterns and parse functions common to multiple built-in expression types."""
from __future__ import annotations
import re
import sys

from typing import Callable
from typing import Iterator
from typing import Tuple
from typing import Union
from typing import TYPE_CHECKING

from liquid.expression import Expression
from liquid.expression import TRUE
from liquid.expression import FALSE
from liquid.expression import BLANK
from liquid.expression import NIL
from liquid.expression import EMPTY
from liquid.expression import Nil
from liquid.expression import Blank
from liquid.expression import Empty
from liquid.expression import Boolean
from liquid.expression import Identifier
from liquid.expression import IdentifierPath
from liquid.expression import IdentifierPathElement
from liquid.expression import StringLiteral
from liquid.expression import IntegerLiteral
from liquid.expression import FloatLiteral
from liquid.expression import RangeLiteral

from liquid.token import reverse_operators
from liquid.token import TOKEN_TRUE
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_IDENTINDEX
from liquid.token import TOKEN_IDENTSTRING
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_RBRACKET
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_RANGE
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_NULL
from liquid.token import TOKEN_BLANK
from liquid.token import TOKEN_EMPTY
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_NEWLINE
from liquid.token import TOKEN_SKIP
from liquid.token import TOKEN_ILLEGAL
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_OR

from liquid.exceptions import LiquidSyntaxError
from liquid.limits import to_int

if TYPE_CHECKING:
    from liquid.expressions.stream import TokenStream

GROUP_QUOTE = sys.intern("quote")
GROUP_QUOTED = sys.intern("quoted")
GROUP_IDENTINDEX = sys.intern("path_index")
GROUP_IDENTQUOTE = sys.intern("identquote")
GROUP_IDENTQUOTED = sys.intern("identquoted")

# The reference implementation will accept identifiers that start with an integer or
# hyphen when in lax mode, but will raise a syntax error in strict mode. For historic
# reasons we'll stick the following pattern until at least version 2 of Python Liquid.
IDENTIFIER_PATTERN = r"\w[\w\-]*\??"

# Trailing ? is not allowed in assignment names
ASSIGN_IDENTIFIER_PATTERN = r"\w[\w\-]*"

# ["ident"] or ['ident']
IDENTSTRING_PATTERN = (
    rf"\[\s*(?P<{GROUP_IDENTQUOTE}>[\"'])"
    rf"(?P<{GROUP_IDENTQUOTED}>.*?)"
    rf"(?P={GROUP_IDENTQUOTE})\s*]"
)

# [0] or [-1]
IDENTINDEX_PATTERN = rf"\[\s*(?P<{GROUP_IDENTINDEX}>\-?\d+)\s*]"

# 'something' or "something"
STRING_PATTERN = rf"(?P<{GROUP_QUOTE}>[\"'])(?P<{GROUP_QUOTED}>.*?)(?P={GROUP_QUOTE})"

# (position, type, value)
Token = Tuple[int, str, str]


def parse_boolean(stream: "TokenStream") -> Boolean:
    """Read a boolean literal (true or false) from the token stream."""
    if stream.current[1] == TOKEN_TRUE:
        return TRUE
    return FALSE


def parse_nil(_: "TokenStream") -> Nil:
    """Read a 'nil' keyword from the token stream."""
    return NIL


def parse_empty(_: "TokenStream") -> Empty:
    """Read a 'empty' keyword from the token stream."""
    return EMPTY


def parse_blank(_: "TokenStream") -> Blank:
    """Read a 'blank' keyword from the token stream."""
    return BLANK


def parse_string_literal(stream: "TokenStream") -> StringLiteral:
    """Read a string from the token stream."""
    return StringLiteral(value=stream.current[2])


def parse_integer_literal(stream: "TokenStream") -> IntegerLiteral:
    """Read an integer from the token stream."""
    return IntegerLiteral(value=to_int(stream.current[2]))


def parse_float_literal(stream: "TokenStream") -> FloatLiteral:
    """Read a float from the token stream."""
    return FloatLiteral(value=float(stream.current[2]))


def parse_identifier(stream: "TokenStream") -> Identifier:
    """Read an identifier from the token stream.

    An identifier might be chained with dots and square brackets, and might contain
    more, possibly chained, identifiers within those brackets.
    """
    path: IdentifierPath = []

    while True:
        pos, typ, val = stream.current
        if typ == TOKEN_IDENTIFIER:
            path.append(IdentifierPathElement(val))
        elif typ == TOKEN_IDENTINDEX:
            path.append(IdentifierPathElement(to_int(val)))
        elif typ == TOKEN_LBRACKET:
            stream.next_token()
            path.append(parse_identifier(stream))
            # Eat close bracket
            stream.next_token()
            stream.expect(TOKEN_RBRACKET)
        elif typ == TOKEN_FLOAT:
            raise LiquidSyntaxError(
                f"expected an identifier, found {val!r}",
                linenum=pos,
            )
        elif typ == TOKEN_DOT:
            pass
        else:
            stream.push(stream.current)
            break

        stream.next_token()

    return Identifier(path)


def parse_string_or_identifier(
    stream: "TokenStream",
) -> Union[StringLiteral, Identifier]:
    """Parse an expression from a stream of tokens. If the stream is not at a string or
    identifier expression, raise a syntax error.
    """
    typ = stream.current[1]
    if typ in (TOKEN_IDENTIFIER, TOKEN_LBRACKET):
        expr: Union[StringLiteral, Identifier] = parse_identifier(stream)
    elif typ == TOKEN_STRING:
        expr = parse_string_literal(stream)
    else:
        _typ = reverse_operators.get(typ, typ)
        msg = f"expected identifier or string, found {_typ}"
        raise LiquidSyntaxError(msg, linenum=stream.current[0])

    return expr


def parse_unchained_identifier(stream: "TokenStream") -> Identifier:
    """Parse an identifier from a stream of tokens. If the stream is not at an
    identifier or the identifier is chained, raise a syntax error."""
    tok = stream.current
    ident = parse_identifier(stream)
    if len(ident.path) != 1:
        raise LiquidSyntaxError(f"invalid identifier '{ident}'", linenum=tok[0])
    return ident


def make_parse_range(
    parse_obj: Callable[["TokenStream"], Expression]
) -> Callable[["TokenStream"], RangeLiteral]:
    """Return a function that parse range expressions using the given parse_obj
    callable.
    """

    def _parse_range_literal(stream: "TokenStream") -> RangeLiteral:
        """Read a range literal from the token stream.

        A range literal can contain an identifier (possibly chained), an integer or a
        float as its start and stop values.
        """
        # Eat left parenthesis
        stream.expect(TOKEN_LPAREN)
        stream.next_token()

        # Parse start
        if stream.current[1] not in (TOKEN_IDENTIFIER, TOKEN_INTEGER, TOKEN_FLOAT):
            raise LiquidSyntaxError(
                f"unexpected {stream.current[2]!r} in range expression",
                linenum=stream.current[0],
            )
        start = parse_obj(stream)
        stream.next_token()

        # Eat TOKEN_RANGE
        stream.expect(TOKEN_RANGE)
        stream.next_token()

        # Parse stop
        if stream.current[1] not in (TOKEN_IDENTIFIER, TOKEN_INTEGER, TOKEN_FLOAT):
            raise LiquidSyntaxError(
                f"unexpected {stream.current[2]!r} in range expression",
                linenum=stream.current[0],
            )
        stop = parse_obj(stream)

        expr = RangeLiteral(start, stop)

        # Eat right parenthesis
        stream.next_token()
        stream.expect(TOKEN_RPAREN)

        return expr

    return _parse_range_literal


_IDENT_TOKENS = frozenset(
    (
        TOKEN_IDENTIFIER,
        TOKEN_IDENTINDEX,
        TOKEN_DOT,
        TOKEN_LBRACKET,
    )
)


def _parse_common_identifier(stream: "TokenStream") -> Identifier:
    """This is much like `parse_identifier`, but leaves the last ident
    token on the stream."""
    path: IdentifierPath = []

    while True:
        _, _type, value = stream.current
        if _type == TOKEN_IDENTIFIER:
            path.append(IdentifierPathElement(value))
        elif _type == TOKEN_IDENTINDEX:
            path.append(IdentifierPathElement(to_int(value)))
        elif _type == TOKEN_LBRACKET:
            stream.next_token()
            path.append(_parse_common_identifier(stream))
            stream.next_token()
            stream.expect(TOKEN_RBRACKET)
        elif _type == TOKEN_DOT:
            pass

        if stream.peek[1] in _IDENT_TOKENS:
            next(stream)
        else:
            break

    return Identifier(path)


LITERAL_OR_IDENT_TOKEN_RULES = (
    (TOKEN_IDENTINDEX, IDENTINDEX_PATTERN),
    (TOKEN_IDENTSTRING, IDENTSTRING_PATTERN),
    (TOKEN_STRING, STRING_PATTERN),
    (TOKEN_RANGE, r"\.\."),
    (TOKEN_FLOAT, r"-?\d+\.(?!\.)\d*"),
    (TOKEN_INTEGER, r"-?\d+\b"),
    (TOKEN_DOT, r"\."),
    (TOKEN_IDENTIFIER, IDENTIFIER_PATTERN),
    (TOKEN_LPAREN, r"\("),
    (TOKEN_RPAREN, r"\)"),
    (TOKEN_LBRACKET, r"\["),
    (TOKEN_RBRACKET, r"]"),
    (TOKEN_COMMA, r","),
    (TOKEN_NEWLINE, r"\n"),
    (TOKEN_SKIP, r"[ \t\r]+"),
    (TOKEN_ILLEGAL, r"."),
)

LITERAL_OR_IDENT_KEYWORDS = frozenset(
    [
        TOKEN_TRUE,
        TOKEN_FALSE,
        TOKEN_NIL,
        TOKEN_NULL,
        TOKEN_EMPTY,
        TOKEN_BLANK,
        TOKEN_OR,
    ]
)

LITERAL_OR_IDENT_MAP = {
    TOKEN_IDENTIFIER: _parse_common_identifier,
    TOKEN_STRING: parse_string_literal,
    TOKEN_INTEGER: parse_integer_literal,
    TOKEN_FLOAT: parse_float_literal,
    TOKEN_NIL: parse_nil,
    TOKEN_TRUE: parse_boolean,
    TOKEN_FALSE: parse_boolean,
    TOKEN_BLANK: parse_blank,
    TOKEN_EMPTY: parse_empty,
}

LITERAL_OR_IDENT_RE = re.compile(
    "|".join(
        f"(?P<{name}>{pattern})" for name, pattern in LITERAL_OR_IDENT_TOKEN_RULES
    ),
    re.DOTALL,
)


def tokenize_common_expression(expr: str, linenum: int = 1) -> Iterator[Token]:
    """Yield tokens from a "common" expression."""
    _keywords = LITERAL_OR_IDENT_KEYWORDS
    for match in LITERAL_OR_IDENT_RE.finditer(expr):
        kind = match.lastgroup
        assert kind is not None

        value = match.group()
        newlines = value.count("\n")

        if kind == TOKEN_IDENTIFIER and value in _keywords:
            kind = value
        elif kind == TOKEN_IDENTINDEX:
            value = match.group(GROUP_IDENTINDEX)
        elif kind == TOKEN_IDENTSTRING:
            kind = TOKEN_IDENTIFIER
            value = match.group(GROUP_IDENTQUOTED)
        elif kind == TOKEN_STRING:
            value = match.group(GROUP_QUOTED)
        elif kind == TOKEN_NEWLINE:
            linenum += 1
            continue
        elif kind == TOKEN_SKIP:
            continue
        elif kind == TOKEN_ILLEGAL:
            raise LiquidSyntaxError(f"unexpected {value!r}", linenum=linenum)

        linenum += newlines
        yield (linenum, kind, value)


def parse_common_expression(stream: TokenStream) -> Expression:
    """Parse a string, int, float, range, nil, true, false, blank, empty or identifier.

    Raises a LiquidSyntaxError if any other tokens are found.
    """
    try:
        return LITERAL_OR_IDENT_MAP[stream.current[1]](stream)
    except KeyError as err:
        raise LiquidSyntaxError(
            f"expected a literal or variable, found {stream.current[2]}",
            linenum=stream.current[0],
        ) from err


LITERAL_OR_IDENT_MAP[TOKEN_LPAREN] = make_parse_range(parse_common_expression)
