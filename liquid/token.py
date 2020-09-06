"""Token definitions"""

import sys
from typing import NamedTuple


WHITESPACE = frozenset(" \t\n\r\x0b\x0c")

TOKEN_ILLEGAL = sys.intern("illegal")
TOKEN_INITIAL = sys.intern("initial")
TOKEN_EOF = sys.intern("eof")

TOKEN_EXPRESSION = sys.intern("expression")
TOKEN_TAG_START = sys.intern("tag_begin")
TOKEN_TAG_END = sys.intern("tag_end")
TOKEN_TAG_NAME = sys.intern("tag")
TOKEN_STATEMENT_START = sys.intern("statement_begin")
TOKEN_STATEMENT_END = sys.intern("statement_end")
TOKEN_STATEMENT = sys.intern("statement")
TOKEN_LITERAL = sys.intern("literal")

TOKEN_WHITESPACE = sys.intern("whitespace")
TOKEN_WHITESPACE_CONTROL = sys.intern("-")

TOKEN_IDENTIFIER = sys.intern("identifier")
TOKEN_STRING = sys.intern("string")
TOKEN_INTEGER = sys.intern("integer")
TOKEN_FLOAT = sys.intern("float")
TOKEN_EMPTY = sys.intern("empty")
TOKEN_NIL = sys.intern("nil")

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
TOKEN_LIMIT = sys.intern("limit")
TOKEN_OFFSET = sys.intern("offset")
TOKEN_REVERSED = sys.intern("reversed")

# Tablerow specific argument
TOKEN_COLS = sys.intern("cols")

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

# Filter symbols
TOKEN_PIPE = sys.intern("pipe")
TOKEN_COLON = sys.intern("colon")
TOKEN_COMMA = sys.intern("comma")

# Identifier symbols
TOKEN_DOT = sys.intern("dot")
TOKEN_LBRACKET = sys.intern("lbracket")
TOKEN_RBRACKET = sys.intern("rbracket")

# Assignment
TOKEN_ASSIGN = sys.intern("assign")

token_types = {
    1: TOKEN_STATEMENT_START,
    2: TOKEN_STATEMENT_END,
    3: TOKEN_TAG_START,
    4: TOKEN_TAG_END,
    5: TOKEN_STATEMENT,
    6: TOKEN_TAG_NAME,
    7: TOKEN_EXPRESSION,
    8: TOKEN_LITERAL,
    9: TOKEN_EOF,
}

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

keywords = {
    "true": TOKEN_TRUE,
    "false": TOKEN_FALSE,
    "nil": TOKEN_NIL,
    "and": TOKEN_AND,
    "or": TOKEN_OR,
    "contains": TOKEN_CONTAINS,
    "in": TOKEN_IN,
    "limit": TOKEN_LIMIT,
    "offset": TOKEN_OFFSET,
    "reversed": TOKEN_REVERSED,
    "cols": TOKEN_COLS,
    "empty": TOKEN_EMPTY,
    "with": TOKEN_WITH,
    "for": TOKEN_FOR,
    "as": TOKEN_AS,
    "by": TOKEN_BY,
}


class Token(NamedTuple):
    linenum: int
    type: str
    value: str

    def test(self, typ: str) -> bool:
        return self.type == typ

    def istag(self, name: str) -> bool:
        return self.type == TOKEN_TAG_NAME and self.value == name
