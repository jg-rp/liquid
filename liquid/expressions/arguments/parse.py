"""Generic argument list parsers."""
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from liquid.exceptions import LiquidSyntaxError

from liquid.expression import Expression
from liquid.expression import NIL

from liquid.expressions.common import parse_unchained_identifier
from liquid.expressions.arguments.lex import tokenize
from liquid.expressions.filtered.parse import parse_obj
from liquid.expressions.stream import TokenStream

from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_EQUALS
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_STRING


Argument = Tuple[Any, Expression]


def make_parse_arguments(
    func: Callable[[TokenStream, str], Argument],
    separator_token: str = TOKEN_COLON,
) -> Callable[[TokenStream], List[Argument]]:
    """Return an argument list parser using the given function to parse
    each argument."""

    def _parse_arguments(stream: TokenStream) -> List[Argument]:
        """Parse arguments from a stream of tokens until EOF."""
        args: List[Argument] = []
        # Leading commas are OK
        if stream.current[1] == TOKEN_COMMA:
            next(stream)

        while stream.current[1] != TOKEN_EOF:
            args.append(func(stream, separator_token))
            next(stream)
            # Catch missing comma
            if stream.current[1] != TOKEN_EOF:
                stream.expect(TOKEN_COMMA)
            # Eat comma. Trailing commas are OK
            if stream.current[1] == TOKEN_COMMA:
                next(stream)

        return args

    return _parse_arguments


def parse_argument(stream: TokenStream, separator_token: str) -> Argument:
    """Parse a single keyword argument from a stream of tokens."""
    key = str(parse_unchained_identifier(stream))
    next(stream)
    stream.expect(separator_token)
    next(stream)  # Eat separator
    return key, parse_obj(stream)


parse_colon_separated_arguments = make_parse_arguments(parse_argument, TOKEN_COLON)
parse_equals_separated_arguments = make_parse_arguments(parse_argument, TOKEN_EQUALS)


def parse_keyword_arguments(expr: str, linenum: int = 1) -> Dict[str, Expression]:
    """Parse keyword or named arguments from a Liquid expression string.

    Each key/value pair is assumed to be separated by a comma. Leading and
    trailing commas are OK.

    If the same key/name appears multiple times, the last occurrence in the
    argument "list" will take priority.

    Values can be string, integer, float, true, false or nil literals, an
    identifier or a range expression. An identifier value could be chained
    using a mixture of dot and bracket notation."""
    return dict(parse_colon_separated_arguments(TokenStream(tokenize(expr, linenum))))


def parse_macro_argument(stream: TokenStream, separator_token: str) -> Argument:
    """Parse either a positional or keyword argument.

    If the separator token appears after an identifier, the argument is a keyword
    argument. Otherwise it is positional, with an expression of NIL.
    """
    key = str(parse_unchained_identifier(stream))
    if stream.peek[1] == separator_token:
        next(stream)
        # A keyword argument
        next(stream)  # Eat separator
        val = parse_obj(stream)
    else:
        # A positional argument
        val = NIL
    return key, val


def parse_call_argument(stream: TokenStream, separator_token: str) -> Argument:
    """Parse an argument value that could be preceded by a name."""
    if stream.peek[1] == separator_token:
        # A keyword argument
        key: Optional[str] = str(parse_unchained_identifier(stream))
        next(stream)
        next(stream)  # Eat separator
    else:
        # A positional argument
        key = None

    return key, parse_obj(stream)


_parse_macro_arguments = make_parse_arguments(parse_macro_argument, TOKEN_COLON)
_parse_call_arguments = make_parse_arguments(parse_call_argument, TOKEN_COLON)


def _parse_macro_name(stream: TokenStream) -> str:
    if stream.current[1] in (TOKEN_IDENTIFIER, TOKEN_STRING):
        return stream.current[2]
    raise LiquidSyntaxError(
        f"invalid macro name '{stream.current[2]}'", linenum=stream.current[0]
    )


def parse_macro_arguments(expr: str, linenum: int = 1) -> Tuple[str, List[Argument]]:
    """Parse a sequence of argument names, possibly with default values."""
    stream = TokenStream(tokenize(expr, linenum))
    name = _parse_macro_name(stream)
    next(stream)
    return name, _parse_macro_arguments(stream)


def parse_call_arguments(expr: str, linenum: int = 1) -> Tuple[str, List[Argument]]:
    """Parse a sequence of positional and/or keyword arguments."""
    stream = TokenStream(tokenize(expr, linenum))
    name = _parse_macro_name(stream)
    next(stream)
    return name, _parse_call_arguments(stream)
