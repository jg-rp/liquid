The result of [rendering a template](rendering_templates.md) depends on the [context](api/render_context.md) in which it is rendered. That is, available variables and their values, and options set on the bound [Environment](environment.md).

Template _global_ variables are those added to a render context by application developers. From a template author's perspective, _globals_ are read-only and are available to all templates, including those rendered with the [`{% render %}`](tag_reference.md#render) tag.

Template _local_ variables are those defined by template authors using [`{% assign %}`](tag_reference.md#assign) and [`{% capture %}`](tag_reference.md#capture). Local variables can mask names defined in the global namespace, but never change them.

Named counters created with [`{% increment %}`](tag_reference.md#increment) and [`{% decrement %}`](tag_reference.md#decrement) have their own namespace. Outside of `increment` or `decrement`, Liquid will look in the counters namespace last, after locals and globals.

## Environment globals

The [`Environment`](api/environment.md) constructor accepts an optional `globals` argument, which should be a dictionary mapping variable names to their values. These variables get pinned to the environment and will be automatically merged with other variables for every template rendered from that environment.

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

## Template globals

Similar to [Environment globals](#environment-globals), you can pin global variables to a template when calling [`from_string()`](api/environment.md#liquid.Environment.from_string) or [`get_template()`](api/environment.md#liquid.Environment.get_template). Global variables set on a template will be merged with any set on its environment and added to each render context automatically.

If environment and template globals have conflicting names, template variables take priority over environment variables.

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

## Render arguments

Keyword arguments passed to [`BoundTemplate.render()`](api/template.md#liquid.BoundTemplate.render) are also added to the _global_ namespace, although, unlike environment and template globals, they do not persist between calls to `render()`.

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

Matter variables are those pinned to a [`Template`](api/template.md) by a [template loader](loading_templates.md). They could be from a [front matter loader](loading_templates.md#matter) or extra meta data from a database loader.

These, too, are merged into the _global_ namespace, taking priority over template globals,
but not `render()` keyword arguments.
