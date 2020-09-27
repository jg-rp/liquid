import collections.abc
from abc import ABC, abstractmethod
from typing import Any, TextIO


class IterableDrop(ABC, collections.abc.Collection):
    """Inherit from this class if you want the drop to be iterable from
    tags like 'include' and 'render'."""

    @abstractmethod
    def step(self, item: Any):
        """Step the iterator."""

    def step_write(self, item: Any, buffer: TextIO):
        """Step the iterator and write auxiliary text to buffer."""
        self.step(item)

    def empty_exit_buffer(self, buffer: TextIO):
        """Write auxiliary text on StopIteration."""
