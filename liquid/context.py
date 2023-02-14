"""Liquid template render context."""

from __future__ import annotations

import collections.abc
import datetime
import itertools
import re
import sys
import warnings

from contextlib import contextmanager

from functools import partial
from functools import reduce

from itertools import cycle
from io import StringIO

from operator import getitem
from operator import mul

from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Dict
from typing import Iterator
from typing import List
from typing import Mapping
from typing import MutableMapping
from typing import Optional
from typing import Sequence
from typing import TextIO
from typing import Union
from typing import TYPE_CHECKING

from liquid import Mode
from liquid.chain_map import ReadOnlyChainMap
from liquid.output import LimitedStringIO

from liquid.exceptions import NoSuchFilterFunc
from liquid.exceptions import ContextDepthError
from liquid.exceptions import Error
from liquid.exceptions import LocalNamespaceLimitError
from liquid.exceptions import LoopIterationLimitError
from liquid.exceptions import lookup_warning

from liquid.undefined import DebugUndefined
from liquid.undefined import is_undefined
from liquid.undefined import StrictDefaultUndefined
from liquid.undefined import StrictUndefined
from liquid.undefined import Undefined
from liquid.undefined import UNDEFINED

if TYPE_CHECKING:  # pragma: no cover
    from liquid import Environment
    from liquid.template import BoundTemplate
    from liquid.builtin.tags.for_tag import ForLoop


__all__ = (
    "Context",
    "DebugUndefined",
    "get_item",
    "is_undefined",
    "ReadOnlyChainMap",
    "StrictDefaultUndefined",
    "StrictUndefined",
    "VariableCaptureContext",
    "Undefined",
)

ContextPath = Union[str, Sequence[Union[str, int]]]
Namespace = Mapping[str, object]


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


def _liquid_size(
    obj: Any, item_getter: Callable[[Any, str], object] = getitem
) -> object:
    try:
        return item_getter(obj, "size")
    except (KeyError, IndexError, TypeError):
        if isinstance(obj, collections.abc.Sized):
            return len(obj)
        raise


def _liquid_first(
    obj: Any, item_getter: Callable[[Any, str], object] = getitem
) -> object:
    try:
        return item_getter(obj, "first")
    except (KeyError, IndexError, TypeError):
        if isinstance(obj, str):
            raise
        if isinstance(obj, collections.abc.Mapping) and obj:
            return list(itertools.islice(obj.items(), 1))[0]
        if isinstance(obj, collections.abc.Sequence):
            return obj[0]
        raise


def _liquid_last(
    obj: Any, item_getter: Callable[[Any, str], object] = getitem
) -> object:
    try:
        return item_getter(obj, "last")
    except (KeyError, IndexError, TypeError):
        if isinstance(obj, str):
            raise
        if isinstance(obj, collections.abc.Sequence):
            return obj[-1]
        raise


async def _liquid_size_async(
    obj: Any, item_getter: Callable[[Any, str], Awaitable[object]]
) -> object:
    try:
        return await item_getter(obj, "size")
    except (KeyError, IndexError, TypeError):
        if isinstance(obj, collections.abc.Sized):
            return len(obj)
        raise


async def _liquid_first_async(
    obj: Any, item_getter: Callable[[Any, str], Awaitable[object]]
) -> object:
    try:
        return await item_getter(obj, "first")
    except (KeyError, IndexError, TypeError):
        if isinstance(obj, str):
            raise
        if isinstance(obj, collections.abc.Mapping) and obj:
            return list(itertools.islice(obj.items(), 1))[0]
        if isinstance(obj, collections.abc.Sequence):
            return obj[0]
        raise


async def _liquid_last_async(
    obj: Any, item_getter: Callable[[Any, str], Awaitable[object]]
) -> object:
    try:
        return await item_getter(obj, "last")
    except (KeyError, IndexError, TypeError):
        if isinstance(obj, str):
            raise
        if isinstance(obj, collections.abc.Sequence):
            return obj[-1]
        raise


