"""Token definitions."""

import sys
from typing import NamedTuple

TOKEN_ILLEGAL = sys.intern("illegal")
TOKEN_INITIAL = sys.intern("initial")
TOKEN_EOF = sys.intern("end of expression")
TOKEN_NEWLINE = sys.intern("newline")
TOKEN_SKIP = sys.intern("skip")

TOKEN_TAG = sys.intern("tag")
TOKEN_EXPRESSION = sys.intern("expression")
TOKEN_OUTPUT = sys.intern("output")
TOKEN_CONTENT = sys.intern("content")
TOKEN_COMMENT = sys.intern("comment")
TOKEN_DOC = sys.intern("doc")

TOKEN_WORD = sys.intern("word")
TOKEN_IDENTINDEX = sys.intern("identindex")
TOKEN_IDENTSTRING = sys.intern("identstring")
TOKEN_STRING = sys.intern("string")
TOKEN_INTEGER = sys.intern("integer")
TOKEN_FLOAT = sys.intern("float")
TOKEN_EMPTY = sys.intern("empty")
TOKEN_NIL = sys.intern("nil")
TOKEN_NULL = sys.intern("null")
TOKEN_BLANK = sys.intern("blank")

# "include" and "render" keywords
TOKEN_WITH = sys.intern("with")
TOKEN_FOR = sys.intern("for")
TOKEN_AS = sys.intern("as")

# "paginate" keywords
TOKEN_BY = sys.intern("by")

TOKEN_NEGATIVE = sys.intern("negative")

TOKEN_TRUE = sys.intern("true")
TOKEN_FALSE = sys.intern("false")

# String, array and hash membership
TOKEN_CONTAINS = sys.intern("contains")

# Looping symbols and keywords. Use by `for` and `tablerow` tags.
TOKEN_IN = sys.intern("in")
TOKEN_LPAREN = sys.intern("lparen")
TOKEN_RPAREN = sys.intern("rparen")
TOKEN_RANGE = sys.intern("range")
TOKEN_RANGE_LITERAL = sys.intern("rangeexpression")
TOKEN_LIMIT = sys.intern("limit")
TOKEN_OFFSET = sys.intern("offset")
TOKEN_REVERSED = sys.intern("reversed")
TOKEN_CONTINUE = sys.intern("continue")

# Tablerow specific argument
TOKEN_COLS = sys.intern("cols")

# Template inheritance keywords
TOKEN_REQUIRED = sys.intern("required")

# Comparison symbols and logic operators for `if` and `unless` tags.
TOKEN_EQ = sys.intern("eq")
TOKEN_NE = sys.intern("ne")
TOKEN_LG = sys.intern("ltgt")
TOKEN_LT = sys.intern("lt")
TOKEN_GT = sys.intern("gt")
TOKEN_LE = sys.intern("le")
TOKEN_GE = sys.intern("ge")
TOKEN_AND = sys.intern("and")
TOKEN_OR = sys.intern("or")
TOKEN_NOT = sys.intern("not")
TOKEN_ELSE = sys.intern("else")
TOKEN_IF = sys.intern("if")


# Filter symbols
TOKEN_PIPE = sys.intern("pipe")
TOKEN_COLON = sys.intern("colon")
TOKEN_COMMA = sys.intern("comma")
TOKEN_DPIPE = sys.intern("dpipe")

# Identifier symbols
TOKEN_DOT = sys.intern("dot")
TOKEN_LBRACKET = sys.intern("lbracket")
TOKEN_RBRACKET = sys.intern("rbracket")

# Assignment
TOKEN_ASSIGN = sys.intern("assign")

# Non-standard key/value argument separator. Standard liquid uses TOKEN_COLON.
TOKEN_EQUALS = sys.intern("equals")

operators = {
    "==": TOKEN_EQ,
    "!=": TOKEN_NE,
    "<>": TOKEN_LG,
    "<": TOKEN_LT,
    ">": TOKEN_GT,
    "<=": TOKEN_LE,
    ">=": TOKEN_GE,
    "|": TOKEN_PIPE,
    ":": TOKEN_COLON,
    ",": TOKEN_COMMA,
    ".": TOKEN_DOT,
    "-": TOKEN_NEGATIVE,
    "(": TOKEN_LPAREN,
    ")": TOKEN_RPAREN,
    "..": TOKEN_RANGE,
    "[": TOKEN_LBRACKET,
    "]": TOKEN_RBRACKET,
    "=": TOKEN_ASSIGN,
}

reverse_operators = {v: k for k, v in operators.items()}


class Token(NamedTuple):
    """A substring into Liquid template source text along with its type."""

    kind: str
    """The type of the token.
    
    Could be one of `TOKEN_TAG`, `TOKEN_OUTPUT`, `TOKEN_EXPRESSION` or `TOKEN_CONTENT`
    indicating that it is a "top-level" token. All other tokens kinds are for tag and
    output expressions.
    """

    value: str
    """The substring associated with this token."""

    start_index: int
    """The index into _source_ where this token starts."""

    source: str
    """A reference to the template source text from which this token came."""

    def test(self, typ: str) -> bool:
        """Return `True` if this token's type matches the `typ` argument."""
        return self.kind == typ

    def is_tag(self, name: str) -> bool:
        """Return `True` if this token is a tag and has the given name."""
        return self.kind == TOKEN_TAG and self.value == name
