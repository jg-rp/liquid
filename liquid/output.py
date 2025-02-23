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

    def write(self, __s: str) -> int:  # noqa: D102
        if __s:
            self.size += len(__s.encode("utf-8"))
            if self.size > self.limit:
                raise OutputStreamLimitError("output stream limit reached", token=None)
        return super().write(__s)


class NullIO(StringIO):
    """A StringIO subclass that is a null op. It doesn't write anything."""

    def write(self, _s: str) -> int:
        """Pretend to write the string to the stream."""
        return 0
