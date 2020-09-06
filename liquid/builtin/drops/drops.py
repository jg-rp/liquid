import collections.abc
from abc import ABC


class IterableDrop(ABC, collections.abc.Collection):
    """Inherit from this class if you want the drop to be iterable from
    tags like 'include' and 'render'."""
