# Custom Loaders

Loaders are responsible for finding a template's source text given a name or identifier. Built-in loaders include a [`FileSystemLoader`](../api/filesystemloader.md), a [`FileExtensionLoader`](../api/fileextensionloader.md), a [`ChoiceLoader`](../api/choiceloader.md) and a [`DictLoader`](../api/dictloader.md). You might want to write a custom loader to load templates from a database or add extra meta data to the template context, for example.

Write a custom loader class by inheriting from `liquid.loaders.BaseLoader` and implementing its
`get_source` method. Then pass an instance of your loader to a [liquid.Environment](../api/environment.md) as the `loader` argument.

We could implement our own version of `DictLoader` like this.

```python title="myloaders.py"
from typing import TYPE_CHECKING
from typing import Dict

from liquid.loaders import BaseLoader
from liquid.loaders import TemplateSource
from liquid.exceptions import TemplateNotFound

if TYPE_CHECKING:
    from liquid import Environment

class DictLoader(BaseLoader):
    def __init__(self, templates: Dict[str, str]):
        self.templates = templates

    def get_source(self, _: Environment, template_name: str) -> TemplateSource:
        try:
            source = self.templates[template_name]
        except KeyError as err:
            raise TemplateNotFound(template_name) from err

        return TemplateSource(source, template_name, None)
```

`TemplateSource` is a named tuple containing the template source as a string, its name and an optional `uptodate` callable. If `uptodate` is not `None` it should be a callable that returns `False` if the template needs to be loaded again, or `True` otherwise.

You could then use `DictLoader` like this.

```python
from liquid import Environment
from myloaders import DictLoader

snippets = {
    "greeting": "Hello {{ user.name }}",
    "row": """
        <div class="row"'
            <div class="col">
            {{ row_content }}
            </div>
        </div>
        """,
}

env = Environment(loader=DictLoader(snippets))

template = env.from_string("""
    <html>
        {% include 'greeting' %}
        {% for i in (1..3) %}
        {% include 'row' with i as row_content %}
        {% endfor %}
    </html>
""")

print(template.render(user={"name": "Brian"}))
```

## Loading Sections and Snippets

**_New in version 1.1.3_**

Custom loaders can reference the name of the tag that's trying to load a template, if used from a tag like `{% include 'template_name' %}` or `{% render 'template_name' %}`, or any custom tag that uses `Context.get_template_with_context()`.

This is useful for situations where you want to load partial templates (or "snippets" or "sections") from sub folders within an existing search path, without requiring template authors to include sub folder names in every `include` or `render` tag.

`BaseLoader.get_source_with_context()` and `BaseLoader.get_source_with_context_async()` where added in Python Liquid version 1.1.3. These methods are similar to `get_source()` and `get_source_async()`, but are passed the active render context instead of an environment, and arbitrary keyword arguments that can be used by a loader to modify its search space. Their default implementations ignore context and keyword arguments, simply delegating to `get_source()` or `get_source_async()`.

:::note
`Context.get_template_with_context()` and `Context.get_template_with_context_async()` do not use the default template cache. The environment that manages the default template cache does not know what context variables and keyword arguments might be used to manipulate the search space or loaded template.
:::

This example extends [`FileExtensionLoader`](../api/fileextensionloader.md), making `.liquid` optional, and searches `./snippets/` (relative to the loaders search path) for templates when rendering with the built-in `include` tag.

```python
from pathlib import Path

from liquid import Context
from liquid.loaders import TemplateSource
from liquid.loaders import FileExtensionLoader

class SnippetsFileSystemLoader(FileExtensionLoader):
    def get_source_with_context(
        self,
        context: Context,
        template_name: str,
        **kwargs: str,
    ) -> TemplateSource:
        if kwargs.get("tag") == "include":
            section = Path("snippets").joinpath(template_name)
            return self.get_source(context.env, str(section))
        return self.get_source(context.env, template_name)
```

