from enum import IntEnum, auto
import warnings

from liquid.exceptions import Error, lookup_warning


class Mode(IntEnum):
    """Template correctness tolerence."""

    LAX = auto()
    WARN = auto()
    STRICT = auto()


class mode:
    def __init__(self, _mode: Mode, linenum: int, filename=None) -> None:
        self.mode: Mode = _mode
        self.linenum = linenum
        self.filename = filename

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb) -> bool:
        if isinstance(exc_value, Error):
            exc_value.filename = self.filename
            if not exc_value.linenum:
                exc_value.linenum = self.linenum

        if exc_type is not None and self.mode == Mode.WARN:
            warnings.warn(str(exc_value), category=lookup_warning(exc_type))
            return True

        return self.mode < Mode.STRICT
