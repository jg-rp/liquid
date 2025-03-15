A template loader is a class inheriting from [`BaseLoader`](api/loaders.md#liquid.loader.BaseLoader). It is responsible for finding template source text given a name or identifier, and will be called upon whenever you or a tag call [`Environment.get_template()`](api/environment.md#liquid.Environment.get_template) or await [`Environment.get_template_async()`](api/environment.md#liquid.Environment.get_template_async).

To use one of the template loaders described here, pass an instance of your chosen loader as the `loader` argument when constructing a Liquid [`Environment`](environment.md).

## Built-in loaders

### Dictionary loader

[`DictLoader`](api/loaders.md#liquid.DictLoader) is a template loader that stores template source text in memory using a dictionary. If you're experimenting with Liquid or if all your templates are known at application startup time and they all fit in RAM, then `DictLoader` is a good choice.

Simply pass a dictionary mapping template names to template source text to the `DictLoader` constructor.

```python
from liquid import DictLoader
from liquid import Environment

env = Environment(
    loader=DictLoader(
        {
            "index": "{% render 'header' %}\nbody\n{% render 'footer' %}",
            "header": "some header",
            "footer": "a footer",
        }
    )
)

template = env.get_template("index")
print(template.render())
```

```plain title="output"
some header
body
a footer
```

### Caching dictionary loader

[`CachingDictLoader`](api/loaders.md#liquid.CachingDictLoader) is a [dictionary loader](#dictionary-loader) that maintains an in-memory LRU cache of parsed templates, so as to avoid parsing the same source text multiple times unnecessarily.

As well as a dictionary mapping template names to template source text, the `CachingDictLoader` constructor takes an optional `capacity` argument to control the maximum size of the cache. The default capacity is 300 templates.

```python
from liquid import CachingDictLoader
from liquid import Environment

env = Environment(
    loader=CachingDictLoader(
        {
            "index": "{% render 'header' %}\nbody\n{% render 'footer' %}",
            "header": "some header",
            "footer": "a footer",
        }
    )
)

template = env.get_template("index")
assert env.get_template("index") is template
```

### File system loader

[`FileSystemLoader`](api/loaders.md#liquid.FileSystemLoader) is a template loader that reads source text from files on a file system. Its first argument, `search_path`, is a path to a folder containing Liquid templates, either as a string or `pathlib.Path`. `search_path` can also be a list of paths to search in order.

In this example, calls to [`Environment.get_template()`](api/environment.md#liquid.Environment.get_template) will look for templates in a folder called `templates` relative to the current directory.

```python
from liquid import Environment
from liquid import FileSystemLoader

env = Environment(loader=FileSystemLoader("templates/"))
```

If a file called `index.html` exists in `./templates`, we could render it with `{% render 'index.html' %}`. To avoid having to include `.html` in every `render` tag, we can give `FileSystemLoader` a default file extension. It should include a leading `.`.

```python
from liquid import Environment
from liquid import FileSystemLoader

env = Environment(loader=FileSystemLoader("templates/", ext=".html"))
```

If your templates are organized in sub folders of `./templates`, you can include the relative path to a template in a `render` tag, `{% render 'snippets/footer' %}`, but you won't be allowed to escape out of `./templates`. This would raise a `TemplateNotFoundError`.

```liquid
{% render '../../path/to/private/file' %}
```

### Caching file system loader

[`CachingFileSystemLoader`](api/loaders.md#liquid.CachingFileSystemLoader) is a [file system loader](#file-system-loader) that maintains an in-memory LRU cache of parsed templates, so as to avoid reading and parsing the same source text multiple times unnecessarily.

As well as `search_path` and `ext` arguments covered in the [file system loader](#file-system-loader) section above, `CachingFileSystemLoader` takes optional `auto_reload` and `capacity` arguments.

`capacity` is the maximum number of templates that can fit in the cache and defaults to `300` templates.

`auto_reload` is a flag to indicate if the template loader should check to see if each cached template has been modified since it was last loaded. If `True` and template source text has been modified on-disk, that source text will automatically be read and parsed again. `auto_reload` defaults to `True`.

```python
from liquid import Environment
from liquid import CachingFileSystemLoader

loader = CachingFileSystemLoader(
    "/var/www/templates/",
    ext=".liquid",
    auto_reload=True,
    capacity=1000,
)

env = Environment(loader=loader)
```

### Package loader

[`PackageLoader`](api/loaders.md#liquid.PackageLoader) is a template loader that reads template source text from Python packages installed in your Python environment. You should pass the name of the package and, optionally, one or more paths to directories containing template source text within the package. The default `package_path` is `templates`.

Just like [`FileSystemLoader`](#file-system-loader), `PackageLoader` accepts a default file extension, `ext`. This time it defaults to `.liquid`.

```python
from liquid import Environment
from liquid import PackageLoader

loader = PackageLoader(
    "awesome_templates",
    package_path="path/to/templates",
    ext=".liquid",
)

env = Environment(loader=loader)
```

### Choice loader

[`ChoiceLoader`](api/loaders.md#liquid.ChoiceLoader) and [`CachingChoiceLoader`](api/loaders.md#liquid.CachingChoiceLoader) are template loaders that delegate to a list of other template loaders. Each one is tried in turn until a template is found.

When using `CachingChoiceLoader`, you should probably avoid delegating to other caching loaders.

```python
from liquid import CachingFileSystemLoader
from liquid import ChoiceLoader
from liquid import DictLoader
from liquid import Environment

base_loader = DictLoader({"foo": "some template source text"})
overlay_loader = CachingFileSystemLoader("templates/")
loader = ChoiceLoader([overlay_loader, base_loader])

env = Environment(loader=loader)
```

## Custom loaders

If you want to load templates from a database or over a network, you'll need to write your own template loader. Simply inherit from [`BaseLoader`](api/loaders.md#liquid.loader.BaseLoader) and implement [`get_source()`](api/loaders.md#liquid.loader.BaseLoader.get_source) and, possibly, [`get_source_async()`](api/loaders.md#liquid.loader.BaseLoader.get_source_async).

`get_source()` should return an instance of [`TemplateSource`](api/loaders.md#liquid.loader.TemplateSource), which is a named tuple containing source text, the template's name, an optional `uptodate` callable and any extra data you want bound to the template.

Take a look at [source code for the built-in loaders](https://github.com/jg-rp/python-liquid/tree/main/liquid/builtin/loaders) for examples.

### Load context

[`get_source()`](api/loaders.md#liquid.loader.BaseLoader.get_source) takes an optional `context` argument. When [`Environment.get_template()`](api/environment.md#liquid.Environment.get_template) is called from a tag, like [`render`](tag_reference.md), the active render context will be passed along to `get_source()`. Loaders can then choose to use render context data to dynamically refine template names and loader search paths.

Arbitrary keyword arguments can also be passed to [`Environment.get_template()`](api/environment.md#liquid.Environment.get_template). These too are passed along to `get_source()`, and can also be used by custom template loaders to refine the template source search space.

For example, all built-in tags that call [`Environment.get_template()`](api/environment.md#liquid.Environment.get_template) pass a keyword argument called `tag` set to the name of the calling tag. We can use the tag name to mimic Shopify's `snippets` convention, where `{% include %}` and `{% render %}` automatically load templates from a subfolder call `snippets`.

```python
from pathlib import Path

from liquid import CachingFileSystemLoader
from liquid import Environment
from liquid import RenderContext
from liquid import TemplateSource


class SnippetsFileSystemLoader(CachingFileSystemLoader):
    def get_source(
        self,
        env: Environment,
        template_name: str,
        *,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> TemplateSource:
        if kwargs.get("tag") in ("include", "render"):
            snippet = Path("snippets").joinpath(template_name)
            return super().get_source(
                env, template_name=str(snippet), context=context, **kwargs
            )
        return super().get_source(
            env, template_name=template_name, context=context, **kwargs
        )
```

### Matter

Sometimes template source text comes with associated data. This could be meta data read from a database or _front matter_ read from the top of the file containing template source text. The [`TemplateSource`](api/loaders.md#liquid.loader.TemplateSource) object returned from [`get_source()`](api/loaders.md#liquid.loader.BaseLoader.get_source) facilitates these cases with `matter`, a dictionary mapping strings to arbitrary objects that will be merged with environment and template globals and bound to the resulting `Template` instance.

Here's an example of a template loader that reads front matter in YAML format.

```python
import re

import yaml

from liquid import CachingFileSystemLoader
from liquid import Environment
from liquid import RenderContext
from liquid import TemplateSource

RE_FRONT_MATTER = re.compile(r"\s*---\s*(.*?)\s*---\s*", re.MULTILINE | re.DOTALL)


class FrontMatterLoader(CachingFileSystemLoader):
    def get_source(
        self,
        env: Environment,
        template_name: str,
        *,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> TemplateSource:
        source, filename, uptodate, matter = super().get_source(env, template_name)
        match = RE_FRONT_MATTER.search(source)

        if match:
            # TODO: add some yaml error handling here.
            matter = yaml.load(match.group(1), Loader=yaml.SafeLoader)
            source = source[match.end() :]

        return TemplateSource(
            source,
            filename,
            uptodate,
            matter,
        )
```

### Caching mixin

Use [`CachingLoaderMixin`](api/loaders.md#liquid.CachingLoaderMixin) to add in-memory LRU caching to your custom template loaders. For example, here's the definition of `CachingDictLoader`.

```python
from liquid import CachingLoaderMixin
from liquid import DictLoader

class CachingDictLoader(CachingLoaderMixin, DictLoader):
    """A `DictLoader` that caches parsed templates in memory."""

    def __init__(
        self,
        templates: dict[str, str],
        *,
        auto_reload: bool = True,
        namespace_key: str = "",
        capacity: int = 300,
    ):
        super().__init__(
            auto_reload=auto_reload,
            namespace_key=namespace_key,
            capacity=capacity,
        )

        DictLoader.__init__(self, templates)
```
