"""An LRU cache with a mapping interface implemented using an ordered dict."""

from collections import OrderedDict
from collections.abc import Iterator
from threading import Lock
from typing import overload


class LRUCache[KT, VT]:
    """An LRU cache with a mapping interface."""

    def __init__(self, capacity: int):
        if capacity < 1:
            raise ValueError("cache capacity must be greater than zero")

        self.capacity = capacity
        self._cache: OrderedDict[KT, VT] = OrderedDict()

    def __getitem__(self, key: KT) -> VT:
        value = self._cache[key]  # This will raise a KeyError if key is not cached
        self._cache.move_to_end(key)
        return value

    def __setitem__(self, key: KT, value: VT) -> None:
        try:
            self._cache.move_to_end(key)
        except KeyError:
            if len(self._cache) >= self.capacity:
                self._cache.popitem(last=False)

        self._cache[key] = value

    def __delitem__(self, key: KT) -> None:
        del self._cache[key]

    def __len__(self) -> int:
        return len(self._cache)

    def __iter__(self) -> Iterator[KT]:
        return reversed(self._cache)

    def __contains__(self, key: KT) -> bool:
        return key in self._cache

    @overload
    def get(self, key: KT) -> VT | None: ...
    @overload
    def get(self, key: KT, default: VT) -> VT: ...
    @overload
    def get[T](self, key: KT, default: T) -> VT | T: ...
    def get(self, key: KT, default: object = None) -> object:
        """Return the cached value for _key_ if _key_ is in the cache, else default."""
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self) -> Iterator[KT]:
        """Return an iterator over this cache's keys."""
        return reversed(self._cache.keys())

    def values(self) -> Iterator[VT]:
        """Return an iterator over this cache's values."""
        return reversed(self._cache.values())

    def items(self) -> Iterator[tuple[KT, VT]]:
        """Return an iterator over this cache's key/value pairs."""
        return reversed(self._cache.items())


class ThreadSafeLRUCache[KT, VT](LRUCache[KT, VT]):
    """A thread safe LRU cache."""

    def __init__(self, capacity: int):
        super().__init__(capacity)
        self._lock = Lock()

    def __getitem__(self, key: KT) -> VT:
        with self._lock:
            return super().__getitem__(key)

    def __setitem__(self, key: KT, value: VT) -> None:
        with self._lock:
            return super().__setitem__(key, value)

    def __delitem__(self, key: KT) -> None:
        with self._lock:
            return super().__delitem__(key)

    def __contains__(self, key: KT) -> bool:
        with self._lock:
            return super().__contains__(key)

    @overload
    def get(self, key: KT) -> VT | None: ...
    @overload
    def get(self, key: KT, default: VT) -> VT: ...
    @overload
    def get[T](self, key: KT, default: T) -> VT | T: ...
    def get(self, key: KT, default: object = None) -> object:
        """Return the cached value for _key_ if _key_ is in the cache, else default."""
        # NOTE: self.__getitem__ is already acquiring the lock.
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self) -> Iterator[KT]:
        """Return an iterator over this cache's keys."""
        with self._lock:
            return super().keys()

    def values(self) -> Iterator[VT]:
        """Return an iterator over this cache's values."""
        with self._lock:
            return super().values()

    def items(self) -> Iterator[tuple[KT, VT]]:
        """Return an iterator over this cache's key/value pairs."""
        with self._lock:
            return super().items()
