"""Liquid specific Exceptions and warnings."""

from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional
from typing import Type
from typing import Union


class Error(Exception):
    """Base class for all Liquid exceptions."""

    def __init__(
        self,
        *args: object,
        linenum: Optional[int] = None,
        filename: Optional[Union[str, Path]] = None,
    ):
        self.linenum = linenum
        self.filename = filename
        super().__init__(*args)

    def __str__(self) -> str:
        msg = super().__str__()
        if self.linenum:
            msg = f"{msg}, on line {self.linenum}"
        if self.filename:
            msg += f" of {self.filename}"
        return msg

    @property
    def message(self) -> object:
        """The exception's error message if one was given."""
        if self.args:
            return self.args[0]
        return None

    @property
    def name(self) -> str:
        """The name of the template that raised this exception.

        An empty string is return if a name is not available.
        """
        if isinstance(self.filename, Path):
            return self.filename.as_posix()
        if self.filename:
            return str(self.filename)
        return ""


class LiquidInterrupt(Exception):
    """Loop interrupt exception."""


class StopRender(Exception):
    """Template inheritance interrupt.

    An interrupt used to signal that `BoundTemplate.render_with_context` should stop
    rendering more nodes. This is used by template inheritance tags and is not an error
    condition.
    """


class LiquidEnvironmentError(Error):
    """An exception raised due to a misconfigured environment."""


class LiquidSyntaxError(Error):
    """Exception raised when there is a parser error."""

    def __init__(
        self,
        *args: object,
        linenum: Optional[int] = None,
        filename: Optional[Union[str, Path]] = None,
    ):
        super().__init__(*args, linenum=linenum, filename=filename)
        self.source: Optional[str] = None


class TemplateInheritanceError(Error):
    """An exceptions raised when template inheritance tags are used incorrectly.

    This could occur when parsing a template or at render time.
    """

    def __init__(
        self,
        *args: object,
        linenum: Optional[int] = None,
        filename: Optional[Union[str, Path]] = None,
    ):
        super().__init__(*args, linenum=linenum, filename=filename)
        self.source: Optional[str] = None


class RequiredBlockError(TemplateInheritanceError):
    """An exception raised when a required block has not been overridden."""


class LiquidTypeError(Error):
    """Exception raised when an error occurs at render time."""


class DisabledTagError(Error):
    """Exception raised when an attempt is made to render a disabled tag."""


class NoSuchFilterFunc(Error):
    """Exception raised when a filter lookup fails."""


class FilterError(Error):
    """Exception raised when a filter fails."""


class FilterArgumentError(Error):
    """Exception raised when a filter's arguments are invalid."""


class FilterValueError(Error):
    """Exception raised when a filters value is invalid."""


class FilterItemTypeError(Error):
    """Exception raised when an array item causes a type error when filtered."""


class TemplateNotFound(Error):
    """Exception raised when a template could not be found."""

    def __str__(self) -> str:
        msg = super().__str__()
        return f"template not found {msg}"


class ResourceLimitError(Error):
    """Base class for exceptions relating to resource limits."""


class ContextDepthError(ResourceLimitError):
    """Exception raised when the maximum context depth is reached.

    Usually indicates recursive use of `render` or `include` tags.
    """


class LoopIterationLimitError(ResourceLimitError):
    """Exception raised when the loop iteration limit has been exceeded."""


class OutputStreamLimitError(ResourceLimitError):
    """Exception raised when an output stream limit has been exceeded."""


class LocalNamespaceLimitError(ResourceLimitError):
    """Exception raised when a local namespace limit has been exceeded."""


# LiquidValueError inheriting from LiquidSyntaxError does not make complete sense.
# The alternative is to have multiple to_int functions that raise more appropriate
# exceptions depending on whether we are parsing or rendering when attempting to
# convert long strings to integers.


class LiquidValueError(LiquidSyntaxError):
    """Exception raised when a cast from str to int exceeds the length limit."""


class UndefinedError(Error):
    """Exception raised by the StrictUndefined type."""


class BreakLoop(LiquidInterrupt):
    """Exception raised when a BreakNode is rendered."""


class ContinueLoop(LiquidInterrupt):
    """Exception raised when a ContinueNode is rendered."""


class TemplateTraversalError(Error):
    """Exception raised when an AST node or expression can not be visited."""


class LiquidWarning(UserWarning):
    """Base warning."""


class LiquidSyntaxWarning(LiquidWarning):
    """Replaces LiquidSyntaxError when in WARN mode."""


class LiquidTypeWarning(LiquidWarning):
    """Replaces LiquidTypeError when in WARN mode."""


class FilterWarning(LiquidWarning):
    """Replaces filter exceptions when in WARN mode."""


WARNINGS: Dict[Type[Error], Type[LiquidWarning]] = {
    LiquidSyntaxError: LiquidSyntaxWarning,
    LiquidTypeError: LiquidTypeWarning,
    FilterArgumentError: FilterWarning,
    NoSuchFilterFunc: FilterWarning,
}


def lookup_warning(exc: Type[Error]) -> Type[LiquidWarning]:
    """Return a warning equivalent of the given exception."""
    return WARNINGS.get(exc, LiquidWarning)


def escape(_: Any) -> str:
    """A dummy escape function that always raises an exception."""
    raise Error("autoescape requires Markupsafe to be installed")


class Markup(str):
    """A dummy markup class that always raises an exception."""

    def __init__(self, _: object):
        super().__init__()
        raise Error("autoescape requires Markupsafe to be installed")

    def join(self, _: object) -> str:  # noqa: D102
        raise Error(
            "autoescape requires Markupsafe to be installed"
        )  # pragma: no cover

    def unescape(self) -> str:  # noqa: D102
        raise Error(
            "autoescape requires Markupsafe to be installed"
        )  # pragma: no cover

    def format(self, *args: Any, **kwargs: Any) -> str:  # noqa: A003, D102, ARG002
        raise Error(
            "autoescape requires Markupsafe to be installed"
        )  # pragma: no cover


class CacheCapacityValueError(ValueError):
    """An exception raised when the LRU cache is given a zero or negative capacity."""
