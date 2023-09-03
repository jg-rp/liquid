---
id: Environment
---

# liquid.Environment

Shared configuration from which templates can be loaded and parsed. An environment is where you might register custom tags and filters, or store global render context variables that should be included with every template.

## `Environment`

`class Environment([options])`

**Parameters:**

- `tag_start_string: str` - The sequence of characters indicating the start of a liquid tag. Defaults to `{%`.

- `tag_end_string: str` - The sequence of characters indicating the end of a liquid tag. Defaults to `%}`.

- `statement_start_string: str` - The sequence of characters indicating the start of an output statement. Defaults to `{{`.

- `statement_end_string: str` - The sequence of characters indicating the end of an output statement. Defaults to `}}`.

- `comment_start_string: str` - The sequence of characters indicating the start of a comment. Defaults to `{#`. `template_comments` must be `True` for `comment_start_string` to have any effect.

- `comment_end_string: str` - The sequence of characters indicating the end of a comment. Defaults to `#}`. `template_comments` must be `True` for `comment_end_string` to have any effect.

- `template_comments: bool` - If `True`, enable template comments. Where, by default, anything between `{#` and `#}` is considered a comment. Defaults to `False`.

- `tolerance: Mode` - Indicates how tolerant to be of errors. Must be one of `Mode.LAX`, `Mode.WARN` or `Mode.STRICT`. Defaults to `Mode.STRICT`.

- `loader: Optional[liquid.loaders.BaseLoader]` - A template loader. If you want to use the builtin "render" or "include" tags, a loader must be configured. Defaults to an empty [`liquid.loaders.DictLoader`](./dictloader.md).

- `undefined: liquid.Undefined` - A subclass of Undefined that represents undefined values. Could be one of the built-in undefined types, Undefined, DebugUndefined or StrictUndefined. Defaults to `Undefined`, an undefined type that silently ignores undefined values.

- `strict_filters: bool` - If `True`, will raise an exception upon finding an undefined filter. Otherwise undefined filters are silently ignored. Defaults to `True`.

- `autoescape: bool` - If `True`, all context values will be HTML-escaped before output unless they've been explicitly marked as "safe". Requires the package Markupsafe. Defaults to `False`.

- `auto_reload: bool` - If `True`, loaders that have an `uptodate` callable will reload template source data automatically. For deployments where template sources don't change between service reloads, setting auto_reload to False can yield an increase in performance by avoiding calls to `uptodate`. Defaults to `True`.

- `cache_size: int` - The capacity of the template cache in number of templates. Defaults to `300`. If `cache_size` is `None` or less than `1`, it has the effect of setting `auto_reload` to `False`.

- `expression_cache_size: int` - The capacity of each of the common expression caches. Defaults to `0`, disabling expression caching.

- `globals: Optional[Mapping[str, object]]` - An optional mapping that will be added to the context of any template loaded from this environment. Defaults to `None`.

## Class Attributes

### `context_depth_limit`

**Type**: `ClassVar[int]`

The maximum number of times a render context can be extended or wrapped before a `ContextDepthError` is raised. Defaults to `30`.

### `loop_iteration_limit`

**Type**: `ClassVar[Optional[int]]`

The maximum number of bytes (according to sys.getsizeof) allowed in a template's local namespace, per render, before a `LocalNamespaceLimitError` exception is raised. Note that we only count the size of the local namespace values, not its keys. Defaults to `None`.

### `local_namespace_limit`

**Type**: `ClassVar[int]`

The maximum number of loop iterations allowed before a `liquid.exceptions.LoopIterationLimitError` is raised. Defaults to `None`.

### `output_stream_limit`

**Type**: `ClassVar[int]`

The maximum number of bytes that can be written to a template's output stream, per render, before an `OutputStreamLimitError` exception is raised. Defaults to `None`.

### `template_class`

**Type**: `Type[liquid.template.BoundTemplate]`

