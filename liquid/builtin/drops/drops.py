"""Legacy iterable drop base class."""
from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Collection


class IterableDrop(ABC, Collection[Any]):
    """Base class for drops that can be iterated with `include` and `render` tags."""

    @abstractmethod
    def step(self, item: Any) -> None:
        """Step the iterator."""
