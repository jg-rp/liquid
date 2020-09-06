# cython: language_level=3

from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from cpython cimport array
import array

ctypedef unsigned int uint
# ctypedef unsigned int[:] src_t
ctypedef const uint* src_t
ctypedef (uint, uint) slice_t

ctypedef enum TokenType:
    STATEMENT_START = 1
    STATEMENT_END = 2
    TAG_START = 3
    TAG_END = 4
    END_DELIM = 5
    STATEMENT = 6
    TAG = 6
    EXPRESSION = 7
    LITERAL = 8
    EOF = 9

ctypedef uint[4] Token


cdef uint[6] ENDRAW = [ord("e"), ord("n"), ord("d"), ord("r"), ord("a"), ord("w")]

cdef inline bint at_stmt(src_t source, uint pos, const Py_ssize_t n):
    """Return `True` if source[pos] is at the statement start sequence."""
    cdef bint result = False
    if pos + 1 < n:
        result = source[pos] == ord("{") and source[pos + 1] == ord("{")
    return result

cdef inline bint at_close_stmt(src_t source, uint pos, const Py_ssize_t n):
    if pos + 2 < n and source[pos] == ord("-") and source[pos + 1] == ord("}") and source[pos + 2] == ord("}"):
        return True
    
    if pos + 1 < n and source[pos] == ord("}") and source[pos + 1] == ord("}"):
        return True

    return False

cdef inline bint at_close_tag(src_t source, uint pos, const Py_ssize_t n):
    if pos + 2 < n and source[pos] == ord("-") and source[pos + 1] == ord("%") and source[pos + 2] == ord("}"):
        return True
    
    if pos + 1 < n and source[pos] == ord("%") and source[pos + 1] == ord("}"):
        return True

    return False

cdef inline bint at_tag(src_t source, uint pos, const Py_ssize_t n):
    """Return `True` if source[pos] is at the tag start sequence."""
    if pos + 1 >= n:
        return False
    return source[pos] == ord("{") and source[pos + 1] == ord("%")

cdef inline bint at_whitespace(src_t source, uint pos, const Py_ssize_t n):
    if source[pos] == ord("\n") or source[pos] == ord("\t") or source[pos] == ord(" ") or source[pos] == ord("\r"):
        return True
    return False

cdef inline void eat_whitespace(src_t source, uint *pos, const Py_ssize_t n):
    """Advance to the next non-whitespace character."""
    while source[pos[0]] == ord("\n") or source[pos[0]] == ord("\t") or source[pos[0]] == ord(" ") or source[pos[0]] == ord("\r"):
        if pos[0] + 1 < n:
            pos[0] += 1

cdef inline slice_t read_start(src_t source, uint *pos, const Py_ssize_t n):
    """Advance passed the current statement or tag start sequence."""
    cdef uint start_pos = pos[0]
    if pos[0] + 2 >= n:
        return (pos[0], n-1)
    
    pos[0] += 2

    if source[pos[0]] == ord("-") and pos[0] + 1 < n:
        pos[0] += 1

    eat_whitespace(source, pos, n)
    return (start_pos, pos[0])

cdef inline slice_t read_end(src_t source, uint *pos, const Py_ssize_t n):
    """Advance passed the current statement or tag end sequence."""
    cdef uint start_pos = pos[0]

    eat_whitespace(source, pos, n)

    if not at_close_stmt(source, pos[0], n) and not at_close_tag(source, pos[0], n):
        return (start_pos, pos[0])

    if source[pos[0]] == ord("-") and pos[0] < n:
        pos[0] += 1

    if pos[0] < n:
        pos[0] += 2
    return (start_pos, pos[0])

cdef inline slice_t read_statement(src_t source, uint *pos, const Py_ssize_t n):
    """Return start and end positions of characters up to the next end statement sequence."""
    cdef uint start_pos = pos[0]
    while not at_close_stmt(source, pos[0], n) and pos[0] < n:
        pos[0] += 1
    return (start_pos, pos[0])

cdef inline slice_t read_tag_name(src_t source, uint *pos, const Py_ssize_t n):
    """Return start and end positions of characters up to the next whitespace or close tag sequence."""
    cdef uint start_pos = pos[0]
    while not at_whitespace(source, pos[0], n) and not at_close_tag(source, pos[0], n) and pos[0] < n:
        pos[0] += 1
    return (start_pos, pos[0])

cdef inline slice_t read_expression(src_t source, uint *pos, const Py_ssize_t n):
    """Return start and end positions of characters up to the next close tag sequence."""
    eat_whitespace(source, pos, n)
    cdef uint start_pos = pos[0]
    while not at_close_tag(source, pos[0], n) and pos[0] < n:
        pos[0] += 1
    return (start_pos, pos[0])

