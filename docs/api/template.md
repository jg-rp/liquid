---
id: Template
---

# liquid.Template

A factory function. Create a [`liquid.template.BoundTemplate`](./bound-template.md), automatically creating a [`liquid.Environment`](./environment.md) to bind it to.

## `Template`

`Template(source, [options]) -> liquid.template.BoundTemplate`

**Parameters:**

- `source: str` - The liquid template source code.

- `tag_start_string: str` - The sequence of characters indicating the start of a liquid tag.
  Defaults to `{%`.

- `tag_end_string: str` - The sequence of characters indicating the end of a liquid tag. Defaults to
  `%}`.

- `statement_start_string: str` - The sequence of characters indicating the start of an output
  statement. Defaults to `{{`.

- `statement_end_string: str` - The sequence of characters indicating the end of an output
  statement. Defaults to `}}`.

- `comment_start_string: str` - The sequence of characters indicating the start of a comment.
  Defaults to `{#`. `template_comments` must be `True` for `comment_start_string` to have any
  effect.

- `comment_end_string: str` - The sequence of characters indicating the end of a comment. Defaults
  to `#}`. `template_comments` must be `True` for `comment_end_string` to have any effect.

- `template_comments: bool` - If `True`, enable template comments. Where, by default, anything
  between `{#` and `#}` is considered a comment. Defaults to `False`.

- `tolerance: Mode` - Indicates how tolerant to be of errors. Must be one of `Mode.LAX`, `Mode.WARN`
  or `Mode.STRICT`. Defaults to `Mode.STRICT`.

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

- `expression_cache_size: int` - The capacity of each of the common expression caches. Defaults to
  `0`, disabling expression caching.

- `globals: Optional[Mapping[str, object]]` - An optional mapping that will be added to the context
  every time the resulting `BoundTemplate` is rendered. Defaults to `None`.

**Return type:** [`liquid.template.BoundTemplate`](./bound-template.md)
