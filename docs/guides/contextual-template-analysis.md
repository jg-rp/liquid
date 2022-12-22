# Contextual Template Analysis

**_New in version 1.3.0_**

Complementing [static template analysis](./static-template-analysis.md), added in Python Liquid version 1.2.0, contextual template analysis renders a template and captures information about template variable and filter usage as it goes.

Given some [render context](../introduction/render-context.md) data, [`BoundTemplate.analyze_with_context()`](../api/bound-template.md#analyze_with_context) will visit nodes in a template's syntax tree as if it were being rendered, excluding those nodes that are not reachable using the current render context.

## Limitations

Due to some unfortunate design decisions, Python Liquid does not support template introspection from within a render context or `Expression` object. Meaning line numbers and template names are not available when using contextual template analysis. Only variable names are reported along with the number of times they were referenced. This is not the case with [static template analysis](./static-template-analysis.md).

It's also not currently possible to detect names added to a block's scope. For example, `forloop.index` will be included in the results object if referenced within a for loop block.

## Usage

[`BoundTemplate.analyze_with_context()`](../api/bound-template.md#analyze_with_context) and [`BoundTemplate.analyze_with_context_async()`](../api/bound-template.md#analyze_with_context_async) accept the same arguments as [`BoundTemplate.render()`](../api/bound-template.md#render). The returned object is an instance of [`ContextualTemplateAnalysis`](../api/contextual-template-analysis.md). Each of its properties is a dictionary mapping template variable name to the number of times that name was referenced.

`ContextualTemplateAnalysis.all_variables` includes all variable names discovered while rendering a template given some render context data. It will not include variables from blocks that would not have been rendered.

```python
from liquid import Template

template = Template("""\
{% assign fallback = 'anonymous' %}
{% if user %}
  Hello, {{ user.name }}.
{% else %}
  Hello, {{ fallback }}
{% endif %}
""")

# `user` is undefined
analysis = template.analyze_with_context()
print(list(analysis.all_variables))


# `user` is defined
analysis = template.analyze_with_context(user={"name": "Sally"})
print(list(analysis.all_variables))
```

```plain title="output"
['user', 'fallback']
['user', 'user.name']
```

## Local Variables

`ContextualTemplateAnalysis.local_variables` includes variable names that have been assigned with the `assign`, `capture`, `increment` or `decrement` tags, or any custom tag that uses `Context.assign()`.

```python
from liquid import Template

template = Template("""\
{% assign fallback = 'anonymous' %}
{% if user %}
  Hello, {{ user.name }}.
{% else %}
  Hello, {{ fallback }}
{% endif %}
""")

# `user` is undefined
analysis = template.analyze_with_context()
print(list(analysis.local_variables))
```

```plain title="output"
['fallback']
```

## Undefined variables

`ContextualTemplateAnalysis.undefined_variables` includes variable names that could not be resolved in the current render context. If a name is referenced before it is assigned, it will appear in `undefined_variables` and `local_variables`.

```python
from liquid import Template

template = Template("""\
{% assign fallback = 'anonymous' %}
{{ nosuchthing }}

{% if user %}
  Hello, {{ user.name }}.
{% else %}
  Hello, {{ fallback }}
{% endif %}
""")

# `user` is undefined
analysis = template.analyze_with_context()
print(list(analysis.undefined_variables))
```

```plain title="output"
['nosuchthing', 'user']
```

## Filters

**_New in version 1.7.0_**

`ContextualTemplateAnalysis.filters` includes the names of filters used in a template, including those found in [included](../language/tags.md#include) or [rendered](../language/tags.md#render) templates.

```python
from liquid import Template

template = Template(
    """\
{% assign fallback = 'anonymous' %}
{{ nosuchthing }}

{% if user %}
  Hello, {{ user.name | upcase }}.
{% else %}
  Hello, {{ fallback | downcase }}
{% endif %}
"""
)

analysis = template.analyze_with_context(user="Sue")
print(list(analysis.filters))
```

```plain title="output"
['upcase']
```
