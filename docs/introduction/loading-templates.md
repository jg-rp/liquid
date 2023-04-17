# Loading Templates

You can load templates from a file system or database, for example, by creating an [`Environment`](../api/environment.md) and configuring a template _loader_. You'd also need a loader if you want to use the built-in [`{% include %}`](../language/tags.md#include) or [`{% render %}`](../language/tags.md#render) tags.

[`Environment.get_template()`](../api/environment.md#get_template) and [`Environment.get_template_async()`](../api/environment.md#get_template_async) accept a template name and return a [`BoundTemplate`](../api/bound-template.md). That is a template bound to the environment, ready to be rendered. It is up to the loader to interpret a template name. In the case of [`FileSystemLoader`](../api/filesystemloader.md), the name would be a file name, possibly preceded by a path relative to the configured search path.

Available, built-in loaders are [`CachingFileSystemLoader`](../api/cachingfilesystemloader.md), [`FileSystemLoader`](../api/filesystemloader.md), [`FileExtensionLoader`](../api/fileextensionloader.md), [`DictLoader`](../api/dictloader.md) and [`ChoiceLoader`](../api/choiceloader.md). See also [custom loaders](../guides/custom-loaders.md), and examples of a [`FrontMatterFileSystemLoader`](../guides/custom-loaders.md#front-matter-loader) and an [`AsyncDatabaseLoader`](../guides/custom-loaders.md#async-database-loader).

This example assumes a folder called `templates` exists in the current working directory, and that template files `index.html` and `some-list.html` exist within it.

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

By default, every [`Environment`](../api/environment.md) is created with an empty [`DictLoader`](../api/dictloader.md). Specify an alternative template loader using the `loader` argument.

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

```html title="output"
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
Notice how whitespace is output unchanged. See [`whitespace control`](../language/introduction.md#whitespace-control) for more information.
:::

## Caching File System Loader

**_New in version 1.9.0_**

When rendering partial templates with [`{% include %}`](../language/tags.md#include) or [`{% render %}`](../language/tags.md#render), or making use of Python Liquid's [template inheritance features](../extra/tags.md#extends--block), it is recommended to use a [`CachingFileSystemLoader`](../api/cachingfilesystemloader.md) or a custom loader that handles its own cache.

```python
from liquid import CachingFileSystemLoader
from liquid import Environment

loader = CachingFileSystemLoader("templates/", cache_size=500)
env = Environment(loader=loader)

# ...
```
