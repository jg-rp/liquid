# Strictness

Templates are parsed and rendered in strict mode by default. Where syntax and render-time type errors raise an exception as soon as possible. You can change the error tolerance mode with the `tolerance` argument to [`Environment`](../api/environment.md) or [`Template`](../api/template.md).

Available modes are `Mode.STRICT`, `Mode.WARN` and `Mode.LAX`.

```python
from liquid import Environment, FileSystemLoader, Mode

env = Environment(
    loader=FileSystemLoader("templates/"),
    tolerance=Mode.LAX,
)
```

## Undefined Variables

By default, references to undefined variables are silently ignored. Pass `StrictUndefined` as the `undefined` argument to [`Template`](../api/template.md) or [`Environment`](../api/environment.md), and any operation on an undefined variable will raise an `UndefinedError`.

```python
from liquid import Environment, StrictUndefined
env = Environment(undefined=StrictUndefined)
```

See [Undefined Variables](../guides/undefined-variables.md) for more information and example of how to customize undefined variable handling.

## Undefined Filters

Undefined filters raise a `NoSuchFilterFunc` exception by default. Set the `strict_filters` argument to [`Template`](../api/template.md) or [`Environment`](../api/environment.md) to `False` and undefined filters will be silently ignored.

```python
from liquid import Environment
env = Environment(strict_filters=False)
```
