"""Liquid template render context."""

from __future__ import annotations

import datetime
import itertools
import re
import sys
import warnings
from collections import defaultdict
from contextlib import contextmanager
from functools import partial
from functools import reduce
from io import StringIO
from operator import mul
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Iterator
from typing import Mapping
from typing import MutableMapping
from typing import Optional
from typing import Sequence
from typing import Sized
from typing import TextIO
from typing import Union

from .exceptions import ContextDepthError
from .exceptions import LiquidError
from .exceptions import LocalNamespaceLimitError
from .exceptions import LoopIterationLimitError
from .exceptions import UnknownFilterError
from .exceptions import lookup_warning
from .mode import Mode
from .output import LimitedStringIO
from .undefined import UNDEFINED
from .undefined import Undefined
from .utils import ReadOnlyChainMap

if TYPE_CHECKING:
    from .builtin.tags.for_tag import ForLoop
    from .environment import Environment
    from .template import BoundTemplate
    from .token import Token


class RenderContext:
    """A template render context.

    A new render context is created automatically each time `BoundTemplate.render`
    is called, which includes `globals` set on the bound `liquid.Environment` and
    `liquid.template.BoundTemplate`.
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

    def __init__(
        self,
        template: BoundTemplate,
        *,
        globals: Optional[Mapping[str, object]] = None,  # noqa: A002
        disabled_tags: Optional[list[str]] = None,
        copy_depth: int = 0,
        parent_context: Optional[RenderContext] = None,
        loop_iteration_carry: int = 1,
        local_namespace_size_carry: int = 0,
    ):
        self.env: Environment = template.env
        self.template = template

        # A namespace for template local variables. Those that are bound with
        # `assign` or `capture`.
        self.locals: MutableMapping[str, object] = {}

        # A read-only namespace containing globally available variables. Usually
        # passed down from the environment.
        self.globals: Mapping[str, object] = globals or {}

        # A namespace for `increment` and `decrement` counters.
        self.counters: dict[str, int] = {}

        # Namespaces are searched in this order. When a context is extended, the
        # temporary namespace is pushed to the front of this chain.
        self.scope = ReadOnlyChainMap(self.locals, self.globals, builtin, self.counters)

        # A namespace supporting stateful tags. Such as `cycle`, `increment`,
        # `decrement` and `ifchanged`.
        self.tag_namespace: dict[str, Any] = {
            "cycles": {},
            "ifchanged": "",
            "stopindex": {},
            "extends": defaultdict(list),
            "macros": {},
        }

        # As stack of forloop objects. Used for populating forloop.parentloop.
        self.loops: list[ForLoop] = []

        # A list of tags names that are disallowed in this context. For example,
        # partial templates rendered using the "render" tag are not allowed to
        # use "include" tags.
        self.disabled_tags: list[str] = disabled_tags or []

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
        """Add or replace the context variable named _key_ with the value _val_."""
        self.locals[key] = val
        if (
            self.env.local_namespace_limit
            and self.get_size_of_locals() > self.env.local_namespace_limit
        ):
            raise LocalNamespaceLimitError("local namespace limit reached", token=None)

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

    def get(  # noqa: PLR0911
        self, path: list[object], *, token: Optional[Token], default: object = UNDEFINED
    ) -> object:
        """Resolve and return _path_ in the current scope.

        If _token_ is not None, it will be used to give error messages extra contextual
        information.

        Returns _default_ is the path is not in scope.
        """
        it = iter(path)
        root = next(it)
        assert isinstance(root, str)

        try:
            obj = self.scope[root]
        except (KeyError, TypeError, IndexError):
            if default == UNDEFINED:
                hint = f"{root!r} is undefined"
                return self.env.undefined(root, hint=hint, token=token)
            return default

        for i, segment in enumerate(it):
            try:
                obj = self.get_item(obj, segment)
            except (KeyError, TypeError):
                if default == UNDEFINED:
                    hint = f"{_segments_str(path[: i + 2])} is undefined"
                    return self.env.undefined(root, hint=hint, token=token)
                return default
            except IndexError:
                if default == UNDEFINED:
                    hint = "index out of range"
                    return self.env.undefined(root, hint=hint, token=token)
                return default

        return obj

    async def get_async(  # noqa: PLR0911
        self,
        path: list[object],
        *,
        token: Optional[Token],
        default: object = UNDEFINED,
    ) -> object:
        """Resolve and return _path_ in the current scope.

        If _token_ is not None, it will be used to give error messages extra contextual
        information.

        Returns _default_ is the path is not in scope.
        """
        it = iter(path)
        root = next(it)
        assert isinstance(root, str)

        try:
            obj = self.scope[root]
        except (KeyError, TypeError, IndexError):
            if default == UNDEFINED:
                hint = f"{root!r} is undefined"
                return self.env.undefined(root, hint=hint, token=token)
            return default

        for i, segment in enumerate(it):
            try:
                obj = await self.get_item_async(obj, segment)
            except (KeyError, TypeError):
                if default == UNDEFINED:
                    hint = f"{_segments_str(path[: i + 2])} is undefined"
                    return self.env.undefined(root, hint=hint, token=token)
                return default
            except IndexError:
                if default == UNDEFINED:
                    hint = "index out of range"
                    return self.env.undefined(root, hint=hint, token=token)
                return default

        return obj

    def resolve(
        self, name: str, *, token: Optional[Token] = None, default: object = UNDEFINED
    ) -> Any:
        """Return the object/value at `name` in the current scope.

        This is like `get`, but does a single, top-level lookup rather than a
        chained lookup from a sequence of keys.
        """
        return self._resolve(name, token=token, default=default)

    def _resolve(
        self, name: str, *, token: Optional[Token], default: object = UNDEFINED
    ) -> Any:
        try:
            return self.scope[name]
        except KeyError:
            if default == UNDEFINED:
                return self.env.undefined(name, token=token)
            return default

    def filter(self, name: str, token: Optional[Token]) -> Callable[..., object]:  # noqa: A003
        """Return the filter function with given name."""
        try:
            filter_func = self.env.filters[name]
        except KeyError as err:
            if not self.env.strict_filters:
                return _no_op_filter
            raise UnknownFilterError(f"unknown filter '{name}'", token=token) from err

        kwargs: dict[str, Any] = {}

        if getattr(filter_func, "with_context", False):
            kwargs["context"] = self

        if getattr(filter_func, "with_environment", False):
            kwargs["environment"] = self.env

        if kwargs:
            if hasattr(filter_func, "filter_async"):
                _filter_func = partial(filter_func, **kwargs)
                _filter_func.filter_async = partial(  # type: ignore
                    filter_func.filter_async,
                    **kwargs,
                )
                return _filter_func
            return partial(filter_func, **kwargs)

        return filter_func

    def get_template(self, name: str) -> BoundTemplate:
        """Load a template from the environment."""
        return self.env.get_template(name)

    async def get_template_async(self, name: str) -> BoundTemplate:
        """Load a template from the environment asynchronously."""
        return await self.env.get_template_async(name)

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

    def cycle(self, key: object, length: int) -> int:
        """Return the index of the next item in the cycle."""
        namespace: dict[object, int] = self.tag_namespace["cycles"]
        idx = namespace.setdefault(key, 0)
        namespace[key] = (idx + 1) % length
        return idx

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
        self, namespace: Mapping[str, object], template: Optional[BoundTemplate] = None
    ) -> Iterator[RenderContext]:
        """Extend this context with the given read-only namespace."""
        if self.scope.size() > self.env.context_depth_limit:
            raise ContextDepthError(
                "maximum context depth reached, possible recursive include", token=None
            )

        # Remember the current template so we can restore it upon exiting the
        # context manager.
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
    def loop(
        self, namespace: Mapping[str, object], forloop: ForLoop
    ) -> Iterator[RenderContext]:
        """Just like `Context.extend`, but keeps track of ForLoop objects too."""
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
            return self.env.undefined("parentloop", token=None)

    def raise_for_loop_limit(self, length: int = 1) -> None:
        """Raise a `LoopIterationLimitError` if loop stack is bigger than the limit."""
        if (
            self.env.loop_iteration_limit
            and reduce(
                mul,
                (loop.length for loop in self.loops),
                length * self.loop_iteration_carry,
            )
            > self.env.loop_iteration_limit
        ):
            raise LoopIterationLimitError("loop iteration limit reached", token=None)

    def copy(
        self,
        namespace: Mapping[str, object],
        disabled_tags: Optional[list[str]] = None,
        carry_loop_iterations: bool = False,
        template: Optional[BoundTemplate] = None,
        block_scope: bool = False,
    ) -> RenderContext:
        """Return a copy of this render context.

        Local variables and other state for stateful tags are not copied.
        """
        if self._copy_depth > self.env.context_depth_limit:
            raise ContextDepthError(
                "maximum context depth reached, possible recursive render", token=None
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
                template or self.template,
                globals=ReadOnlyChainMap(namespace, self.scope),
                disabled_tags=disabled_tags,
                copy_depth=self._copy_depth + 1,
                parent_context=self,
                loop_iteration_carry=loop_iteration_carry,
                local_namespace_size_carry=self.get_size_of_locals(),
            )
            # This might need to be generalized so the caller can specify which
            # tag namespaces need to be copied.
            ctx.tag_namespace["extends"] = self.tag_namespace["extends"]
        else:
            ctx = self.__class__(
                template or self.template,
                globals=ReadOnlyChainMap(namespace, self.globals),
                disabled_tags=disabled_tags,
                copy_depth=self._copy_depth + 1,
                parent_context=self,
                loop_iteration_carry=loop_iteration_carry,
                local_namespace_size_carry=self.get_size_of_locals(),
            )

        return ctx

    def error(self, exc: LiquidError) -> None:
        """Ignore, raise or convert the given exception to a warning."""
        if self.env.mode == Mode.STRICT:
            raise exc
        if self.env.mode == Mode.WARN:
            warnings.warn(
                str(exc), category=lookup_warning(exc.__class__), stacklevel=2
            )

    def get_buffer(self, buf: Optional[TextIO] = None) -> StringIO:
        """Return a new StringIO object that respects the configured stream limit."""
        if self.env.output_stream_limit is None:
            return StringIO()

        carry = buf.size if isinstance(buf, LimitedStringIO) else 0
        return LimitedStringIO(limit=self.env.output_stream_limit - carry)

    def get_item(self, obj: Any, key: Any) -> Any:  # noqa: PLR0911, PLR0912
        """An item getter used when resolving a Liquid path.

        Override this to change the behavior of `.first`, `.last` and `.size`.
        """
        if hasattr(key, "__liquid__"):
            key = key.__liquid__()

        if key == "size":
            try:
                return obj["size"]
            except (KeyError, IndexError, TypeError):
                if isinstance(obj, Sized):
                    return len(obj)
                raise

        if key == "first":
            try:
                return obj["first"]
            except (KeyError, IndexError, TypeError):
                if isinstance(obj, Mapping) and obj:
                    return next(itertools.islice(obj.items(), 1))
                if isinstance(obj, str) and not self.env.string_first_and_last:
                    raise TypeError("string object has no method 'first'") from None
                if isinstance(obj, Sequence):
                    return obj[0]
                raise

        if key == "last":
            try:
                return obj["last"]
            except (KeyError, IndexError, TypeError):
                if isinstance(obj, str) and not self.env.string_first_and_last:
                    raise TypeError("string object has no method 'last'") from None
                if isinstance(obj, Sequence):
                    return obj[-1]
                raise

        if (
            not self.env.string_sequences
            and isinstance(key, int)
            and isinstance(obj, str)
        ):
            raise TypeError("string object is not subscriptable")

        return obj[key]

    async def get_item_async(self, obj: Any, key: Any) -> Any:  # noqa: PLR0911, PLR0912
        """An async item getter for resolving paths."""

        async def _get_item(obj: Any, key: Any) -> object:
            if hasattr(obj, "__getitem_async__"):
                return await obj.__getitem_async__(key)
            return obj[key]

        if hasattr(key, "__liquid__"):
            key = key.__liquid__()

        if key == "size":
            try:
                return await _get_item(obj, "size")
            except (KeyError, IndexError, TypeError):
                if isinstance(obj, Sized):
                    return len(obj)
                raise

        if key == "first":
            try:
                return await _get_item(obj, "first")
            except (KeyError, IndexError, TypeError):
                if isinstance(obj, Mapping) and obj:
                    return next(itertools.islice(obj.items(), 1))
                if isinstance(obj, str) and not self.env.string_first_and_last:
                    raise TypeError("string object has no method 'first'") from None
                if isinstance(obj, Sequence):
                    return obj[0]
                raise

        if key == "last":
            try:
                return await _get_item(obj, "last")
            except (KeyError, IndexError, TypeError):
                if isinstance(obj, str) and not self.env.string_first_and_last:
                    raise TypeError("string object has no method 'last'") from None
                if isinstance(obj, Sequence):
                    return obj[-1]
                raise

        if (
            not self.env.string_sequences
            and isinstance(key, int)
            and isinstance(obj, str)
        ):
            raise TypeError("string object is not subscriptable")

        return await _get_item(obj, key)


class FutureContext(RenderContext):
    """A render context configured for maximum compatibility with the Ruby liquid."""


class BuiltIn(Mapping[str, object]):
    """Mapping-like object for resolving built-in, dynamic objects."""

    def __contains__(self, item: object) -> bool:
        return item in ("now", "today")

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

RE_PROPERTY = re.compile(r"[\u0080-\uFFFFa-zA-Z_][\u0080-\uFFFFa-zA-Z0-9_-]*")


def _segments_str(segments: list[object]) -> str:
    it = iter(segments)
    buf = [str(next(it))]
    for segment in it:
        if isinstance(segment, str):
            if RE_PROPERTY.fullmatch(segment):
                buf.append(f".{segment}")
            else:
                buf.append(f"[{segment!r}]")
    return "".join(buf)


def _no_op_filter(left: object, *_args: object, **_kwargs: object) -> object:
    return left