[`Environment.get_template()`](#get_template) and [`Environment.from_string()`](#from_string) return an instance of [`Environment.template_class`](#template_class). Defaults to [`liquid.template.BoundTemplate`](./bound-template.md).

### `render_whitespace_only_blocks`

**Type**: `bool`

Indicates if block tags that, when rendered, contain whitespace only should be output. Defaults to `False`, meaning empty blocks are suppressed.

## Properties

### `undefined`

**Type**: `Type[liquid.Undefined]`

The undefined type. When an identifier can not be resolved, an instance of undefined is returned.

### `strict_filters`

**Type**: `bool`

Indicates if an undefined filter should raise an exception or be ignored.

### `autoescape`

**Type**: `bool`

Indicates if auto-escape is enabled.

### `tags`

**Type**: `Dict[str, liquid.tag.Tag]`

A dictionary mapping tag names to liquid.tag.Tag instances.

### `filters`

**Type**: `Dict[str, Callable[..., Any]`

A dictionary mapping filter names to callable objects implementing a filter's behavior.

### `mode`

**Type**: `liquid.Mode`

The current tolerance mode.

### `cache`

**Type**: `MutableMapping[Any, Any]`

The template cache.

### `auto_reload`

Indicates if automatic reloading of templates is enabled.

### `globals`

**Type**: `Mapping[str, object]`

A dictionary of variables that will be added to the context of every template rendered from the environment.

## Methods

### `add_filter`

`add_filter(name, func) -> None`

Register a filter function with the environment.

**Parameters:**

- `name: str` - The filter's name. Does not need to match the function name. This is what you'll use to apply the filter to an expression in a liquid template.

- `func: Callable[.., Any]` - Any callable that accepts at least one argument, the result of the expression the filter is applied to.

**Return type:** `None`

### `add_tag`

`add_tag(tag) -> None`

Register a liquid tag with the environment. Built-in tags are registered for you automatically with every new `Environment`.

**Parameters:**

- `tag: Type[liquid.tag.Tag]` - The [`Tag`](./tag.md) class to register. Not a class instance.

**Return type:** `None`

### `from_string`

`from_string(source, [options]) -> liquid.template.BoundTemplate`

Parse the given string as a Liquid template.

**Parameters:**

- `source: str` - The liquid template source code.

- `name: str` - Name of the template. Available as Template.name. Defaults to the empty string.

- `path: Optional[Union[str, pathlib.Path]]` - Optional path or identifier to the origin of the template. Defaults to `None`.

- `globals: Optional[Mapping[str, object]]` - An optional mapping of context variables made available every time the resulting template is rendered. Defaults to `None`.

- `matter: Optional[Mapping[str, object]]` - Optional mapping containing variables associated with the template. Could be front matter or other meta data. Defaults to `None`.

**Returns:** A parsed template bound to the environment and ready to be rendered.  
**Return type:** [`liquid.template.BoundTemplate`](./bound-template.md)

### `get_template`

`get_template(name, globals=None) -> liquid.template.BoundTemplate`

Load and parse a template using the configured loader.

**Parameters:**

- `name: str` - The template's name or identifier. The loader is responsible for interpreting the name.

- `globals: Optional[Mapping[str, object]]` - A mapping of context variables made available every time the resulting template is rendered.

**Returns:** A parsed template bound to the environment and ready to be rendered.  
**Return type:** [`liquid.template.BoundTemplate`](./bound-template.md)  
**Raises:** [`liquid.exceptions.TemplateNotFound`](./exceptions.md#liquidexceptionstemplatenotfound): If a template with the given name can not be found.

### `get_template_async`

`async get_template_async(name, globals=None) -> liquid.template.BoundTemplate`

An async version of [`get_template()`](#get_template).

### `analyze_tags`

`analyze_tags(name, *, context = None, inner_tags = None, **kwargs) -> liquid.TagAnalysis`

Audit template tags without parsing source text into an abstract syntax tree.

This is useful for identifying unknown, misplaced and unbalanced tags in a template's source text. See also [`BoundTemplate.analyze()`](./bound-template.md#analyze).

**Parameters:**

- `name: str` - The template's name or identifier, as you would use with [`get_template()`](#get_template). Use [`analyze_tags_from_string()`](#analyze_tags_from_string) to audit tags in template text without using a template [loader](../introduction/loading-templates.md).

- `context: Optional["Context"]` - An optional render context the loader might use to modify the template search space. If given, uses `get_source_with_context()` of the current loader instead of `get_source()`, and keywords arguments are passed along to `get_source_with_context()` too.

- `inner_tags: Optional[InnerTagMap]` - A mapping of block tags to a list of allowed "inner" tags for the block. For example, `{% if %}` blocks are allowed to contain `{% elsif %}` and `{% else %}` tags. Defaults to mapping suitable for the built-in block tags.

**Returns:** A tag audit including the location of any unknown tags and any unbalanced block tags.  
**Return type:** [`liquid.TagAnalysis`](./tag-analysis.md)  
**Raises:** [`liquid.exceptions.TemplateNotFound`](./exceptions.md#liquidexceptionstemplatenotfound): If a template with the given name can not be found.

### `analyze_tags_async`

`async analyze_tags_async(name, *, context = None, inner_tags = None, **kwargs) -> liquid.TagAnalysis`

An async version of [`analyze_tags()`](#analyze_tags).

### `analyze_tags_from_string`

`analyze_tags_from_string(source, name = "<string>", *, inner_tags = None) -> liquid.TagAnalysis`

Analyze tags in template source text against those registered with this environment.

**Parameters:**

- `source: str` - The source text of the template.

- `name: str` - A name or identifier for the template. Defaults to `"<string>"`.

- `inner_tags: Optional[InnerTagMap]` - A mapping of block tags to a list of allowed "inner" tags for the block. For example, `{% if %}` blocks are allowed to contain `{% elsif %}` and `{% else %}` tags. Defaults to mapping suitable for the built-in block tags.

**Returns:** A tag audit including the location of any unknown tags and any unbalanced block tags.  
**Return type:** [`liquid.TagAnalysis`](./tag-analysis.md)
