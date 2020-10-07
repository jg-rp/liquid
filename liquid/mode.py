import warnings

from enum import IntEnum, auto
from pathlib import Path
from typing import Union, Optional, Type

from liquid.exceptions import Error, lookup_warning


class Mode(IntEnum):
    """Template correctness tolerence."""

    LAX = auto()
    WARN = auto()
    STRICT = auto()


class mode:
    def __init__(
        self,
        tolerence: Mode,
        linenum: int,
        filename: Optional[Union[str, Path]] = None,
    ):
        self.mode: Mode = tolerence
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


def error(
    tolerence: Mode,
    exc: Union[Type[Error], Error],
    msg: Optional[str] = None,
    linenum: Optional[int] = None,
):
    """Raise an exception or warning according to the given mode."""
    if not isinstance(exc, Error):
        exc = exc(msg, linenum=linenum)
    elif not exc.linenum:
        exc.linenum = linenum

    if tolerence == Mode.STRICT:
        raise exc
    if tolerence == Mode.WARN:
        warnings.warn(str(exc), category=lookup_warning(exc.__class__))
