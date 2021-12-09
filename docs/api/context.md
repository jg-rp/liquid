# liquid.Context

The result of rendering a template depends on the _context_ in which it is rendered. That is,
available variables and their values, and options set on the bound [Environment](Environment).

You probably don't want to instantiate a context directly. A new one is created automatically every
time a template is rendered. If you're writing custom tags, consider [copying](#copy) or
[extending](#extend) an existing context.

## `Context`

`class Context(env, [options])`

**Parameters**:

- `env: liquid.Environment` - The [Environment](Environment) associated with this context.

- `globals: Optional[Mapping[str, object]]` - Template global variables.

- `disabled_tags: Optional[List[str]]` - A list of tags names that are disallowed in this context.
  For example, partial templates rendered using the "render" tag are not allowed to use "include"
  tags.

- `copy_depth: int = 0` - The number times a context was copied to create this one.

## `Properties`

### env

**Type**: `env: liquid.Environment`

The [Environment](Environment) associated with this context.

### `locals`

**Type**: `locals: Dict[str, Any]`

A namespace for template local variables. Those that are bound with `assign` or `capture`.

### `globals`

**Type**: `globals: Mapping[str, object]`

A read-only namespace containing globally available variables. Usually passed down from the
environment.

### `counters`

**Type**: `counters: Dict[str, int]`

A namespace for `increment` and `decrement` counters.

### `scope`

**Type**: `scope: ReadOnlyChainMap`

Namespaces are searched using this chain map. When a context is extended, the temporary namespace is
pushed to the front of this chain.

### `loops`

**Type**: `loops: List[object]`

As stack of `forloop` objects. Used for populating `forloop.parentloop`.

### `disabled_tags`

**Type**: `disabled_tags: List[str]`

A list of tags names that are disallowed in this context. For example, partial templates rendered
using the "render" tag are not allowed to use "include" tags.

### `autoescape`

**Type**: `autoescape: bool`

Indicates if HTML auto-escaping is enabled.

## Methods

### `assign`

`assign(key: str, val: Any) -> None`

Add `val` to the local namespace with key `key`.

### `get`

`get(self, path: Union[str, Sequence[Union[str, int]]], default: object = _undefined) -> object:`

Return the value at path `path` if it is in scope, else default.

### `get_async`

`async assign_async(key: str, val: Any) -> None`

An async version of [get](#get).

### `resolve`

`resolve(self, name: str, default: object = _undefined) -> Any`

Return the object at `name` in the current scope. This is like [get](#get), but does a single,
top-level lookup rather than a chained lookup from a sequence of keys.`

### `filter`

`filter(self, name: str) -> Callable[..., object]`

Return the filter function with given name.

**Raises**: NoSuchFilterFunc if a filter with the given name does not exist.

### `get_template`

`get_template(self, name: str) -> BoundTemplate`

Load a template from the environment.

### `get_template_async`

`async get_template_async(self, name: str) -> BoundTemplate`

Load a template from the environment asynchronously.

### `extend`

`extend(self, namespace: Mapping[str, object]) -> Iterator[Context]`

A context manager that extends this context with the given read-only namespace.

**Raises**: `ContextDepthError` if the context has been extended too many times.

### `copy`

`copy( self, namespace: Dict[str, object], disabled_tags: Optional[List[str]] = None) -> Context:`

Return a copy of this context without any local variables or other state for stateful tags.

**Raises**: `ContextDepthError` if the context has been copied too many times.

### `error`

`error(self, exc: Error) -> None:`

Ignore, raise or convert the given exception to a warning, according to the current tolerance mode.
