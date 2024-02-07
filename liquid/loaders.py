"""Built-in loaders."""
from .builtin.loaders import BaseLoader
from .builtin.loaders import CachingChoiceLoader
from .builtin.loaders import CachingFileSystemLoader
from .builtin.loaders import ChoiceLoader
from .builtin.loaders import DictLoader
from .builtin.loaders import FileExtensionLoader
from .builtin.loaders import FileSystemLoader
from .builtin.loaders import PackageLoader
from .builtin.loaders import TemplateNamespace
from .builtin.loaders import TemplateSource
from .builtin.loaders import UpToDate
from .builtin.loaders import make_choice_loader
from .builtin.loaders import make_file_system_loader

__all__ = (
    "BaseLoader",
    "CachingChoiceLoader",
    "CachingFileSystemLoader",
    "ChoiceLoader",
    "DictLoader",
    "FileExtensionLoader",
    "FileSystemLoader",
    "make_choice_loader",
    "make_file_system_loader",
    "PackageLoader",
    "TemplateNamespace",
    "TemplateSource",
    "UpToDate",
)
