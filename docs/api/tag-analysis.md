# liquid.TagAnalysis

**_New in version 1.7.0_**

The result of analyzing a template's tags with [`Environment.analyze_tags()`](./environment.md#analyze_tags), [`Environment.analyze_tags_async()`](./environment.md#analyze_tags_async) and [`Environment.analyze_tags_from_string()`](./environment.md#analyze_tags_from_string).

## `TagAnalysis`

`class TagAnalysis(*, env, name, tokens, inner_tags)`

Each of the following properties maps tag names to a list of their locations Locations are (template_name, line_number) tuples.

Note that `raw` tags are not included at all. The lexer converts them to text tokens before we get a chance to analyze them.

Also be aware that reported `unexpected_tags` don't handle the possibility of an "inner" tag appearing in a partial template (using `{% include %}`), where appropriate enclosing block tags are in the parent template.

## Properties

### `tags`

A mapping of tag names to their locations. Excludes "end" and inner tags, includes unknown tags (those that are not registered with the environment, possibly typos).

### `all_tags`

A mapping of tag names to their locations, including "end" and inner tags.

### `unclosed_tags`

Block tag names and locations that do not have a matching "end" tag.

### `unexpected_tags`

Inner tag names and locations that do not have an appropriate enclosing block tag. Like an `{% else %}` appearing outside an `{% if %}` or `{% unless %}` block, for example.

### `unknown_tags`

The names and locations of tags that are not registered with the environment. If there's an unregistered block tag, only the tag starting the block will be reported. In the case of an "end" tag typo, the "end" tag will be reported as "unknown" and the start tag will be in [`unclosed_tags`](#unclosed_tags).
