class StringBuffer:
    """An output text buffer that keeps track of its own length."""

    def __init__(self) -> None:
        self._parts: list[str] = []
        self._length = 0

    def write(self, s: str) -> None:
        """Write `s` to the buffer."""
        self._parts.append(s)
        self._length += len(s)

    def __len__(self) -> int:
        return self._length

    def getvalue(self) -> str:
        """Return the contents of the buffer."""
        return "".join(self._parts)