`tag` being parse as a keyword argument is a convention used by the built-in [`{% include %}`](../language/tags.md#include) and [`{% render %}`](../language/tags.md#render) tags. Custom tags are free to pass whatever keyword arguments they wish to `Context.get_template_with_context()`, and they will be passed on to `get_source_with_context()` of the configured loader.

This example leaves the `include` tag's search path alone, instead defining a `section` tag that inherits from `include` and searches for templates in the `sections/` subfolder of `templates/`.

```python
from pathlib import Path

from liquid import Context
from liquid import Environment
from liquid.loaders import FileExtensionLoader
from liquid.loaders import TemplateSource
from liquid.builtin.tags.include_tag import IncludeNode
from liquid.builtin.tags.include_tag import IncludeTag

class SectionNode(IncludeNode):
    tag = "section"

class SectionTag(IncludeTag):
    name = "section"
    node_class = SectionNode

class SectionFileSystemLoader(FileExtensionLoader):
    def get_source_with_context(
        self,
        context: Context,
        template_name: str,
        **kwargs: str,
    ) -> TemplateSource:
        if kwargs.get("tag") == "section":
            section = Path("sections").joinpath(template_name)
            return self.get_source(context.env, str(section))
        return self.get_source(context.env, template_name)

env = Environment(loader=SectionFileSystemLoader(search_path="templates/"))
env.add_tag(SectionTag)
```

## Loading with Context

**_New in version 1.1.3_**

When using Liquid in multi-user applications, a loader might need to narrow its search space depending on the current user. The classic example being Shopify, where, to be able to find the appropriate template, the loader must know what the current store ID is.

A loader can reference the current render context by implementing `BaseLoader.get_source_with_context()` and/or `BaseLoader.get_source_with_context_async()`. This example gets a `site_id` from the active render context and uses it in combination with the template's name to query an SQLite database. It assumes a table called `templates` exists with columns `source`, `updated`, `name` and `site_id`.

```python
import sqlite3
import functools

from liquid import Context
from liquid.loaders import BaseLoader
from liquid.loaders import TemplateSource
from liquid.exceptions import TemplateNotFound

class SQLiteLoader(BaseLoader):
    def __init__(self, con: sqlite3.Connection):
        self.con = con

    def get_source_with_context(
        self, context: Context, template_name: str, **kwargs: str
    ) -> TemplateSource:
        site_id = context.resolve("site_id")
        cur = self.con.cursor()
        cur.execute(
            "SELECT source, updated "
            "FROM templates "
            "WHERE name = ? "
            "AND site_id = ?",
            [template_name, site_id],
        )

        source = cur.fetchone()
        if not source:
            raise TemplateNotFound(template_name)

        return TemplateSource(
            source=source[0],
            filename=template_name,
            uptodate=functools.partial(
                self._is_site_up_to_date,
                name=template_name,
                site_id=site_id,
                updated=source[1],
            ),
        )

    def get_source(self, env: Environment, template_name: str) -> TemplateSource:
        cur = self.con.cursor()
        cur.execute(
            "SELECT source, updated FROM templates WHERE name = ?",
            [template_name],
        )

        source = cur.fetchone()
        if not source:
            raise TemplateNotFound(template_name)

        return TemplateSource(
            source=source[0],
            filename=template_name,
            uptodate=functools.partial(
                self._is_up_to_date,
                name=template_name,
                updated=source[1],
            ),
        )

    def _is_site_up_to_date(self, name: str, site_id: int, updated: str) -> bool:
        cur = self.con.cursor()
        cur.execute(
            "SELECT updated FROM templates WHERE name = ? AND site_id = ?",
            [name, site_id],
        )

        row = cur.fetchone()
        if not row:
            return False
        return updated == row[0]

    def _is_up_to_date(self, name: str, updated: str) -> bool:
        cur = self.con.cursor()
        cur.execute(
            "SELECT updated FROM templates WHERE name = ?",
            [name],
        )

        row = cur.fetchone()
        if not row:
            return False
        return updated == row[0]
```

## Front Matter Loader

Loaders can add to a template's render context using the `matter` argument to `TemplateSource`. This example implements a Jekyll style front matter loader.

```python
import re
import yaml  # Assumes pyyaml is installed

from liquid import Environment
from liquid.loaders import FileSystemLoader
from liquid.loaders import TemplateSource

RE_FRONT_MATTER = re.compile(r"\s*---\s*(.*?)\s*---\s*", re.MULTILINE | re.DOTALL)


class FrontMatterFileSystemLoader(FileSystemLoader):
    def get_source(
        self,
        env: Environment,
        template_name: str,
    ) -> TemplateSource:
        source, filename, uptodate, matter = super().get_source(env, template_name)
        match = RE_FRONT_MATTER.search(source)

        if match:
            # Should add some yaml error handling here.
            matter = yaml.load(match.group(1), Loader=yaml.Loader)
            source = source[match.end() :]

        return TemplateSource(
            source,
            filename,
            uptodate,
            matter,
        )
```

## Async Database Loader

Template loaders can implement `get_source_async()`. When a template is rendered by awaiting [`BoundTemplate.render_async()`](../api/bound-template.md#renderasync) instead of calling [`BoundTemplate.render()`](../api/bound-template.md#render), `{% render %}` and `{% include %}` tags will use `get_template_async` of the bound [`Environment`](../api/environment.md), which delegates to `get_source_async` of the configured loader.

For example, `AsyncDatabaseLoader` will load templates from a PostgreSQL database using [asyncpg](https://github.com/MagicStack/asyncpg).

```python
import datetime
import functools

import asyncpg

from liquid import Environment
from liquid.exceptions import TemplateNotFound
from liquid.loaders import BaseLoader
from liquid.loaders import TemplateSource


class AsyncDatabaseLoader(BaseLoader):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    def get_source(self, env: Environment, template_name: str) -> TemplateSource:
        raise NotImplementedError("async only loader")

    async def _is_up_to_date(self, name: str, updated: datetime.datetime) -> bool:
        async with self.pool.acquire() as connection:
            return updated == await connection.fetchval(
                "SELECT updated FROM templates WHERE name = $1", name
            )

    async def get_source_async(
        self, env: Environment, template_name: str
    ) -> TemplateSource:
        async with self.pool.acquire() as connection:
            source = await connection.fetchrow(
                "SELECT source, updated FROM templates WHERE name = $1", template_name
            )

        if not source:
            raise TemplateNotFound(template_name)

        return TemplateSource(
            source=source["source"],
            filename=template_name,
            uptodate=functools.partial(
                self._is_up_to_date, name=template_name, updated=source["updated"]
            ),
        )
```

## File Extension Loader

This example extends `FileSystemLoader` to automatically append a file extension if one is missing.

```python
from pathlib import Path

from typing import Union
from typing import Iterable

from liquid.loaders import FileSystemLoader


class FileExtensionLoader(FileSystemLoader):
    """A file system loader that adds a file name extension if one is missing."""

    def __init__(
        self,
        search_path: Union[str, Path, Iterable[Union[str, Path]]],
        encoding: str = "utf-8",
        ext: str = ".liquid",
    ):
        super().__init__(search_path, encoding=encoding)
        self.ext = ext

    def resolve_path(self, template_name: str) -> Path:
        template_path = Path(template_name)

        if not template_path.suffix:
            template_path = template_path.with_suffix(self.ext)

        # Don't allow "../" to escape the search path.
        if os.path.pardir in template_path.parts:
            raise TemplateNotFound(template_name)

        for path in self.search_path:
            source_path = path.joinpath(template_path)

            if not source_path.exists():
                continue
            return source_path
        raise TemplateNotFound(template_name)
```
