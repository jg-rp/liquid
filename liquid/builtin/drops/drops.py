import collections.abc
from abc import ABC, abstractmethod
from typing import Any


class IterableDrop(ABC, collections.abc.Collection):
    """Inherit from this class if you want the drop to be iterable from
    tags like 'include' and 'render'."""

    @abstractmethod
    def step(self, item: Any):
        """Step the iterator."""
