from markupsafe import Markup
from markupsafe import escape
from markupsafe import soft_str

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
from .loaders import make_choice_loader
from .loaders import make_file_system_loader

from .context import RenderContext
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

from .stream import TokenStream

from . import future

__version__ = "1.13.0"

__all__ = (
    "AwareBoundTemplate",
    "BoundTemplate",
    "CachingChoiceLoader",
    "CachingFileSystemLoader",
    "ChoiceLoader",
    "RenderContext",
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
    "make_choice_loader",
    "make_file_system_loader",
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
    "TokenStream",
    "parse",
    "render",
)

DEFAULT_ENVIRONMENT = Environment()


def parse(source: str) -> BoundTemplate:
    """Parse template source text using the default environment."""
    return DEFAULT_ENVIRONMENT.from_string(source)


def render(source: str, **data: object) -> str:
    """Parse and render source text using the default environment."""
    return DEFAULT_ENVIRONMENT.from_string(source).render(**data)
