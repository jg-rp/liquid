# flake8: noqa
# pylint: disable=useless-import-alias,missing-module-docstring

__version__ = "1.1.2"

try:
    from markupsafe import escape as escape
    from markupsafe import Markup as Markup
    from markupsafe import soft_str
except ImportError:
    from liquid.exceptions import escape as escape  # type: ignore
    from liquid.exceptions import Markup as Markup  # type: ignore

    # pylint: disable=invalid-name
    soft_str = str  # type: ignore

from .mode import Mode as Mode
from .token import Token
from .expression import Expression

from .loaders import FileSystemLoader as FileSystemLoader
from .loaders import DictLoader as DictLoader
from .loaders import ChoiceLoader as ChoiceLoader

from .context import Context as Context
from .context import Undefined as Undefined
from .context import DebugUndefined as DebugUndefined
from .context import StrictUndefined as StrictUndefined
from .context import is_undefined as is_undefined

from .environment import Environment as Environment
from .environment import Template as Template
