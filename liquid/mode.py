import warnings

from enum import IntEnum, auto

from typing import Union
from typing import Optional
from typing import Type

from liquid.exceptions import Error
from liquid.exceptions import lookup_warning


class Mode(IntEnum):
    """Template correctness tolerance."""

    LAX = auto()
    WARN = auto()
    STRICT = auto()


def error(
    tolerance: Mode,
    exc: Union[Type[Error], Error],
    msg: Optional[str] = None,
    linenum: Optional[int] = None,
) -> None:
    """Raise an exception or warning according to the given mode."""
    if not isinstance(exc, Error):
        exc = exc(msg, linenum=linenum)
    elif not exc.linenum:
        exc.linenum = linenum

    if tolerance == Mode.STRICT:
        raise exc
    if tolerance == Mode.WARN:
        warnings.warn(str(exc), category=lookup_warning(exc.__class__))
