# Render Context

The result of rendering a template depends on the [context](../api/context) in which it is rendered.
That is, available variables and their values, and options set on the bound [Environment](../api/Environment).

## Environment Globals

You can add _global_ variables to an environment using the `globals` argument to the
[Environment](../api/Environment) constructor. `globals` should be a dictionary (or any Mapping)
mapping strings to Python objects. Environment globals are automatically added to the render
context of every template rendered with [Environment.from_string](../api/Environment#from_string)
and [Environment.get_template](../api/Environment#get_template), including templates rendered with
the [render tag](../language/tags#render).

```python
from liquid import Environment

env = Environment(globals={"site_name": "MySite"})

template = env.from_string("""\
    <html>
    <head>
        <title>{{ site_name }}</title>
    </head>
    </html>
""")

print(template.render())
```

```plain title="output"
<html>
<head>
    <title>MySite</title>
</head>
</html>
```

## Template Globals

Similar to [Environment Globals](#environment-globals), you can add global template variables to a
[liquid.template.BoundTemplate](../api/BoundTemplate). Globals set on a template will be merged with
any set on its environment and added to the render context automatically.

If environment and template globals have conflicting names, template variables take priority over
environment variables.

```python
from liquid import Environment

env = Environment(globals={"site_name": "MySite"})

source = """\
    <html>
    <head>
        <title>{{ site_name }} - {{ page.name }}</title>
    </head>
    </html>
"""

template = env.from_string(source, globals={"page": {"name": "Blog"}})
print(template.render())
```

```plain title="output"
<html>
<head>
    <title>MySite - Blog</title>
</head>
</html>
```

## Render Arguments

Keyword arguments passed to [liquid.template.BoundTemplate.render()](../api/BoundTemplate#render)
are also added to the _global_ namespace, although, unlike environment and template globals, they do
not persist between calls to `render()`.

`render()` keyword arguments take priority over environment and template globals.

```python
from liquid import Environment

env = Environment(globals={"site_name": "MySite"})

source = """\
    <html>
    <head>
        <title>{{ site_name }} - {{ page.name }}</title>
    </head>
    <body>
        <p>Hello, {{ user.name }}</p>
    </body>
    </html>
"""

template = env.from_string(source, globals={"page": {"name": "Blog"}})
print(template.render(user = {"name": "Sally"}))
```

```plain title="output"
<html>
<head>
    <title>MySite - Blog</title>
</head>
    <body>
        <p>Hello, Sally</p>
    </body>
</html>
```

## Matter

Matter variables are those that are added to a [template](../api/BoundTemplate) by a
[loader](loading-templates). They could be from a [front matter loader](../guides/custom-loaders#front-matter-loader)
or extra meta data from a [database loader](../guides/custom-loaders#async-database-loader).

These, too, are merged into the _global_ context namespace, taking priority over template globals,
but not `render()` keyword arguments.

## Namespaces

A new [liquid.Context](../api/context) is created automatically every time a template is rendered.
Each context manages multiple namespaces.

### globals

From a template designer's perspective, the _globals_ namespace is read-only. The built-in
[assign](../language/tags#assign) and [capture](../language/tags#capture) tags can _mask_ names
defined in the global namespace, but never change them.

Built from [environment globals](#environment-globals), [template globals](#template-globals),
[matter variables](#matter) and [keyword arguments](#render-arguments) passed to `render()`, the
global namespace is available to all templates, including those rendered with
[`{% render %}`](../language/tags#render).

### locals

The _local_ namespace is where variables set using [`{% assign %}`](../language/tags#assign) and
[`{% capture %}`](../language/tags#capture) are stored. When Liquid resolves a name, it looks in the
local namespace first, then the global namespace.

Some tags extend the local namespace for the duration of their block. For example, the
[`{% for %}`](../language/tags/#for) tag adds a `forloop` object, which goes out of scope when the
for loop has finished.

### counters

Named counters created with [`{% increment %}`](../language/tags#increment) and
[`{% decrement %}`](../language/tags#increment) have their own namespace. Outside of an `increment`
or `decrement` tag, Liquid will look in the counters namespace last, after [locals](#locals) and
[globals](#globals).
