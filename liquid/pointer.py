"""Template string pointer used by lexers."""

import re

from liquid.token import TOKEN_EOF


# pylint: disable=too-many-instance-attributes
class Pointer:
    """Lexer state. Holds the current character and index into a source string.

    Args:
        source: The template source.
        linenum: A starting number for the line counter.
    """

    def __init__(self, source: str, linenum: int = 1):
        self.source = source
        self.len = len(source)

        self.idx = -1
        self.next_idx = 0
        self.ch = ""

        # Line counter. Increments with every "\n" char read. XXX:
        self.linecount = linenum
        self.linenum = 1

        # Populate self.ch with the first character.
        self.read_char()

    def read_char(self) -> None:
        """Move the pointer forward one character."""
        if self.next_idx >= self.len:
            self.ch = TOKEN_EOF
        else:
            self.ch = self.source[self.next_idx]

        self.idx = self.next_idx
        self.next_idx += 1

        if self.ch == "\n":
            self.linecount += 1

    def _jump(self, idx: int):
        # Fix the line count after the jump. If we were already on a newline
        # it will already have been counted (hence next_idx rather than idx).
        # If `pattern` matches a newline, we'll need to count that too (hence
        # start + 1 rather than start).
        self.linecount += self.source.count("\n", self.next_idx, idx + 1)

        # Jump to the first character if the match.
        if idx >= self.len:
            self.ch = TOKEN_EOF
            self.idx = self.len
        else:
            self.ch = self.source[idx]
            self.idx = idx
            self.next_idx = idx + 1

    def _jump_to_eof(self):
        self.idx = self.len
        self.ch = TOKEN_EOF

    def jump_to_pattern(self, pattern: re.Pattern, or_eof: bool = True) -> str:
        """Advance the pointer to the next occurrence of the given pattern.

        Args:
            pattern: Compiled pattern to search for.
            or_eof: When `True`, will jump to the end of the string if no match
                was found for the given pattern.
        Returns:
            The sub string that matched the given pattern, or an empty string if
            there was no match.
        """
        match = pattern.search(self.source, pos=self.idx)

        if match:
            self._jump(match.start())
            return match.group()

        if or_eof:
            self._jump_to_eof()

        return ""

    def jump_to(self, sub: str, or_eof: bool = True) -> bool:
        """Advances the pointer to the next occurrence of the given substring.

        Args:
            sub: Substring to find.
            or_eof: When `True`, will jump to the end of the string if the
                substring is not found.
        Returns:
            `True` if the substring was found, `False` otherwise.
        """
        idx = self.source.find(sub, self.idx)

        if idx >= 0:
            self._jump(idx)
            return True

        if or_eof:
            self._jump_to_eof()

        return False

    def eat(self, pattern: re.Pattern) -> str:
        """Advance the pointer past any characters matched by the given pattern.

        Returns:
            The sequence of characters that matched the given pattern. Or an
            empty string if no match was found.
        """
        match = pattern.match(self.source, pos=self.idx)

        if match:
            self._jump(match.end())
            return match.group()

        return ""

    def peek(self, n=1) -> str:
        """Return upcoming characters without advancing the pointer.

        Args:
            n: Number of characters past the current index to peek at.
        Returns:
            A single character at idx + n, or TOKEN_EOF if idx + n goes past
            the end of the source string.
        """
        if self.idx + n >= self.len:
            return TOKEN_EOF
        return self.source[self.idx + n]

    # pylint: disable=invalid-name
    def at(self, seq: str) -> bool:
        """Return True if we are pointing at the given sequence of characters."""
        n = len(seq)

        if n == 1:
            return self.ch == seq

        if self.idx + n > self.len:
            return False

        return seq == self.source[self.idx : self.idx + n]

    def at_pattern(self, pattern: re.Pattern) -> bool:
        """Return `True` if we are pointing at the given pattern."""
        return bool(pattern.match(self.source, pos=self.idx))
