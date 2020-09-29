"""Liquid template render context/environment."""
from __future__ import annotations

import collections.abc
import datetime
import functools
import itertools

from collections import deque
from functools import reduce
from operator import getitem
from itertools import cycle
from typing import Any, Union, Callable, Optional, List, Mapping, Iterable, Iterator

from liquid.exceptions import NoSuchFilterFunc, ContextDepthError
from liquid.filter import Filter
from liquid import hash_identifier

MAX_CONTEXT_DEPTH = 30


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

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def push(self, namespace: Mapping[Any, Any]):
        self._maps.appendleft(namespace)

    def pop(self) -> Mapping[Any, Any]:
        return self._maps.popleft()


# pylint: disable=too-many-instance-attributes
class Context:
    """Liquid template context."""

    __slots__ = (
        "_builtin",
        "locals",
        "globals",
        "scopes",
        "_filters",
        "_filters_by_hash",
        "cycles",
        "counters",
        "_disabled_tags",
        "outer",
        "block_scope",
        "_depth",
    )

    def __init__(
        self,
        global_objects: Mapping[str, Any] = None,
        filters: dict = None,
        disabled_tags: List[str] = None,
        outer: Context = None,
        block_scope: bool = False,
    ):

        # A namespace for built in, dynamic objects. Current date and time, for example.
        self._builtin = BuiltIn()

        # The namespace for local variables. Those that are bound with `assign`
        # or `capture`.
        self.locals = {}

        # Read only namespace containing globally available variables. Usually
        # passed down from the environment.
        self.globals = global_objects or {}

        # Namespace order of resolution. The local namespace is checked before the
        # global namespace, potentially overriding names in the global namespace.
        self.scopes = ReadOnlyChainMap(self.locals, self.globals, self._builtin)

        # Map of filter names to filter functions.
        self._filters = filters or {}

        # A distinct namespace for cycle tags. The cycle tag render function
        # manages the getting and setting of itertools.cycle instances.
        self.cycles = {}

        # A namespace for simple integer counters. The built in increment and decrement
        # tags share this namespace.
        self.counters = {}

        # A list of tags names that will raise an exception if an associated node
        # is rendered in this context.
        self._disabled_tags = disabled_tags or []

        # An enclosing render context. self.get() falls back to self.outer.get()
        # if its not None.
        self.outer = outer

        # When block_scope is False, assigns to this context will be delegated to the
        # outer context, if one exists.
        #
        # The common case for built in block tags is to temporarilty extend a context
        # whilst maintaining the enclosing local namespace, both for getting and
        # setting variables.
        self.block_scope = block_scope

        self._depth = 1

    def assign(self, key: str, val: Any):
        """Add `val` to the context with key `key`."""
        if self.outer and not self.block_scope:
            self.outer.assign(key, val)
        else:
            self.locals[key] = val

    def get(self, path: Union[str, List[Union[str, int]]], default: Any = None) -> Any:
        """Return the value at path `path` if it is in scope, else default."""
        if isinstance(path, str):
            path = [path]

        # Does the top level object (the first key in path) exist in this context?
        val, exists = nested_get(path, self.scopes)

        # The path could exist, but hold a None (or "nil"). If that's the case,
        # we'll return the default value after the following two conditions are
        # False.
        if val is not None:
            return val

        # Don't work our way back up the context chain if the start of the path
        # matched any scope in this context.
        if self.outer and not exists:
            return self.outer.get(path, default)

        # warnings.warn(f"default of '{default}' used at '{path}'")
        return default

    def filter(self, name: Union[str, int]) -> Callable:
        """Returns a filter function with name `name`."""
        filter_func = self._filters.get(name)
        if not filter_func and self.outer:
            filter_func = self.outer.filter(name)

        if not filter_func:
            raise NoSuchFilterFunc(name)

        if isinstance(filter_func, Filter) and filter_func.with_context:
            return functools.partial(filter_func, context=self)

        return filter_func

    def increment(self, name: Union[str, int]) -> int:
        val = self.counters.get(name, -1) + 1
        self.counters[name] = val
        return val

    def decrement(self, name: Union[str, int]) -> int:
        val = self.counters.get(name, 0) - 1
        self.counters[name] = val
        return val

    def cycle(self, group_name, args) -> Iterator[Any]:
        key = f"{group_name}:{''.join([str(arg) for arg in args])}"
        if key not in self.cycles:
            self.cycles[key] = cycle(args)
        return self.cycles[key]

    def extend(self, namespace: Mapping[str, Any]):
        if self._depth > MAX_CONTEXT_DEPTH:
            raise ContextDepthError(
                "maximum context depth reached, possible recursive include"
            )
        return ReadOnlyContext(self, namespace)

    def copy(
        self, namespace: Mapping[str, Any], disabled_tags: List[str] = None
    ) -> Context:
        """Return a copy of this context without any local variables."""
        return Context(
            global_objects=ReadOnlyChainMap(namespace, self.globals),
            filters=self._filters,
            disabled_tags=disabled_tags,
        )

    @property
    def disabled_tags(self):
        return self._disabled_tags


class ReadOnlyContext(Context):
    """A read-only namespace that defers variable assignments and filter lookups to it's parent."""

    __slots__ = ("outer", "namespace", "scopes")

    def __init__(self, outer: Context, namespace: Mapping[str, Any]):
        self.outer = outer
        self.namespace = namespace
        self.scopes = ReadOnlyChainMap(self.namespace)

        # Context chain length for detecting recursive includes.
        self._depth = outer._depth + 1

    def assign(self, key: str, val: Any):
        self.outer.assign(key, val)

    def filter(self, name: str) -> Optional[Callable]:
        return self.outer.filter(name)

    def increment(self, name: str) -> int:
        return self.outer.increment(name)

    def decrement(self, name: str) -> int:
        return self.outer.decrement(name)

    def cycle(self, group_name, args) -> Iterable[Any]:
        return self.outer.cycle(group_name, args)

    def copy(
        self, namespace: Mapping[str, Any], disabled_tags: List[str] = None
    ) -> Context:
        return self.outer.copy(namespace, disabled_tags=disabled_tags)

    @property
    def disabled_tags(self):
        return self.outer.disabled_tags


def _getitem(obj, key):
    """Item getter with special methods for arrays/lists and hashes/dicts."""
    # TODO: abc instead of list/dixt/str
    if isinstance(obj, list):
        if obj and key == "first":
            return obj[0]
        if obj and key == "last":
            return obj[-1]
        if key == "size":
            return len(obj)
        if not isinstance(key, int):
            raise KeyError(str(key))

    if isinstance(obj, (dict, str)) and key == "size":
        return len(obj)

    return getitem(obj, key)


def nested_get(keys: List[Union[str, int]], scope: Mapping[Any, Any]) -> Any:
    """Repeatedly lookup keys in a dictionary-like object. Returns None if the
    path does not exist in `scope`.

    If scope is `{"a": {"b": {"c": "foo"}}}`, then `nested_get(["a", "b", "c"], scope)`
    should return "foo".
    """
    exists = keys[0] in scope
    try:
        return reduce(_getitem, keys, scope), exists
    except (KeyError, IndexError, TypeError):
        return None, exists


class BuiltIn(collections.abc.Mapping):
    """"""

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
        return 3

    def __iter__(self):
        return iter(["now", "today"])
