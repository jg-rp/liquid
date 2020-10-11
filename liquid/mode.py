import warnings

from enum import IntEnum, auto

from typing import Union
from typing import Optional
from typing import Type

from liquid.exceptions import Error
from liquid.exceptions import lookup_warning


class Mode(IntEnum):
    """Template correctness tolerence."""

    LAX = auto()
    WARN = auto()
    STRICT = auto()


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
