"""Liquid template render context."""
from __future__ import annotations

import collections.abc
import datetime
import functools
import itertools
import warnings

from collections import deque
from contextlib import contextmanager
from functools import reduce
from operator import getitem
from itertools import cycle

from typing import (
    Any,
    Union,
    Callable,
    List,
    Mapping,
    Iterator,
    Sequence,
)

from liquid.exceptions import NoSuchFilterFunc, ContextDepthError, Error, lookup_warning
from liquid.filter import Filter
from liquid import Mode

MAX_CONTEXT_DEPTH = 30

ContextPath = Union[str, Sequence[Union[str, int]]]
Namespace = Mapping[str, Any]


class ReadOnlyChainMap(collections.abc.Mapping):
    """Combine multiple mappings for sequential lookup.

    For example, to emulate Python's normal lookup sequence:

        import __builtin__
        pylookup = Chainmap(locals(), globals(), vars(__builtin__))
    """

    def __init__(self, *maps):
        self._maps = deque(maps)

    def __getitem__(self, key):
        for mapping in self._maps:
            try:
                return mapping[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __iter__(self):
        return itertools.chain(*self._maps)

    def __len__(self):
        return sum(len(map) for map in self._maps)

    def size(self):
        """Return the number of maps in the chain."""
        return len(self._maps)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def push(self, namespace: Mapping[Any, Any]):
        self._maps.appendleft(namespace)

    def pop(self) -> Mapping[Any, Any]:
        return self._maps.popleft()


class BuiltIn(collections.abc.Mapping):
    """Mapping-like object for resolving built-in, dynamic objects."""

    def __contains__(self, item):
        if item in ("now", "today"):
            return True
        return False

    def __getitem__(self, key):
        if key == "now":
            return datetime.datetime.now()
        if key == "today":
            return datetime.date.today()
        raise KeyError(str(key))

    def __len__(self):
        return 2

    def __iter__(self):
        return iter(["now", "today"])


builtin = BuiltIn()

# pylint: disable=too-many-instance-attributes redefined-builtin
class Context:
    """Liquid template context."""

    __slots__ = (
        "env",
        "locals",
        "globals",
        "scope",
        "cycles",
        "counters",
        "disabled_tags",
    )

    def __init__(
        self,
        env,
        globals: Namespace = None,
        disabled_tags: List[str] = None,
    ):
        self.env = env

        # The namespace for local variables. Those that are bound with `assign`
        # or `capture`.
        self.locals = {}

        # Read only namespace containing globally available variables. Usually
        # passed down from the environment.
        self.globals = globals or {}

        # Namespaces are searched in this order. When a context is extended, the
        # temporary namespace is pushed to the front of this scope.
        self.scope = ReadOnlyChainMap(self.locals, self.globals, builtin)

        # A distinct namespace for iterables created by the built-in "cycle" tag.
        self.cycles = {}

        # A namespace for integer counters. The built-in increment and decrement
        # tags share this namespace.
        self.counters = {}

        # A list of tags names that are disallowed in this context. For example,
        # partial tags rendered using the "render" tag are not allowed to use
        # "include" tags.
        self.disabled_tags = disabled_tags or []

    def assign(self, key: str, val: Any):
        """Add `val` to the context with key `key`."""
        self.locals[key] = val

    def get(self, path: ContextPath, default: Any = None) -> Any:
        """Return the value at path `path` if it is in scope, else default."""
        if isinstance(path, str):
            return self.resolve(path, default)

        name, items = path[0], path[1:]
        assert isinstance(name, str)

        obj = self.resolve(name, default)

        if items:
            return get_item(obj, *items, default=default)
        return obj

    def resolve(self, name: str, default=None) -> Any:
        try:
            return self.scope[name]
        except KeyError:
            return default

    def filter(self, name: str) -> Callable:
        """Returns a filter function with given name."""
        filter_func = self.env.filters.get(name)

        if not filter_func:
            raise NoSuchFilterFunc(name)

        if isinstance(filter_func, Filter) and filter_func.with_context:
            return functools.partial(filter_func, context=self)

        return filter_func

    def increment(self, name: str) -> int:
        """Increment the named counter and return it's value."""
        val = self.counters.get(name, -1) + 1
        self.counters[name] = val
        return val

    def decrement(self, name: str) -> int:
        """Decrement the named counter and return it's value."""
        val = self.counters.get(name, 0) - 1
        self.counters[name] = val
        return val

    def cycle(self, group_name: str, args: Sequence[Any]) -> Iterator[Any]:
        """Return the next item in the given cycle. Initialise the cycle first
        if this is is the first time we're seeing this combination of group name
        and arguments."""
        key = f"{group_name}:{''.join([str(arg) for arg in args])}"
        if key not in self.cycles:
            self.cycles[key] = cycle(args)
        return self.cycles[key]

    @contextmanager
    def extend(self, namespace: Namespace):
        """Extend this context with the given read-only namespace."""
        if self.scope.size() > MAX_CONTEXT_DEPTH:
            raise ContextDepthError(
                "maximum context depth reached, possible recursive include"
            )

        self.scope.push(namespace)

        try:
            yield self
        finally:
            self.scope.pop()

    def copy(self, namespace: Namespace, disabled_tags: List[str] = None) -> Context:
        """Return a copy of this context without any local variables."""
        return Context(
            self.env,
            globals=ReadOnlyChainMap(namespace, self.globals),
            disabled_tags=disabled_tags,
        )

    def error(self, exc: Error):
        if self.env.mode == Mode.STRICT:
            raise exc
        if self.env.mode == Mode.WARN:
            warnings.warn(str(exc), category=lookup_warning(exc.__class__))


def _getitem(obj, key):
    """Item getter with special methods for arrays/lists and hashes/dicts."""
    if key == "size" and isinstance(obj, collections.abc.Sized):
        return len(obj)
    if key == "first" and isinstance(obj, collections.abc.Sequence):
        return obj[0]
    if key == "last" and isinstance(obj, collections.abc.Sequence):
        return obj[-1]

    return getitem(obj, key)


def get_item(obj, *items: Union[str, int], default=None) -> Any:
    """Chained item getter."""
    try:
        return reduce(_getitem, items, obj)
    except (KeyError, IndexError, TypeError):
        return default
