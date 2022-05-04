---
id: BoundTemplate
---

# liquid.BoundTemplate

A liquid template that has been parsed and is bound to a [liquid.Environment](Environment).

You probably don't want to instantiate `BoundTemplate` directly. Use
[liquid.Environment.from_string()](Environment#from_string) or
[liquid.Environment.get_template()](Environment#get_template) instead.

## `BoundTemplate`

`class BoundTemplate(env, parse_tree, [options])`

**Parameters**:

- `env: liquid.Environment` - The environment this template is bound to.

- `parse_tree: liquid.ast.ParseTree` - The parse tree representing this template.

- `name: str` - Optional name of the template. Defaults to an empty string.

- `path: Optional[Union[str, Path]]` - Optional origin path or identifier for the template.

- `globals: Optional[Dict[str, object]]` - An optional mapping of context variables made available
  every time the resulting template is rendered. Defaults to `None`.

- `matter: Optional[Mapping[str, object]]` - Optional mapping containing variables associated with
  the template. Could be "front matter" or other meta data.

- `uptodate: Optional[Callable[[], bool]]` - Optional callable that will return `True` if the
  template is up to date, or `False` if it needs to be reloaded. Defaults to `None`.

## Properties

### `name`

The template's name. As it would been passed to [liquid.Environment.get_template()](Environment#get_template).

**Type**: `str`

### `globals`

A dictionary of context variables made available every time this template is rendered.

**Type**: `Dict[str, object]`

### `matter`

Similar to `globals`, a dictionary of context variables made available every time this template is
rendered. `globals` is usually passed down from the environment, `matter` usually originates from
a template loader. They are kept separate so subclasses can choose how to merge them.

**Type**: `Mapping[str, object]`

### `is_up_to_date`

`True` if the template is up to date, `False` otherwise.

**Type**: `bool`

## Methods

### `analyze`

`analyze(follow_partials, raise_for_failures)`

Statically analyze the template and any included/rendered templates.

**Parameters:**

- `follow_partials: bool` - If `True`, we will try to load partial templates and analyze those templates too. Default's to `True`.

- `raise_for_failures: bool` - If `True`, will raise an exception if an `ast.Node` or `expression.Expression` does not define a `children()` method, or if a partial template can not be loaded. When `False`, no exception is raised and a mapping of failed nodes and expressions is available as the `failed_visits` property. A mapping of unloadable partial templates is stored in the `unloadable_partials` property.

**Returns**: An object containing analysis results.  
**Return Type**: [liquid.template.TemplateAnalysis](./template-analysis.md)

### `analyze_async`

`async analyze_async(follow_partials, raise_for_failures)`

Statically analyze the template and any included/rendered templates.

**Parameters:**

- `follow_partials: bool` - If `True`, we will try to load partial templates and analyze those templates too. Default's to `True`.

- `raise_for_failures: bool` - If `True`, will raise an exception if an `ast.Node` or `expression.Expression` does not define a `children()` method, or if a partial template can not be loaded. When `False`, no exception is raised and a mapping of failed nodes and expressions is available as the `failed_visits` property. A mapping of unloadable partial templates is stored in the `unloadable_partials` property.

**Returns**: An object containing analysis results.  
**Return Type**: [liquid.template.TemplateAnalysis](./template-analysis.md)

### `render`

`render(*args, **kwargs) -> str`

Render the template with `args` and `kwargs` included in the render context. Accepts the same
arguments as `dict()`.

**Returns**: The rendered template as a string.  
**Return Type**: `str`

### `render_async`

`async render_async(*args, **kwargs) -> str`

An async version of [liquid.BoundTemplate.render()](#render)

**Returns**: The rendered template as a string.  
**Return Type**: `str`

### `render_with_context`

`render_with_context(context, buffer, *args, **kwargs) -> None`

Render the template using an existing [liquid.Context](Context) and output buffer. `args` and
`kwargs` are passed to `dict()`. The resulting dictionary is added to the render context.

**Parameters**:

- `context: liquid.Context` - A render context.

- `buffer: TextIO` - File-like object to which rendered text is written.

**Return Type**: `None`

### `render_with_context_async`

`async render_with_context_async(context, buffer, *args, **kwargs) -> None`

An async version of [liquid.BoundTemplate.render_with_context_async()](#async-render_with_context_async)

**Return Type**: `None`

### `is_up_to_date_async`

`async is_up_to_date_async() -> bool`

Return `True` if the template is up to date, `False` otherwise.
