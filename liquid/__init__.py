# flake8: noqa
# pylint: disable=missing-module-docstring

__version__ = "1.8.1"

try:
    from markupsafe import escape
    from markupsafe import Markup
    from markupsafe import soft_str
except ImportError:
    from liquid.exceptions import escape  # type: ignore
    from liquid.exceptions import Markup  # type: ignore

    # pylint: disable=invalid-name
    soft_str = str  # type: ignore

from .mode import Mode
from .token import Token
from .expression import Expression

from .loaders import ChoiceLoader
from .loaders import DictLoader
from .loaders import FileExtensionLoader
from .loaders import FileSystemLoader

from .context import Context
from .context import DebugUndefined
from .context import is_undefined
from .context import FutureContext
from .context import StrictDefaultUndefined
from .context import StrictUndefined
from .context import Undefined

from .environment import Environment
from .environment import Template

from .template import AwareBoundTemplate
from .template import BoundTemplate
from .template import FutureAwareBoundTemplate
from .template import FutureBoundTemplate

from .analyze_tags import TagAnalysis
from .analyze_tags import DEFAULT_INNER_TAG_MAP

from . import future

__all__ = (
    "AwareBoundTemplate",
    "BoundTemplate",
    "ChoiceLoader",
    "Context",
    "DebugUndefined",
    "DEFAULT_INNER_TAG_MAP",
    "DictLoader",
    "Environment",
    "escape",
    "Expression",
    "FileExtensionLoader",
    "FileSystemLoader",
    "future",
    "FutureBoundTemplate",
    "FutureAwareBoundTemplate",
    "FutureContext",
    "is_undefined",
    "Markup",
    "Mode",
    "soft_str",
    "StrictDefaultUndefined",
    "StrictUndefined",
    "TagAnalysis",
    "Template",
    "Token",
    "Undefined",
)
