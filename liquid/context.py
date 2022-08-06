"""Liquid template render context."""

from __future__ import annotations

import collections.abc
import datetime
import itertools
import re
import sys
import warnings

from collections import deque
from contextlib import contextmanager

from functools import lru_cache
from functools import partial
from functools import reduce

from itertools import cycle
from io import StringIO

from operator import getitem
from operator import mul

from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import TextIO
from typing import Union
from typing import TYPE_CHECKING

from liquid.exceptions import NoSuchFilterFunc
from liquid.exceptions import ContextDepthError
from liquid.exceptions import Error
from liquid.exceptions import LocalNamespaceLimitError
from liquid.exceptions import LoopIterationLimitError
from liquid.exceptions import UndefinedError
from liquid.exceptions import lookup_warning

from liquid import Mode
from liquid.output import LimitedStringIO

if TYPE_CHECKING:  # pragma: no cover
    from liquid import Environment
    from liquid.template import BoundTemplate
    from liquid.builtin.tags.for_tag import ForLoop


ContextPath = Union[str, Sequence[Union[str, int]]]
Namespace = Mapping[str, object]

_undefined = object()


# pylint: disable=too-many-return-statements
def _getitem(obj: Any, key: Any) -> Any:
    """Item getter with special methods for arrays/lists and hashes/dicts."""
    # NOTE: A runtime checkable protocol was too slow.
    if hasattr(key, "__liquid__"):
        key = key.__liquid__()

    if key == "size":
        try:
            return getitem(obj, "size")
        except (KeyError, IndexError, TypeError):
            if isinstance(obj, collections.abc.Sized):
                return len(obj)
            raise

    if key == "first" and not isinstance(obj, str):
        try:
            return getitem(obj, "first")
        except (KeyError, IndexError, TypeError):
            if isinstance(obj, collections.abc.Mapping) and obj:
                return list(itertools.islice(obj.items(), 1))[0]
            if isinstance(obj, collections.abc.Sequence):
                return obj[0]
            raise

    if key == "last" and not isinstance(obj, str):
        try:
            return getitem(obj, "last")
        except (KeyError, IndexError, TypeError):
            if isinstance(obj, collections.abc.Sequence):
                return obj[-1]
            raise

    return getitem(obj, key)


# pylint: disable=too-many-return-statements
async def _getitem_async(obj: Any, key: Any) -> object:
    """Item getter with special methods for arrays/lists and hashes/dicts."""
    # NOTE: A runtime checkable protocol was too slow.
    if hasattr(key, "__liquid__"):
        key = key.__liquid__()

    if key == "size":
        try:
            return (
                await obj.__getitem_async__(key)
                if hasattr(obj, "__getitem_async__")
                else getitem(obj, "size")
            )
        except (KeyError, IndexError, TypeError):
            if isinstance(obj, collections.abc.Sized):
                return len(obj)
            raise

    if key == "first" and not isinstance(obj, str):
        try:
            return (
                await obj.__getitem_async__(key)
                if hasattr(obj, "__getitem_async__")
                else getitem(obj, "first")
            )
        except (KeyError, IndexError, TypeError):
            if isinstance(obj, collections.abc.Mapping) and obj:
                return list(itertools.islice(obj.items(), 1))[0]
            if isinstance(obj, collections.abc.Sequence):
                return obj[0]
            raise

    if key == "last" and not isinstance(obj, str):
        try:
            return (
                await obj.__getitem_async__(key)
                if hasattr(obj, "__getitem_async__")
                else getitem(obj, "last")
            )
        except (KeyError, IndexError, TypeError):
            if isinstance(obj, collections.abc.Sequence):
                return obj[-1]
            raise

    if hasattr(obj, "__getitem_async__"):
        return await obj.__getitem_async__(key)

    return getitem(obj, key)


def get_item(
    obj: Sequence[Any],
    *items: Any,
    default: Optional[object] = _undefined,
) -> Any:
    """Chained item getter."""
    try:
        itm: Any = reduce(_getitem, items, obj)
    except (KeyError, IndexError, TypeError):
        itm = default
    return itm


def is_undefined(obj: object) -> bool:
    """Return `True` if `obj` is undefined. `False` otherwise."""
    return isinstance(obj, Undefined)