# pylint: disable=too-many-instance-attributes redefined-builtin too-many-public-methods
class Context:
    """A template render context.

    A new render context is created automatically each time :meth:`BoundTemplate.render`
    is called, which includes `globals` set on the bound :class:`liquid.Environment` and
    :class:`liquid.template.BoundTemplate`.
    """

    __slots__ = (
        "_copy_depth",
        "autoescape",
        "counters",
        "disabled_tags",
        "env",
        "globals",
        "local_namespace_size_carry",
        "locals",
        "loop_iteration_carry",
        "loops",
        "parent_context",
        "scope",
        "tag_namespace",
        "template",
    )

    # NOTE: The `template` argument has been added for the benefit of tags like
    # `{% extends %}`, which need access to the current template when rendering. With
    # hindsight, `template` should be the only positional arguments, with `env`
    # accessible via `template`, and all others arguments should be keyword only. We
    # leave `template` optional for backwards compatibility reasons only. This might
    # change in Python Liquid version 2.0.

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
        template: Optional[BoundTemplate] = None,
    ):
        self.env = env
        self.template = template

        # A namespace for template local variables. Those that are bound with
        # `assign` or `capture`.
        self.locals: MutableMapping[str, object] = {}

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
            and self.get_size_of_locals() > self.env.local_namespace_limit
        ):
            raise LocalNamespaceLimitError("local namespace limit reached")

    def get_size_of_locals(self) -> int:
        """Return the "size" or a "score" for the current local namespace.

        This is used by the optional local namespace resource limit. Override
        `get_size_of_locals` to customize how the limit is calculated. Be sure
        to consider `self.local_namespace_size_carry` when writing a custom
        implementation of `get_size_of_locals`.

        The default implementation uses `sys.getsizeof()` on each of the local
        namespace's values. It is not a reliable measure of size in bytes.
        """
        if not self.env.local_namespace_limit:
            return 0
        return (
            sum(sys.getsizeof(obj, default=1) for obj in self.locals.values())
            + self.local_namespace_size_carry
        )

    def get(self, path: ContextPath, default: object = UNDEFINED) -> object:
        """Return the value at path `path` if it is in scope, else default."""
        if isinstance(path, str):
            return self._resolve(path, default)

        name, items = path[0], path[1:]
        assert isinstance(name, str)
        obj = self._resolve(name, default)

        if items:
            try:
                return reduce(self.getitem, items, obj)
            except (KeyError, IndexError, TypeError) as err:
                if isinstance(err, KeyError):
                    hint = (
                        f"key error: {err}, {name}{''.join([f'[{i}]' for i in items])}"
                    )
                else:
                    hint = f"{err}: {name}{''.join([f'[{i}]' for i in items])}"

                if default == UNDEFINED:
                    return self.env.undefined(
                        name=name,
                        hint=hint,
                    )
                return default

        return obj

    async def get_async(self, path: ContextPath, default: object = UNDEFINED) -> object:
        """Return the value at path `path` if it is in scope, else default."""
        if isinstance(path, str):
            return self._resolve(path, default)

        name, items = path[0], path[1:]
        assert isinstance(name, str)
        obj = self._resolve(name, default)

        if items:
            _gi = self.getitem_async
            try:
                for item in items:
                    obj = await _gi(obj, item)
            except (KeyError, IndexError, TypeError) as err:
                if default == UNDEFINED:
                    return self.env.undefined(
                        name=name,
                        hint=f"{err}: {name}{''.join([f'[{i}]' for i in items])}",
                    )

        return obj

    def resolve(self, name: str, default: object = UNDEFINED) -> Any:
        """Return the object/value at `name` in the current scope.

        This is like `get`, but does a single, top-level lookup rather than a
        chained lookup from a sequence of keys.
        """
        return self._resolve(name, default)

    def _resolve(self, name: str, default: object = UNDEFINED) -> Any:
        try:
            return self.scope[name]
        except KeyError:
            if default == UNDEFINED:
                return self.env.undefined(name)
            return default

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

    def cycle(self, group_name: str, args: Sequence[object]) -> object:
        """Return the next item in the cycle of the given arguments."""
        key = (group_name, tuple(args))
        namespace = self.tag_namespace["cycles"]
        if key not in namespace:
            namespace[key] = cycle(range(len(args)))
        return args[next(namespace[key])]

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
    def extend(
        self, namespace: Namespace, template: Optional[BoundTemplate] = None
    ) -> Iterator[Context]:
        """Extend this context with the given read-only namespace."""
        if self.scope.size() > self.env.context_depth_limit:
            raise ContextDepthError(
                "maximum context depth reached, possible recursive include"
            )

        _template = self.template
        if template:
            self.template = template

        self.scope.push(namespace)

        try:
            yield self
        finally:
            if template:
                self.template = _template
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
                (loop.length for loop in self.loops),
                length * self.loop_iteration_carry,
            )
            > self.env.loop_iteration_limit
        ):
            raise LoopIterationLimitError("loop iteration limit reached")

    def copy(
        self,
        namespace: Namespace,
        disabled_tags: Optional[List[str]] = None,
        carry_loop_iterations: bool = False,
        template: Optional[BoundTemplate] = None,
        block_scope: bool = False,
    ) -> Context:
        """Return a copy of this context without any local variables or other state
        for stateful tags."""
        if self._copy_depth > self.env.context_depth_limit:
            raise ContextDepthError(
                "maximum context depth reached, possible recursive render"
            )

        if carry_loop_iterations:
            loop_iteration_carry = reduce(
                mul,
                (loop.length for loop in self.loops),
                self.loop_iteration_carry,
            )
        else:
            loop_iteration_carry = 1

        if block_scope:
            ctx = self.__class__(
                self.env,
                globals=ReadOnlyChainMap(namespace, self.scope),
                disabled_tags=disabled_tags,
                copy_depth=self._copy_depth + 1,
                parent_context=self,
                loop_iteration_carry=loop_iteration_carry,
                local_namespace_size_carry=self.get_size_of_locals(),
            )
            # This might need to be generalized some the caller can specify which
            # tag namespaces need to be copied.
            ctx.tag_namespace["extends"] = self.tag_namespace["extends"]
        else:
            ctx = self.__class__(
                self.env,
                globals=ReadOnlyChainMap(namespace, self.globals),
                disabled_tags=disabled_tags,
                copy_depth=self._copy_depth + 1,
                parent_context=self,
                loop_iteration_carry=loop_iteration_carry,
                local_namespace_size_carry=self.get_size_of_locals(),
            )

        ctx.template = template or self.template
        return ctx

    def error(self, exc: Error) -> None:
        """Ignore, raise or convert the given exception to a warning."""
        if self.env.mode == Mode.STRICT:
            raise exc
        if self.env.mode == Mode.WARN:
            warnings.warn(
                str(exc), category=lookup_warning(exc.__class__), stacklevel=2
            )

    def get_buffer(self, buf: Optional[TextIO] = None) -> StringIO:
        """Return a new StringIO object, possibly limited according to the configured
        output stream limit."""
        if self.env.output_stream_limit is None:
            return StringIO()

        carry = buf.size if isinstance(buf, LimitedStringIO) else 0
        return LimitedStringIO(limit=self.env.output_stream_limit - carry)

    # pylint: disable=too-many-return-statements
    @classmethod
    def getitem(cls, obj: Any, key: Any) -> Any:
        """Item getter with special methods for arrays/lists and hashes/dicts."""
        if hasattr(key, "__liquid__"):
            key = key.__liquid__()

        if key == "size":
            return _liquid_size(obj)
        if key == "first":
            return _liquid_first(obj)
        if key == "last":
            return _liquid_last(obj)

        return getitem(obj, key)

    # pylint: disable=too-many-return-statements
    @classmethod
    async def getitem_async(cls, obj: Any, key: Any) -> object:
        """Item getter with special methods for arrays/lists and hashes/dicts."""

        async def _get_item(obj: Any, key: Any) -> object:
            if hasattr(obj, "__getitem_async__"):
                return await obj.__getitem_async__(key)
            return getitem(obj, key)

        if hasattr(key, "__liquid__"):
            key = key.__liquid__()

        if key == "size":
            return await _liquid_size_async(obj, _get_item)
        if key == "first":
            return await _liquid_first_async(obj, _get_item)
        if key == "last":
            return await _liquid_last_async(obj, _get_item)

        return await _get_item(obj, key)


