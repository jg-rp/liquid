"""Liquid template render context."""

from __future__ import annotations

import collections.abc
import datetime
import functools
import itertools
import warnings

from collections import deque
from contextlib import contextmanager
from itertools import cycle
from operator import getitem

from typing import Any
from typing import Union
from typing import Callable
from typing import List
from typing import Mapping
from typing import Iterator
from typing import Sequence
from typing import Optional
from typing import TYPE_CHECKING

from liquid.exceptions import NoSuchFilterFunc
from liquid.exceptions import ContextDepthError
from liquid.exceptions import Error
from liquid.exceptions import lookup_warning

from liquid import Mode

if TYPE_CHECKING:
    from liquid import Environment
    from liquid import Template

# Maximum number of times a context can be extended or wrapped.
MAX_CONTEXT_DEPTH = 30

ContextPath = Union[str, Sequence[Union[str, int]]]
Namespace = Mapping[str, object]


class ReadOnlyChainMap(collections.abc.Mapping):
    """Combine multiple mappings for sequential lookup.

    Based on the "A greatly simplified read-only version of Chainmap" recipe link to
    from https://docs.python.org/3/library/collections.html#chainmap-examples-and-recipes.

    The link seems to be broken.
    """

    def __init__(self, *maps: Mapping[str, object]):
        self._maps = deque(maps)

    def __getitem__(self, key: str):
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

    def get(self, key: str, default: object = None):
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

    def __contains__(self, item: str) -> bool:
        if item in ("now", "today"):
            return True
        return False

    def __getitem__(self, key: str) -> object:
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
        env: Environment,
        globals: Optional[Namespace] = None,
        disabled_tags: Optional[List[str]] = None,
    ):
        self.env = env

        # A namespace for template local variables. Those that are bound with
        # `assign` or `capture`.
        self.locals = {}

        # A read-only namespace containing globally available variables. Usually
        # passed down from the environment.
        self.globals = globals or {}

        # Namespaces are searched in this order. When a context is extended, the
        # temporary namespace is pushed to the front of this chain.
        self.scope = ReadOnlyChainMap(self.locals, self.globals, builtin)

        # A distinct namespace for iterables created by the built-in "cycle" tag.
        self.cycles = {}

        # A namespace for integer counters. The built-in increment and decrement
        # tags share this namespace.
        self.counters = {}

        # A list of tags names that are disallowed in this context. For example,
        # partial templates rendered using the "render" tag are not allowed to
        # use "include" tags.
        self.disabled_tags = disabled_tags or []

    def assign(self, key: str, val: Any):
        """Add `val` to the context with key `key`."""
        self.locals[key] = val

    def get(self, path: ContextPath, default: object = None) -> object:
        """Return the value at path `path` if it is in scope, else default."""
        if isinstance(path, str):
            return self.resolve(path, default)

        name, items = path[0], path[1:]
        assert isinstance(name, str)

        obj = self.resolve(name, default)

        if items:
            return get_item(obj, *items, default=default)
        return obj

    def resolve(self, name: str, default: object = None) -> Any:
        """Return the object/value at `name` in the current scope.

        This is like `get`, but does a single, top-level lookup rather than a
        chained lookup from sequence of keys.
        """
        try:
            return self.scope[name]
        except KeyError:
            # TODO: Resolve mode.
            return default

    @functools.lru_cache(maxsize=128)
    def filter(self, name: str) -> Callable[..., object]:
        """Return the filter function with given name."""
        try:
            filter_func = self.env.filters[name]
        except KeyError as err:
            raise NoSuchFilterFunc(name) from err

        if getattr(filter_func, "with_context", False):
            return functools.partial(filter_func, context=self)

        return filter_func

    def get_template(self, name: str) -> Template:
        """Load a template from the environment."""
        return self.env.get_template(name)

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

    def copy(
        self, namespace: Namespace, disabled_tags: Optional[List[str]] = None
    ) -> Context:
        """Return a copy of this context without any local variables."""
        return Context(
            self.env,
            globals=ReadOnlyChainMap(namespace, self.globals),
            disabled_tags=disabled_tags,
        )

    def error(self, exc: Error):
        """Ignore, raise or convert the given exception to a warning."""
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


def get_item(
    obj: object,
    *items: Union[str, int],
    default: Optional[object] = None,
) -> Any:
    """Chained item getter."""
    try:
        itm: Any = functools.reduce(_getitem, items, obj)
    except (KeyError, IndexError, TypeError):
        itm = default
    return itm
