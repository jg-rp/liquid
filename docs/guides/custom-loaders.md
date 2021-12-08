# Custom Loaders

Loaders are responsible for finding a template's source text given a name or identifier. Built-in
loaders include a [FileSystemLoader](../api/filesystemloader), a [ChoiceLoader](../api/choiceloader)
and a [DictLoader](../api/dictloader). You might want to write a custom loader to load templates
from a database or add extra meta data to the template context, for example.

Write a custom loader class by inheriting from `liquid.loaders.BaseLoader` and implementing its
`get_source` method. Then pass an instance of your loader to a [liquid.Environment](../api/Environment)
as the `loader` argument.

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

`TemplateSource` is a named tuple containing the template source as a string, its name and an
optional `uptodate` callable. If `uptodate` is not `None` it should be a callable that returns
`False` if the template needs to be loaded again, or `True` otherwise.

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

## Front Matter Loader

Loaders can add to a template's render context using the `matter` argument to `TemplateSource`. This
example implements a Jekyll style front matter loader.

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

Template loaders can implement `get_source_async`. When a template is rendered by awaiting
`render_async` instead of calling `render`, `{% render %}` and `{% include %}` tags will use
`get_template_async` of the bound `Environment`, which delegates to `get_source_async` of the
configured loader.

For example, `AsyncDatabaseLoader` will load templates from a PostgreSQL database using
[asyncpg](https://github.com/MagicStack/asyncpg).

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

This example extends `FileSystemLoader` to automatically append a file extension if one is
missing.

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
