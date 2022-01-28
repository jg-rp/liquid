# Loading Templates

You can load templates from a file system or database, for example, by creating an
[Environment](../api/Environment) and configuring a template _loader_. You'd also need a loader if
you want to use the built-in [include](../language/tags#include) or [render](../language/tags#render)
tags.

[Environment.get_template()](../api/Environment#get_template) and [Environment.get_template_async()](../api/Environment#get_template_async)
accept a template name and return a [BoundTemplate](../api/BoundTemplate). That is a template bound
to the environment, ready to be rendered. It is up to the loader to interpret a template name. In
the case of [FileSystemLoader](../api/FileSystemLoader), the name would be a file name, possibly
preceded by a path relative to the configured search path.

This example assumes a folder called `templates` exists in the current working directory, and that
template files `index.html` and `some-list.html` exist within it.

```html title="templates/index.html"
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>{{ page_title }}</title>
  </head>
  <body>
    <h1>{{ heading }}</h1>
    {% render 'some-list.html' with people %}
  </body>
</html>
```

```html title="templates/some-list.html"
<ul>
  {% for person in people %}
  <li>{{ person.name }}</li>
  {% endfor %}
</ul>
```

By default, every [Environment](../api/Environment) is created with an empty [DictLoader](../api/DictLoader).
Specify an alternative template loader using the `loader` argument.

```python
from liquid import Environment
from liquid import FileSystemLoader

env = Environment(loader=FileSystemLoader("templates/"))

people = [
    {"name": "John"},
    {"name": "Sally"},
]

template = env.get_template("index.html")
print(template.render(
    heading="Some List",
    page_title="Awesome Title",
    people=people,
))
```

```
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Awesome Title</title>
  </head>
  <body>
    <h1>Some List</h1>
    <ul>

  <li>John</li>

  <li>Sally</li>

</ul>
  </body>
</html>
```

:::info
Notice how whitespace is output unchanged. See [whitespace control](../language/introduction#whitespace-control)
for more information.
:::

Available, built-in loaders are [FileSystemLoader](../api/FileSystemLoader), [FileExtensionLoader](../api/FileExtensionLoader), [DictLoader](../api/DictLoader) and [ChoiceLoader](../api/ChoiceLoader). See also [custom loaders](../guides/custom-loaders), and examples of a [FrontMatterFileSystemLoader](../guides/custom-loaders#front-matter-loader) and an [AsyncDatabaseLoader](../guides/custom-loaders#async-database-loader).