class ReadOnlyChainMap(Mapping[str, object]):
    """Combine multiple mappings for sequential lookup.

    Based on the "A greatly simplified read-only version of Chainmap" recipe linked
    to from https://docs.python.org/3/library/collections.html under the section
    chainmap-examples-and-recipes. The link seems to be broken.
    """

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
        return itertools.chain(*self._maps)

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


class BuiltIn(Mapping[str, object]):
    """Mapping-like object for resolving built-in, dynamic objects."""

    def __contains__(self, item: object) -> bool:
        if item in ("now", "today"):
            return True
        return False

    def __getitem__(self, key: str) -> object:
        if key == "now":
            return datetime.datetime.now()
        if key == "today":
            return datetime.date.today()
        raise KeyError(str(key))

    def __len__(self) -> int:
        return 2

    def __iter__(self) -> Iterator[str]:
        return iter(["now", "today"])


builtin = BuiltIn()


class Undefined(Mapping[Any, object]):
    """The default undefined type. Always evaluates to an empty string. Can be iterated
    over and indexed without error.
    """

    __slots__ = ("name", "obj", "hint")

    def __init__(self, name: str, obj: object = _undefined, hint: Optional[str] = None):
        self.name = name
        self.obj = obj
        self.hint = hint

    def __contains__(self, item: object) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Undefined) or other is None

    def __getitem__(self, key: str) -> object:
        return self

    def __len__(self) -> int:
        return 0

    def __iter__(self) -> Iterator[Any]:
        return iter([])

    def __str__(self) -> str:
        return ""

    def __repr__(self) -> str:  # pragma: no cover
        return f"Undefined({self.name})"

    def __int__(self) -> int:
        return 0

    def __hash__(self) -> int:
        return hash(self.name)

    def __reversed__(self) -> Iterable[Any]:
        return []


class DebugUndefined(Undefined):
    """An undefined that returns debug information when rendered."""

    __slots__ = ()

    def __str__(self) -> str:
        if self.hint:
            return f"undefined: {self.hint}"
        if self.obj is not _undefined:
            return f"{type(self.obj).__name__} has no attribute '{self.name}'"
        return f"'{self.name}' is undefined"

    def __repr__(self) -> str:  # pragma: no cover
        return f"Undefined({self.name})"


class StrictUndefined(Undefined):
    """An undefined that raises an exception for everything other than ``repr``."""

    __slots__ = ("msg",)

    # Properties that don't raise an UndefinedError.
    allowed_properties = frozenset(
        [
            "__repr__",
            "name",
            "hint",
            "obj",
            "msg",
        ]
    )

    def __init__(self, name: str, obj: object = _undefined, hint: Optional[str] = None):
        super().__init__(name, obj=obj, hint=hint)
        self.msg = self.hint if self.hint else f"'{self.name}' is undefined"

    def __getattribute__(self, name: str) -> object:
        if name in object.__getattribute__(self, "allowed_properties"):
            return object.__getattribute__(self, name)
        raise UndefinedError(object.__getattribute__(self, "msg"))

    def __contains__(self, item: object) -> bool:
        raise UndefinedError(self.msg)

    def __eq__(self, other: object) -> bool:
        raise UndefinedError(self.msg)

    def __getitem__(self, key: str) -> object:
        raise UndefinedError(self.msg)

    def __len__(self) -> int:
        raise UndefinedError(self.msg)

    def __iter__(self) -> Iterator[Any]:
        raise UndefinedError(self.msg)

    def __str__(self) -> str:
        raise UndefinedError(self.msg)

    def __repr__(self) -> str:
        return f"StrictUndefined({self.name})"

    def __bool__(self) -> bool:
        raise UndefinedError(self.msg)

    def __int__(self) -> int:
        raise UndefinedError(self.msg)

    def __hash__(self) -> int:
        raise UndefinedError(self.msg)

    def __reversed__(self) -> Iterable[Any]:
        raise UndefinedError(self.msg)


class StrictDefaultUndefined(StrictUndefined):
    """An undefined that plays nicely with the `default` filter."""

    # Properties that don't raise an UndefinedError.
    allowed_properties = frozenset(
        [
            "__repr__",
            "__liquid__",
            "__class__",
            "name",
            "hint",
            "obj",
            "msg",
        ]
    )


