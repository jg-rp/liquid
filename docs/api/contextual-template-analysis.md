# liquid.template.ContextualTemplateAnalysis

The result of analyzing a Liquid template using [`BoundTemplate.analyze_with_context()`](./bound-template.md#analyze_with_context).

## `ContextualTemplateAnalysis`

`class ContextualTemplateAnalysis(*, all_variables, local_variables, undefined_variables, filters)`

Each of the following properties is a dictionary mapping variable or filter names to the number of times that variable was referenced.

## Properties

### `all_variables`

All variables references along a path through the template's syntax tree.

### `local_variables`

The names of variables assigned using the built-in `assign`, `capture`, `increment` or `decrement` tags, or any custom tag that uses `Context.assign()`.

### `undefined_variables`

The names of variables that could not be resolved. If a name is referenced before it is assigned, it will appear in `undefined_variables` and `local_variables`.

### `filters`

The names of [filters](../language/introduction.md#filters) found in the template and any [included](../language/tags.md#include) or [rendered](../language/tags.md#render) templates.
