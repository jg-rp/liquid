"""Liquid specific Excpeptions and wanrings."""

from typing import Dict
from typing import Type
from typing import Optional
from typing import Union

from pathlib import Path


class Error(Exception):
    def __init__(
        self,
        *args: object,
        linenum: Optional[int] = None,
        filename: Optional[Union[str, Path]] = None,
    ):
        self.linenum = linenum
        self.filename = filename
        super().__init__(*args)

    def __str__(self):
        msg = super().__str__()
        if self.linenum:
            msg = f"{msg}, on line {self.linenum}"
        if self.filename:
            msg += f" of {self.filename}"
        return msg


class LiquidInterrupt(Exception):
    """Loop interrupt"""


class LiquidSyntaxError(Error):
    """Exception raised when there is a parser error."""


class LiquidTypeError(Error):
    """Exception raised when an error occurs at render time."""


class LiquidKeyError(Error):
    """Exception raised when an undefined variable is accessed."""


class DisabledTagError(Error):
    """Exception raised when an attempt is made to render a disabled tag."""


class NoSuchFilterFunc(Error):
    """Exception raised when a filter lookup fails."""


class FilterArgumentError(Error):
    """Exception raised when a filters arguments are invalid."""


class TemplateNotFound(Error):
    """Excpetions raised when a template could not be found."""

    def __str__(self):
        msg = super().__str__()
        msg = f"template not found {msg}"
        return msg


class ContextDepthError(Error):
    """Exception raised when the maximum context depth is reached."""


class BreakLoop(LiquidInterrupt):
    """Exception raised when a BreakNode is rendered."""


class ContinueLoop(LiquidInterrupt):
    """Exception raised when a ContinueNode is rendered."""


class LiquidWarning(UserWarning):
    """Base warning."""


class LiquidSyntaxWarning(LiquidWarning):
    """Replaces LiquidSyntaxError when in WARN mode."""


class LiquidTypeWarning(LiquidWarning):
    """Replaces LiquidTypeError when in WARN mode."""


class FilterWarning(LiquidWarning):
    """Replaces filter exceptions when in WARN mode."""


class OpcodeError(Error):
    """Exceptions raised when there is an opcode definition error."""


class StackOverflow(Error):
    """Exception raised when the stack is full."""


WARNINGS: Dict[Type[Error], Type[LiquidWarning]] = {
    LiquidSyntaxError: LiquidSyntaxWarning,
    LiquidTypeError: LiquidTypeWarning,
    FilterArgumentError: FilterWarning,
    NoSuchFilterFunc: FilterWarning,
}


def lookup_warning(exc: Type[Error]) -> Type[LiquidWarning]:
    return WARNINGS.get(exc, LiquidWarning)
