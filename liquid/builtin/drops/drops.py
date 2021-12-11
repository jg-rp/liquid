"""Legacy iterable drop base class."""
from typing import Any
from typing import Collection
from abc import ABC
from abc import abstractmethod


# pylint: disable=too-few-public-methods
class IterableDrop(ABC, Collection[Any]):
    """Inherit from this class if you want the drop to be iterable from
    tags like 'include' and 'render'."""

    @abstractmethod
    def step(self, item: Any) -> None:
        """Step the iterator."""
