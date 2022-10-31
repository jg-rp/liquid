# liquid.Context

A render context, containing namespaces for template variables and a references to the bound environment.

You probably don't want to instantiate a context directly. A new one is created automatically every time a template is rendered. If you're writing custom tags, consider [copying](#copy) or [extending](#extend) an existing context.

## `Context`

`class Context(env, [options])`

**Parameters**:

- `env: liquid.Environment` - The [`Environment`](./environment.md) associated with this context.

- `globals: Optional[Mapping[str, object]]` - Template global variables.

- `disabled_tags: Optional[List[str]]` - A list of tags names that are disallowed in this context.
  For example, partial templates rendered using the "render" tag are not allowed to use "include"
  tags.

- `copy_depth: int = 0` - The number times a context was copied to create this one.

## Properties

### `env`

**Type**: `liquid.Environment`

The [`Environment`](./environment.md) associated with this context.

### `locals`

**Type**: `Dict[str, Any]`

A namespace for template local variables. Those that are bound with `assign` or `capture`.

### `globals`

**Type**: `Mapping[str, object]`

A read-only namespace containing globally available variables. Usually passed down from the
environment.

### `counters`

**Type**: `Dict[str, int]`

A namespace for `increment` and `decrement` counters.

### `scope`

**Type**: `ReadOnlyChainMap`

Namespaces are searched using this chain map. When a context is extended, the temporary namespace is
pushed to the front of this chain.

### `loops`

**Type**: `List[object]`

As stack of `forloop` objects. Used for populating `forloop.parentloop`.

### `disabled_tags`

**Type**: `List[str]`

A list of tags names that are disallowed in this context. For example, partial templates rendered
using the "render" tag are not allowed to use "include" tags.

### `autoescape`

**Type**: `bool`

Indicates if HTML auto-escaping is enabled.

## Methods

### `assign`

`assign(key: str, val: Any) -> None`

Add `val` to the local namespace with key `key`.

### `get`

`get(path: Union[str, Sequence[Union[str, int]]], default: object = _undefined) -> object:`

Return the value at path `path` if it is in scope, else default.

### `get_async`

`async get_async(key: str, val: Any) -> None`

An async version of [`get()`](#get).

### `resolve`

`resolve(name: str, default: object = _undefined) -> Any`

Return the object at `name` in the current scope. This is like [`get()`](#get), but does a single, top-level lookup rather than a chained lookup from a sequence of keys.`

### `filter`

`filter(name: str) -> Callable[..., object]`

Return the filter function with given name.

**Raises**: NoSuchFilterFunc if a filter with the given name does not exist.

### `get_size_of_locals`

`get_size_of_locals(self) -> int`

Return the "size" or a "score" for the current local namespace.

This is used by the optional local namespace resource limit. Override `get_size_of_locals` to customize how the limit is calculated. Be sure to consider `self.local_namespace_size_carry` when writing a custom implementation of `get_size_of_locals`.

The default implementation uses `sys.getsizeof()` on each of the local namespace's values. It is not a reliable measure of size in bytes.

### `get_template`

`get_template(name: str) -> BoundTemplate`

Load a template from the environment.

### `get_template_async`

`async get_template_async(name: str) -> BoundTemplate`

Load a template from the environment asynchronously.

### `extend`

`extend(namespace: Mapping[str, object]) -> Iterator[Context]`

A context manager that extends this context with the given read-only namespace.

**Raises**: `ContextDepthError` if the context has been extended too many times.

### `copy`

`copy( self, namespace: Dict[str, object], disabled_tags: Optional[List[str]] = None) -> Context:`

Return a copy of this context without any local variables or other state for stateful tags.

**Raises**: `ContextDepthError` if the context has been copied too many times.

### `error`

`error(exc: Error) -> None:`

Ignore, raise or convert the given exception to a warning, according to the current tolerance mode.
