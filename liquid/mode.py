"""Template error tolerance modes."""

from enum import IntEnum
from enum import auto


class Mode(IntEnum):
    """Template correctness tolerance."""

    LAX = auto()
    WARN = auto()
    STRICT = auto()
