---
id: Environment
---

# liquid.Environment

Shared configuration from which templates can be loaded and parsed. An environment is where you
might register custom tags and filters, or store global context variables that should be included
with every template.

## `Environment`

`class Environment([[options]])`

**Parameters:**

- `tag_start_string: str` - The sequence of characters indicating the start of a liquid tag.
  Defaults to `{%`.

- `tag_end_string: str` - The sequence of characters indicating the end of a liquid tag. Defaults to
  `%}`.

- `statement_start_string: str` - The sequence of characters indicating the start of an output
  statement. Defaults to `{{`.

- `statement_end_string: str` - The sequence of characters indicating the end of an output
  statement. Defaults to `}}`.

- `tolerance: Mode` - Indicates how tolerant to be of errors. Must be one of `Mode.LAX`, `Mode.WARN`
  or `Mode.STRICT`. Defaults to `Mode.STRICT`.

- `loader: Optional[liquid.loaders.BaseLoader]` - A template loader. If you want to use the builtin
  "render" or "include" tags, a loader must be configured. Defaults to an empty
  [liquid.loaders.DictLoader](dictloader).

- `undefined: liquid.Undefined` - A subclass of Undefined that represents undefined values. Could be
  one of the built-in undefined types, Undefined, DebugUndefined or StrictUndefined. Defaults to
  `Undefined`, an undefined type that silently ignores undefined values.

- `strict_filters: bool` - If `True`, will raise an exception upon finding an undefined filter.
  Otherwise undefined filters are silently ignored. Defaults to `True`.

- `autoescape: bool` - If `True`, all context values will be HTML-escaped before output unless
  they've been explicitly marked as "safe". Requires the package Markupsafe. Defaults to `False`.

- `auto_reload: bool` - If `True`, loaders that have an `uptodate` callable will reload template
  source data automatically. For deployments where template sources don't change between service
  reloads, setting auto_reload to False can yield an increase in performance by avoiding calls to
  `uptodate`. Defaults to `True`.

- `cache_size: int` - The capacity of the template cache in number of templates. Defaults to `300`.
  If `cache_size` is `None` or less than `1`, it has the effect of setting `auto_reload` to `False`.

- `globals: Optional[Mapping[str, object]]` - An optional mapping that will be added to the context
  of any template loaded from this environment. Defaults to `None`.

## Properties

### undefined

**Type**: `Type[liquid.Undefined]`

The undefined type. When an identifier can not be resolved, an instance of undefined is returned.

### strict_filters

**Type**: `bool`

Indicates if an undefined filter should raise an exception or be ignored.

### autoescape

**Type**: `bool`

Indicates if auto-escape is enabled.

### tags

**Type**: `Dict[str, liquid.tag.Tag]`

A dictionary mapping tag names to liquid.tag.Tag instances.

### filters

**Type**: `Dict[str, Callable[..., Any]`

A dictionary mapping filter names to callable objects implementing a filter's behavior.

### mode

**Type**: `liquid.Mode`

The current tolerance mode.

### cache

**Type**: `MutableMapping[Any, Any]`

The template cache.

### auto_reload

Indicates if automatic reloading of templates is enabled.

### template_class

**Type**: `Type[liquid.template.BoundTemplate]`

[Environment.get_template()](#get_template) and [Environment.from_string()](#from_string) return an
instance of [Environment.template_class](#template_class). Defaults to
[liquid.template.BoundTemplate](BoundTemplate).

### globals

A dictionary of variables that will be added to the context of every template rendered from the
environment.

## Methods

### `add_filter`

`add_filter(name, func) -> None`

Register a filter function with the environment.

**Parameters:**

- `name: str` - The filter's name. Does not need to match the function name. This is what you'll use
  to apply the filter to an expression in a liquid template.

- `func: Callable[.., Any]` - Any callable that accepts at least one argument, the result of the
  expression the filter is applied to.

**Return type:** `None`

### `add_tag`

`add_tag(tag) -> None`

Register a liquid tag with the environment. Built-in tags are registered for you automatically with
every new `Environment`.

**Parameters:**

- `tag: Type[liquid.tag.Tag]` - The [Tag](tag) class to register. Not a class instance.

**Return type:** `None`

### `from_string`

`from_string(source, [options]) -> liquid.template.BoundTemplate`

Parse the given string as a Liquid template.

**Parameters:**

- `source: str` - The liquid template source code.

- `name: str` - Name of the template. Available as Template.name. Defaults to the empty
  string.

- `path: Optional[Union[str, pathlib.Path]]` - Optional path or identifier to the origin of the
  template. Defaults to `None`.

- `globals: Optional[Mapping[str, object]]` - An optional mapping of context variables made
  available every time the resulting template is rendered. Defaults to `None`.

- `matter: Optional[Mapping[str, object]]` - Optional mapping containing variables associated with
  the template. Could be front matter or other meta data. Defaults to `None`.

**Returns:** A parsed template bound to the environment and ready to be rendered.  
**Return type:** [liquid.template.BoundTemplate](BoundTemplate)

### `get_template`

`get_template(name, globals=None) -> liquid.template.BoundTemplate`

Load and parse a template using the configured loader.

**Parameters:**

- `name: str` - The template's name or identifier. The loader is responsible for interpreting the
  name.

- `globals: Optional[Mapping[str, object]]` - A mapping of context variables made available every
  time the resulting template is rendered.

**Returns:** A parsed template bound to the environment and ready to be rendered.  
**Return type:** [liquid.template.BoundTemplate](BoundTemplate)  
**Raises:** [liquid.exceptions.TemplateNotFound](exceptions#liquidexceptionstemplatenotfound): If a template with the given
name can not be found.

### `get_template_async`

`async get_template_async(name, globals=None) -> liquid.template.BoundTemplate`

An async version of [get_template](#environmentget_template).