# pylint: disable=too-many-instance-attributes redefined-builtin too-many-public-methods
class Context:
    """Liquid template context."""

    __slots__ = (
        "env",
        "locals",
        "globals",
        "counters",
        "scope",
        "loops",
        "tag_namespace",
        "disabled_tags",
        "autoescape",
        "_copy_depth",
        "parent_context",
        "loop_iteration_carry",
        "local_namespace_size_carry",
    )

    getitem = _getitem
    getitem_async = _getitem_async

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        env: Environment,
        globals: Optional[Namespace] = None,
        disabled_tags: Optional[List[str]] = None,
        copy_depth: int = 0,
        parent_context: Optional[Context] = None,
        loop_iteration_carry: int = 1,
        local_namespace_size_carry: int = 0,
    ):
        self.env = env

        # A namespace for template local variables. Those that are bound with
        # `assign` or `capture`.
        self.locals: Dict[str, Any] = {}

        # A read-only namespace containing globally available variables. Usually
        # passed down from the environment.
        self.globals = globals or {}

        # A namespace for `increment` and `decrement` counters.
        self.counters: Dict[str, int] = {}

        # Namespaces are searched in this order. When a context is extended, the
        # temporary namespace is pushed to the front of this chain.
        self.scope = ReadOnlyChainMap(self.locals, self.globals, builtin, self.counters)

        # A namespace supporting stateful tags. Such as `cycle`, `increment`,
        # `decrement` and `ifchanged`.
        self.tag_namespace: Dict[str, Any] = {
            "cycles": {},
            "ifchanged": "",
            "stopindex": {},
        }

        # As stack of forloop objects. Used for populating forloop.parentloop.
        self.loops: List[ForLoop] = []

        # A list of tags names that are disallowed in this context. For example,
        # partial templates rendered using the "render" tag are not allowed to
        # use "include" tags.
        self.disabled_tags = disabled_tags or []

        # Indicates if HTML auto-escaping is enabled.
        self.autoescape = self.env.autoescape

        # Count of the number of times `copy` was called in creating this context. This
        # helps us guard against recursive use of the "render" tag, or at least fail
        # gracefully.
        self._copy_depth = copy_depth

        # A reference to a parent render context, if this one has been copied.
        self.parent_context = parent_context

        # A loop iteration count carried over from a parent context, if this one has
        # been copied. This helps us adhere to loop iteration limits in templates
        # rendered with the `render` tag.
        self.loop_iteration_carry = loop_iteration_carry

        # The cumulative number of names in parent render context local namespaces. We
        # use this to adhere to local namespace limits when copying a render context.
        self.local_namespace_size_carry = local_namespace_size_carry

    def assign(self, key: str, val: Any) -> None:
        """Add `val` to the context with key `key`."""
        self.locals[key] = val
        if (
            self.env.local_namespace_limit
            and self._get_size_of_locals() > self.env.local_namespace_limit
        ):
            raise LocalNamespaceLimitError("local namespace limit reached")

    def _get_size_of_locals(self) -> int:
        if not self.env.local_namespace_limit:
            return 0
        return (
            sum(sys.getsizeof(obj, default=1) for obj in set(self.locals.values()))
            + self.local_namespace_size_carry
        )

    def get(self, path: ContextPath, default: object = _undefined) -> object:
        """Return the value at path `path` if it is in scope, else default."""
        if isinstance(path, str):
            return self._resolve(path, default)

        name, items = path[0], path[1:]
        assert isinstance(name, str)
        obj = self._resolve(name, default)

        if items:
            try:
                return reduce(Context.getitem, items, obj)
            except (KeyError, IndexError, TypeError) as err:
                if isinstance(err, KeyError):
                    hint = (
                        f"key error: {err}, {name}{''.join([f'[{i}]' for i in items])}"
                    )
                else:
                    hint = f"{err}: {name}{''.join([f'[{i}]' for i in items])}"

                if default == _undefined:
                    return self.env.undefined(
                        name=name,
                        hint=hint,
                    )
                return default

        return obj

    async def get_async(
        self, path: ContextPath, default: object = _undefined
    ) -> object:
        """Return the value at path `path` if it is in scope, else default."""
        if isinstance(path, str):
            return self._resolve(path, default)

        name, items = path[0], path[1:]
        assert isinstance(name, str)
        obj = self._resolve(name, default)

        if items:
            _gi = Context.getitem_async
            try:
                for item in items:
                    obj = await _gi(obj, item)
            except (KeyError, IndexError, TypeError) as err:
                if default == _undefined:
                    return self.env.undefined(
                        name=name,
                        hint=f"{err}: {name}{''.join([f'[{i}]' for i in items])}",
                    )

        return obj

    def resolve(self, name: str, default: object = _undefined) -> Any:
        """Return the object/value at `name` in the current scope.

        This is like `get`, but does a single, top-level lookup rather than a
        chained lookup from a sequence of keys.
        """
        return self._resolve(name, default)

    def _resolve(self, name: str, default: object = _undefined) -> Any:
        try:
            return self.scope[name]
        except KeyError:
            if default == _undefined:
                return self.env.undefined(name)
            return default

    @lru_cache(maxsize=128)
    def filter(self, name: str) -> Callable[..., object]:
        """Return the filter function with given name."""
        try:
            filter_func = self.env.filters[name]
        except KeyError as err:
            raise NoSuchFilterFunc(f"unknown filter '{name}'") from err

        kwargs: Dict[str, Any] = {}

        if getattr(filter_func, "with_context", False):
            kwargs["context"] = self

        if getattr(filter_func, "with_environment", False):
            kwargs["environment"] = self.env

        if kwargs:
            return partial(filter_func, **kwargs)

        return filter_func

    def get_template(self, name: str) -> BoundTemplate:
        """Load a template from the environment."""
        return self.env.get_template(name)

    async def get_template_async(self, name: str) -> BoundTemplate:
        """Load a template from the environment asynchronously."""
        return await self.env.get_template_async(name)

    def get_template_with_context(self, name: str, **kwargs: str) -> BoundTemplate:
        """Load a template from the environment, optionally referencing the current
        render context."""
        return self.env.get_template_with_context(self, name, **kwargs)

    async def get_template_with_context_async(
        self,
        name: str,
        **kwargs: str,
    ) -> BoundTemplate:
        """Load a template from the environment asynchronously, optionally referencing
        the current render context."""
        return await self.env.get_template_with_context_async(self, name, **kwargs)

    def increment(self, name: str) -> int:
        """Increment the named counter and return its value."""
        val: int = self.counters.get(name, 0)
        self.counters[name] = val + 1
        return val

    def decrement(self, name: str) -> int:
        """Decrement the named counter and return its value."""
        val: int = self.counters.get(name, 0) - 1
        self.counters[name] = val
        return val

    def cycle(self, group_name: str, args: Sequence[Any]) -> Iterator[Any]:
        """Return the next item in the given cycle. Initialise the cycle first if this
        is the first time we're seeing this combination of group name and arguments."""
        key = (group_name, tuple(args))
        if key not in self.tag_namespace["cycles"]:
            self.tag_namespace["cycles"][key] = cycle(args)
        it: Iterator[Any] = self.tag_namespace["cycles"][key]
        return it

    def ifchanged(self, val: str) -> bool:
        """Return True if the `ifchanged` value has changed."""
        if val != self.tag_namespace["ifchanged"]:
            self.tag_namespace["ifchanged"] = val
            return True

        return False

    def stopindex(self, key: str, index: Optional[int] = None) -> int:
        """Set or return the stop index of a for loop."""
        if index is not None:
            self.tag_namespace["stopindex"][key] = index
            return index

        idx: int = self.tag_namespace["stopindex"].get(key, 0)
        return idx

    @contextmanager
    def extend(self, namespace: Namespace) -> Iterator[Context]:
        """Extend this context with the given read-only namespace."""
        if self.scope.size() > self.env.context_depth_limit:
            raise ContextDepthError(
                "maximum context depth reached, possible recursive include"
            )

        self.scope.push(namespace)

        try:
            yield self
        finally:
            self.scope.pop()

    @contextmanager
    def loop(self, namespace: Namespace, forloop: ForLoop) -> Iterator[Context]:
        """Just like ``Context.extend``, but keeps track of ForLoop objects too."""
        self.raise_for_loop_limit(forloop.length)
        self.loops.append(forloop)
        with self.extend(namespace) as context:
            try:
                yield context
            finally:
                self.loops.pop()

    def parentloop(self) -> Union[Undefined, object]:
        """Return the last ForLoop object from the loop stack."""
        try:
            return self.loops[-1]
        except IndexError:
            return self.env.undefined("parentloop")

    def raise_for_loop_limit(self, length: int = 1) -> None:
        """Raise a ``LoopIterationLimitError`` if the product of the loop stack is
        greater than the configured loop iteration limit.
        """
        if (
            self.env.loop_iteration_limit
            and reduce(
                mul,
                itertools.chain(
                    (loop.length for loop in self.loops),
                    [length, self.loop_iteration_carry],
                ),
                1,
            )
            > self.env.loop_iteration_limit
        ):
            raise LoopIterationLimitError("loop iteration limit reached")

    def copy(
        self,
        namespace: Namespace,
        disabled_tags: Optional[List[str]] = None,
        carry_loop_iterations: bool = False,
    ) -> Context:
        """Return a copy of this context without any local variables or other state
        for stateful tags."""
        if self._copy_depth > self.env.context_depth_limit:
            raise ContextDepthError(
                "maximum context depth reached, possible recursive render"
            )

        loop_iteration_carry = (
            reduce(mul, (loop.length for loop in self.loops), 1)
            if carry_loop_iterations
            else 1
        )

        return self.__class__(
            self.env,
            globals=ReadOnlyChainMap(namespace, self.globals),
            disabled_tags=disabled_tags,
            copy_depth=self._copy_depth + 1,
            parent_context=self,
            loop_iteration_carry=loop_iteration_carry,
            local_namespace_size_carry=self._get_size_of_locals(),
        )

    def error(self, exc: Error) -> None:
        """Ignore, raise or convert the given exception to a warning."""
        if self.env.mode == Mode.STRICT:
            raise exc
        if self.env.mode == Mode.WARN:
            warnings.warn(str(exc), category=lookup_warning(exc.__class__))

    def get_buffer(self, buf: Optional[TextIO] = None) -> StringIO:
        """Return a new StringIO object, possibly limited according to the configured
        output stream limit."""
        if self.env.output_stream_limit is None:
            return StringIO()

        carry = buf.size if isinstance(buf, LimitedStringIO) else 0
        return LimitedStringIO(limit=self.env.output_stream_limit - carry)