# NOTE: The name `VariableCaptureContext` is now a little misleading. We are
# "capturing" more than variable names.


class VariableCaptureContext(Context):
    """A render context that captures template variable and filter names."""

    __slots__ = (
        "local_references",
        "all_references",
        "undefined_references",
        "root_context",
        "filters",
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
        self.filters: List[str] = []

        root_context: VariableCaptureContext = self
        while root_context.parent_context and isinstance(
            root_context.parent_context, VariableCaptureContext
        ):
            root_context = root_context.parent_context
        self.root_context = root_context

    def assign(self, key: str, val: Any) -> None:
        self.root_context.local_references.append(key)
        return super().assign(key, val)

    def get(self, path: ContextPath, default: object = UNDEFINED) -> object:
        result = super().get(path, default)
        self._count_reference(path, result)
        return result

    async def get_async(self, path: ContextPath, default: object = UNDEFINED) -> object:
        result = await super().get_async(path, default)
        self._count_reference(path, result)
        return result

    def resolve(self, name: str, default: object = UNDEFINED) -> Any:
        result = super().resolve(name, default)
        self._count_reference(name, result)
        return result

    def increment(self, name: str) -> int:
        self.root_context.local_references.append(name)
        return super().increment(name)

    def decrement(self, name: str) -> int:
        self.root_context.local_references.append(name)
        return super().decrement(name)

    def filter(self, name: str) -> Callable[..., object]:
        self.root_context.filters.append(name)
        return super().filter(name)

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


class FutureContext(Context):
    """A render context that addresses some incompatibilities between Python Liquid and
    Ruby Liquid.

    These "fixes" have not been implemented in the default `Context` for the benefit of
    existing Python Liquid users that rely on past behavior.

    This render context currently fixes https://github.com/jg-rp/liquid/issues/43 and
    https://github.com/jg-rp/liquid/issues/90.

    """

    @classmethod
    def getitem(cls, obj: Any, key: Any) -> Any:
        if isinstance(obj, str) and isinstance(key, int):
            raise IndexError("string indices are not allowed")
        return super().getitem(obj, key)

    @classmethod
    async def getitem_async(cls, obj: Any, key: Any) -> object:
        if isinstance(obj, str) and isinstance(key, int):
            raise IndexError("string indices are not allowed")
        return await super().getitem_async(obj, key)

    def cycle(self, group_name: str, args: Sequence[object]) -> object:
        if group_name:
            key = group_name
        else:
            key = str(args)

        namespace: Dict[str, int] = self.tag_namespace["cycles"]
        index = namespace.setdefault(key, 0)
        try:
            rv = args[index]
        except IndexError:
            rv = None

        index += 1
        if index >= len(args):
            index = 0

        namespace[key] = index
        return rv


class FutureVariableCaptureContext(VariableCaptureContext, FutureContext):
    """A render context that captures information about template variables and filters."""


def get_item(
    obj: Sequence[Any],
    *items: Any,
    default: Optional[object] = UNDEFINED,
) -> Any:
    """Chained item getter."""
    try:
        itm: Any = reduce(Context.getitem, items, obj)
    except (KeyError, IndexError, TypeError):
        itm = default
    return itm
