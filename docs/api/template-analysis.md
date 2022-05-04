# liquid.template.TemplateAnalysis

The result of analyzing a template's variables using [BoundTemplate.analyze()](./bound-template.md#analyze).

## `TemplateAnalysis`

`class TemplateAnalysis(*, variables, local_variables, global_variables, failed_visits, unloadable_partials,)`

Each of the following properties is a dictionary mapping variable names to a list of two-tuples. Each tuple holds the location of a reference to the name as `(<template name>, <line number>)`. If a name is referenced multiple times, it will appear multiple times in the list. If a name is referenced before it is "assigned", it will appear in `local_variables` and `global_variables`.

## Properties

### `variables`

All referenced variables, whether they are in scope or not. Including references to names such as `forloop` from the `for` tag.

### `local_variables`

Template variables that are added to the template local scope, whether they are subsequently used or not.

### `global_variables`

Template variables that, on the given line number and "file", are out of scope or are assumed to be "global". That is, expected to be included by the application developer rather than a template author.

### `failed_visits`

Names of AST `Node` and `Expression` objects that could not be visited, probably because they do not implement a `children` method.

### `unloadable_partials`

Names or identifiers of partial templates that could not be loaded. This will be empty if `follow_partials` is `False`.