class VariableCaptureContext(Context):
    """A render context that captures template variable names."""

    __slots__ = (
        "local_references",
        "all_references",
        "undefined_references",
        "root_context",
    )

    # Used for formatting context path strings.
    re_ident = re.compile(r"^[\w_][\w_\-]*$")

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        env: Environment,
        globals: Optional[Namespace] = None,
        disabled_tags: Optional[List[str]] = None,
        copy_depth: int = 0,
        parent_context: Optional[VariableCaptureContext] = None,
        loop_iteration_carry: int = 1,
        local_namespace_size_carry: int = 0,
    ):
        super().__init__(
            env,
            globals=globals,
            disabled_tags=disabled_tags,
            copy_depth=copy_depth,
            parent_context=parent_context,
            loop_iteration_carry=loop_iteration_carry,
            local_namespace_size_carry=local_namespace_size_carry,
        )
        self.local_references: List[str] = []
        self.all_references: List[str] = []
        self.undefined_references: List[str] = []

        root_context: VariableCaptureContext = self
        while root_context.parent_context and isinstance(
            root_context.parent_context, VariableCaptureContext
        ):
            root_context = root_context.parent_context
        self.root_context = root_context

    def assign(self, key: str, val: Any) -> None:
        self.local_references.append(key)
        return super().assign(key, val)

    def get(self, path: ContextPath, default: object = _undefined) -> object:
        result = super().get(path, default)
        self._count_reference(path, result)
        return result

    async def get_async(
        self, path: ContextPath, default: object = _undefined
    ) -> object:
        result = await super().get_async(path, default)
        self._count_reference(path, result)
        return result

    def resolve(self, name: str, default: object = _undefined) -> Any:
        result = super().resolve(name, default)
        self._count_reference(name, result)
        return result

    def increment(self, name: str) -> int:
        self.local_references.append(name)
        return super().increment(name)

    def decrement(self, name: str) -> int:
        self.local_references.append(name)
        return super().decrement(name)

    def _count_reference(self, path: ContextPath, result: object) -> None:
        if isinstance(path, str):
            ref = path
        else:
            _path = []
            for elem in path:
                if isinstance(elem, int):
                    _path.append(f"[{elem}]")
                else:
                    if self.re_ident.match(elem):
                        if _path:
                            _path.append(f".{elem}")
                        else:
                            _path.append(f"{elem}")
                    else:
                        _path.append(f'["{elem}"]')
            ref = "".join(_path)

        if is_undefined(result):
            self.root_context.undefined_references.append(ref)
        self.root_context.all_references.append(ref)
