# Render Context

The result of rendering a template depends on the [context](../api/context.md) in which it is rendered. That is, available variables and their values, and options set on the bound [`Environment`](../api/environment.md).

Template _global_ variables are those added to a render context by application developers. From a template author's perspective, _globals_ are read-only and are available to all templates, including those rendered with the [`{% render %}`](../language/tags.md#render) tag.

Template _Local_ variables are those defined by template authors using [`{% assign %}`](../language/tags.md#assign) and [`{% capture %}`](../language/tags.md#capture). Local variables can mask names defined in the global namespace, but never change them.

Named counters created with [`{% increment %}`](../language/tags.md#increment) and [`{% decrement %}`](../language/tags.md#decrement) have their own namespace. Outside of `increment` or `decrement`, Liquid will look in the counters namespace last, after _locals_ and _globals_.

## Environment Globals

You can add _global_ variables to an environment using the `globals` argument to the [`Environment`](../api/environment.md) constructor. `globals` should be a dictionary (or any Mapping) mapping strings to Python objects. Environment globals are automatically added to the render context of every [`Template`](../api/bound-template.md) created with [`Environment.from_string()`](../api/environment.md#from_string) and [`Environment.get_template()`](../api/environment.md#get_template), including templates rendered with the [render tag](../language/tags.md#render).

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

Similar to [Environment Globals](#environment-globals), you can pin global template variables to a [`liquid.template.BoundTemplate`](../api/bound-template.md). Globals set on a template will be merged with any set on its environment and added to each render context automatically.

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

Keyword arguments passed to [`liquid.template.BoundTemplate.render()`](../api/bound-template.md#render) are also added to the _global_ namespace, although, unlike environment and template globals, they do not persist between calls to `render()`.

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

Matter variables are those that are added to a [`Template`](../api/bound-template.md) by a [loader](./loading-templates.md). They could be from a [front matter loader](../guides/custom-loaders.md#front-matter-loader) or extra meta data from a [database loader](../guides/custom-loaders.md#async-database-loader).

These, too, are merged into the _global_ context namespace, taking priority over template globals,
but not `render()` keyword arguments.
