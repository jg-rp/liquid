"""Template error tolerance modes."""

from enum import IntEnum
from enum import auto


class Mode(IntEnum):
    """Template error tolerance mode."""

    LAX = auto()
    WARN = auto()
    STRICT = auto()
