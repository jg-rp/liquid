"""A read-only chain map.

Based on "A greatly simplified read-only version of Chainmap" by Raymond Hettinger.
https://code.activestate.com/recipes/305268/
"""
from collections import deque
from itertools import chain

from typing import Any
from typing import Iterator
from typing import Mapping


class ReadOnlyChainMap(Mapping[str, object]):
    """Combine multiple mappings for sequential lookup."""

    def __init__(self, *maps: Mapping[str, object]):
        self._maps = deque(maps)

    def __getitem__(self, key: str) -> object:
        for mapping in self._maps:
            try:
                return mapping[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return chain(*self._maps)

    def __len__(self) -> int:
        return sum(len(map) for map in self._maps)

    def size(self) -> int:
        """Return the number of maps in the chain."""
        return len(self._maps)

    def get(self, key: str, default: object = None) -> object:
        try:
            return self[key]
        except KeyError:
            return default

    def push(self, namespace: Mapping[Any, Any]) -> None:
        """Add a mapping to the front of the chain map."""
        self._maps.appendleft(namespace)

    def pop(self) -> Mapping[Any, Any]:
        """Remove a mapping from the front of the chain map."""
        return self._maps.popleft()
