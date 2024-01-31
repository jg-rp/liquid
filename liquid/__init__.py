try:
    from markupsafe import Markup
    from markupsafe import escape
    from markupsafe import soft_str
except ImportError:
    from liquid.exceptions import Markup  # type: ignore
    from liquid.exceptions import escape  # type: ignore

    soft_str = str  # type: ignore

from .mode import Mode
from .token import Token
from .expression import Expression

from .loaders import CachingChoiceLoader
from .loaders import CachingFileSystemLoader
from .loaders import ChoiceLoader
from .loaders import DictLoader
from .loaders import FileExtensionLoader
from .loaders import FileSystemLoader
from .loaders import PackageLoader

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

from .static_analysis import TemplateAnalysis
from .static_analysis import ContextualTemplateAnalysis

from . import future

__version__ = "1.11.0"

__all__ = (
    "AwareBoundTemplate",
    "BoundTemplate",
    "CachingChoiceLoader",
    "CachingFileSystemLoader",
    "ChoiceLoader",
    "Context",
    "ContextualTemplateAnalysis",
    "DebugUndefined",
    "DEFAULT_INNER_TAG_MAP",
    "DictLoader",
    "Environment",
    "escape",
    "Expression",
    "FileExtensionLoader",
    "FileSystemLoader",
    "future",
    "FutureAwareBoundTemplate",
    "FutureBoundTemplate",
    "FutureContext",
    "is_undefined",
    "Markup",
    "Mode",
    "PackageLoader",
    "soft_str",
    "StrictDefaultUndefined",
    "StrictUndefined",
    "TagAnalysis",
    "Template",
    "TemplateAnalysis",
    "Token",
    "Undefined",
)
