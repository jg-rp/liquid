"""Template output streams."""
from io import StringIO
from typing import Optional

from liquid.exceptions import OutputStreamLimitError


class LimitedStringIO(StringIO):
    """A StringIO subclass that limits the number of bytes that can be written."""

    def __init__(
        self,
        limit: int,
        initial_value: Optional[str] = None,
        newline: Optional[str] = None,
    ) -> None:
        super().__init__(initial_value, newline)
        self.limit = limit
        self.size = 0

    def write(self, __s: str) -> int:
        if __s:
            self.size += len(__s.encode("utf-8"))
            if self.size > self.limit:
                raise OutputStreamLimitError("output stream limit reached")
        return super().write(__s)