cdef inline slice_t read_literal(src_t source, uint *pos, const Py_ssize_t n):
    """Return start and end positions of characters up to the next start tag or start statement sequence."""
    cdef uint start_pos = pos[0]
    while not at_stmt(source, pos[0], n) and not at_tag(source, pos[0], n) and pos[0] < n:
        pos[0] += 1
    return (start_pos, pos[0])

cdef inline bint is_raw(src_t source, uint start, uint end):
    if end - start != 3:
        return False
    if source[start] == ord("r") and source[start + 1] == ord("a") and source[start+2] == ord("w"):
        return True
    return False

cdef inline slice_t peek_tag_name(src_t source, uint pos, const Py_ssize_t n):
    # Move past the open tag characters.
    # XXX: Assumes open tag is two characters.
    cdef int idx = pos + 2

    while at_whitespace(source, idx, n) and idx < n:
        idx += 1

    cdef int name_idx = idx

    while not at_whitespace(source, idx, n) and not at_close_tag(source, idx, n) and idx < n:
        idx += 1

    return (name_idx, idx)

cdef inline bint at_endraw(src_t source, uint pos, const Py_ssize_t n):
    if not at_tag(source, pos, n):
        return False

    cdef unsigned int start
    cdef unsigned int end
    start, end = peek_tag_name(source, pos, n)
    if end - start != 6:
        return False

    cdef Py_ssize_t j = 0
    for i in range(start, end):
        if source[i] != ENDRAW[j]:
            return False
        j += 1

    return True

cdef inline slice_t read_raw(src_t source, uint *pos, const Py_ssize_t n):
    cdef uint start_pos = pos[0]
    while not at_endraw(source, pos[0], n) and pos[0] < n:
        pos[0] += 1
    return (start_pos, pos[0])


cdef inline unsigned int count_lines(src_t source, unsigned int start, unsigned int end):
    cdef unsigned int n = 0
    for i in range(start, end):
        if source[i] == ord("\n"):
            n += 1
    return n

def tokenize(str source):
    cdef Py_ssize_t size = len(source)
    cdef array.array src_a = array.array('I', source.encode("utf-32le"))
    cdef src_t src = src_a.data.as_uints

    cdef uint pos = 0
    cdef uint linenum = 1

    cdef uint cap = 200
    cdef Token *tokens = <Token *> PyMem_Malloc(cap * sizeof(Token))

    if not tokens:
        raise MemoryError()

    cdef uint ti = 0
    cdef uint start, end

    try:
        while pos < size:
            if at_stmt(src, pos, size):
                start, end = read_start(src, &pos, size)
                tokens[ti] = (linenum, TokenType.STATEMENT_START, start, end)
                linenum += count_lines(src, start, end)
                ti +=1

                start, end = read_statement(src, &pos, size)
                tokens[ti] = (linenum, TokenType.STATEMENT, start, end)
                linenum += count_lines(src, start, end)
                ti +=1

                start, end = read_end(src, &pos, size)
                tokens[ti] = (linenum, TokenType.STATEMENT_END, start, end)
                linenum += count_lines(src, start, end)
                ti +=1
            elif at_tag(src, pos, size):
                start, end = read_start(src, &pos, size)
                tokens[ti] = (linenum, TokenType.TAG_START, start, end)
                linenum += count_lines(src, start, end)
                ti +=1

                start, end = read_tag_name(src, &pos, size)
                tokens[ti] = (linenum, TokenType.TAG, start, end)
                linenum += count_lines(src, start, end)
                ti +=1

                if is_raw(src, start, end):
                    start, end = read_expression(src, &pos, size)
                    tokens[ti] = (linenum, TokenType.EXPRESSION, start, end)
                    linenum += count_lines(src, start, end)
                    ti +=1

                    start, end = read_end(src, &pos, size)
                    tokens[ti] = (linenum, TokenType.TAG_END, start, end)
                    linenum += count_lines(src, start, end)
                    ti +=1

                    start, end = read_raw(src, &pos, size)
                    tokens[ti] = (linenum, TokenType.LITERAL, start, end)
                    linenum += count_lines(src, start, end)
                    ti +=1
                else:
                    start, end = read_expression(src, &pos, size)
                    tokens[ti] = (linenum, TokenType.EXPRESSION, start, end)
                    linenum += count_lines(src, start, end)
                    ti +=1

                    start, end = read_end(src, &pos, size)
                    tokens[ti] = (linenum, TokenType.TAG_END, start, end)
                    linenum += count_lines(src, start, end)
                    ti +=1

            else:
                start, end = read_literal(src, &pos, size)
                tokens[ti] = (linenum, TokenType.LITERAL, start, end)
                linenum += count_lines(src, start, end)
                ti += 1

            if ti > cap - 10:
                cap *= 2
                mem = <Token *> PyMem_Realloc(tokens, cap * sizeof(Token))
                if not mem:
                    raise MemoryError()
                tokens = mem
                

        tokens[ti] = (linenum, TokenType.EOF, 0, 0)
        ti += 1
        return [tokens[i] for i in range(ti)]
    finally:
        PyMem_Free(tokens)


