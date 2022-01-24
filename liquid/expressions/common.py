"""Patterns and parse functions common to multiple built-in expression types."""
import sys

from typing import Callable
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
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_RBRACKET
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_RANGE
from liquid.token import TOKEN_STRING

from liquid.exceptions import LiquidSyntaxError

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
    return IntegerLiteral(value=int(stream.current[2]))


def parse_float_literal(stream: "TokenStream") -> FloatLiteral:
    """Read a float from the token stream."""
    return FloatLiteral(value=float(stream.current[2]))


IDENT_TOKENS = frozenset(
    (
        TOKEN_IDENTIFIER,
        TOKEN_IDENTINDEX,
        TOKEN_LBRACKET,
        TOKEN_DOT,
    )
)


def parse_identifier(stream: "TokenStream") -> Identifier:
    """Read an identifier from the token stream.

    An identifier might be chained with dots and square brackets, and might contain
    more, possibly chained, identifiers within those brackets.
    """
    path: IdentifierPath = []
    stream.expect(TOKEN_IDENTIFIER)

    while True:
        pos, typ, val = stream.current
        if typ == TOKEN_IDENTIFIER:
            path.append(IdentifierPathElement(val))
        elif typ == TOKEN_IDENTINDEX:
            path.append(IdentifierPathElement(int(val)))
        elif typ == TOKEN_LBRACKET:
            stream.next_token()
            path.append(parse_identifier(stream))
            # Eat close bracket
            stream.next_token()
            stream.expect(TOKEN_RBRACKET)
        elif typ == TOKEN_FLOAT:
            raise LiquidSyntaxError(
                f"expected and identifier, found {val!r}",
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
    if typ == TOKEN_IDENTIFIER:
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
