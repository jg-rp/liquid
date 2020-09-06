# distutils: language=c++
# distutils: include_dirs = src/

from libcpp.string cimport string
from libcpp.vector cimport vector

from liquid.token import Token as PyToken
from liquid.stream import TokenStream

cdef extern from "src/lex.h" namespace "liquid":
    cdef struct Token:
        unsigned int linenum
        string type
        string value

    ctypedef vector[Token] stream_t

cdef extern from "src/lex.h" namespace "liquid::lex":
    cdef cppclass Lexer:
        Lexer() except +
        Lexer(string, string, string, string) except +
        stream_t Tokenize(string&)


cdef class PyLexer:
    cdef Lexer c_lexer

    def __cinit__(self, str statement_start, str statement_end, str tag_start, str tag_end):
        self.c_lexer = Lexer()
    
    def tokenize(self, str source):
        cdef bytes source_ = source.encode()
        cdef stream_t tokens = self.c_lexer.Tokenize(source_)
        return TokenStream(iter([PyToken(tok.linenum, tok.type.decode(), tok.value.decode()) for tok in tokens]))