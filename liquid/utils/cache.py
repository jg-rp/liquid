"""A simple LRU Cache implementation.

Coppied from https://github.com/pallets/jinja/blob/master/src/jinja2/utils.py
BSD-3-Clause License
"""
from collections import abc, deque
from threading import Lock


class LRUCache(abc.MutableMapping):
    """A simple LRU Cache implementation."""

    # this is fast for small capacities (something below 1000) but doesn't
    # scale.  But as long as it's only used as storage for templates this
    # won't do any harm.

    def __init__(self, capacity):
        self.capacity = capacity
        self._mapping = {}
        self._queue = deque()
        self._postinit()

    def _postinit(self):
        # alias all queue methods for faster lookup
        self._popleft = self._queue.popleft
        self._pop = self._queue.pop
        self._remove = self._queue.remove
        self._wlock = Lock()
        self._append = self._queue.append

    def __getstate__(self):
        return {
            "capacity": self.capacity,
            "_mapping": self._mapping,
            "_queue": self._queue,
        }

    def __setstate__(self, d):
        self.__dict__.update(d)
        self._postinit()

    def __getnewargs__(self):
        return (self.capacity,)

    def copy(self):
        """Return a shallow copy of the instance."""
        rv = self.__class__(self.capacity)
        rv._mapping.update(self._mapping)
        rv._queue.extend(self._queue)
        return rv

    def get(self, key: str, default: object = None):
        """Return an item from the cache dict or `default`"""
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self, key, default=None):
        """Set `default` if the key is not in the cache otherwise
        leave unchanged. Return the value of this key.
        """
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def clear(self):
        """Clear the cache."""
        self._wlock.acquire()
        try:
            self._mapping.clear()
            self._queue.clear()
        finally:
            self._wlock.release()

    def __contains__(self, key):
        """Check if a key exists in this cache."""
        return key in self._mapping

    def __len__(self):
        """Return the current size of the cache."""
        return len(self._mapping)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self._mapping!r}>"

    def __getitem__(self, key):
        """Get an item from the cache. Moves the item up so that it has the
        highest priority then.
        Raise a `KeyError` if it does not exist.
        """
        self._wlock.acquire()
        try:
            rv = self._mapping[key]
            if self._queue[-1] != key:
                try:
                    self._remove(key)
                except ValueError:
                    # if something removed the key from the container
                    # when we read, ignore the ValueError that we would
                    # get otherwise.
                    pass
                self._append(key)
            return rv
        finally:
            self._wlock.release()

    def __setitem__(self, key, value):
        """Sets the value for an item. Moves the item up so that it
        has the highest priority then.
        """
        self._wlock.acquire()
        try:
            if key in self._mapping:
                self._remove(key)
            elif len(self._mapping) == self.capacity:
                del self._mapping[self._popleft()]
            self._append(key)
            self._mapping[key] = value
        finally:
            self._wlock.release()

    def __delitem__(self, key):
        """Remove an item from the cache dict.
        Raise a `KeyError` if it does not exist.
        """
        self._wlock.acquire()
        try:
            del self._mapping[key]
            try:
                self._remove(key)
            except ValueError:
                pass
        finally:
            self._wlock.release()

    def items(self):
        """Return a list of items."""
        result = [(key, self._mapping[key]) for key in list(self._queue)]
        result.reverse()
        return result

    def values(self):
        """Return a list of all values."""
        return [x[1] for x in self.items()]

    def keys(self):
        """Return a list of all keys ordered by most recent usage."""
        return list(self)

    def __iter__(self):
        return reversed(tuple(self._queue))

    def __reversed__(self):
        """Iterate over the keys in the cache dict, oldest items
        coming first.
        """
        return iter(tuple(self._queue))

    __copy__ = copy
