"""A read-only chain map.

Based on "A greatly simplified read-only version of Chainmap" by Raymond Hettinger.
https://code.activestate.com/recipes/305268/
"""

from collections import deque
from collections.abc import Iterator, Mapping
from itertools import chain

MISSING = object()


class ReadOnlyChainMap(Mapping[str, object]):
    """Combine multiple mappings for sequential lookup.

    This chain map never raises a KeyError. It returns the MISSING sentinel
    if a key does not exist in the chain.
    """

    def __init__(self, *maps: Mapping[str, object]):
        self._maps = deque(maps)

    def __getitem__(self, key: str) -> object:
        for mapping in self._maps:
            if key in mapping:
                return mapping[key]
        return MISSING

    def __iter__(self) -> Iterator[str]:
        return chain(*self._maps)

    def __len__(self) -> int:
        return sum(len(_map) for _map in self._maps)

    def size(self) -> int:
        return len(self._maps)

    def get(self, key: str, default: object = MISSING) -> object:
        return self[key]

    def push(self, namespace: Mapping[str, object]) -> None:
        self._maps.appendleft(namespace)

    def pop(self) -> Mapping[str, object]:
        return self._maps.popleft()
