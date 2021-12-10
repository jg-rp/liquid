# Async Support

Python Liquid supports loading and rendering templates asynchronously. When [Template.render_async()](../api/BoundTemplate)
is awaited, [render](../language/tags#render) and [include](../language/tags#include) tags will use
[Environment.get_template_async()](../api/Environment#get-template-async), which delegates to [get_source_async()](../api/filesystemloader#get_source_async) of the configured template loader.

```python
import asyncio
from liquid import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates/"))

async def coro():
    template = await env.get_template_async("index.html")
    return await template.render_async(you="World")

result = asyncio.run(coro())
```

## Async Loaders

Custom template loaders should implement [get_source_async()](../api/filesystemloader#get_source_async)
and pass a coroutine as the `uptodate` argument to `TemplateSource`.

See [AsyncDatabaseLoader](../guides/custom-loaders#async-database-loader) for an example that loads
templates from a PostgreSQL database asynchronously.

## Async Drops

Custom [drops](objects-and-drops) can implement `__getitem_async__()`. If an instance of a drop that
implements `__getitem_async__()` appears in a [render_async()](../api/BoundTemplate#render_async)
context, `__getitem_async__()` will be awaited instead of calling `__getitem__()`.

Most likely used for lazy loading objects from a database, an async drop could look something like
this.

```python
class AsyncCollection(abc.Mapping):
    def __init__(self, val):
        self.keys = ["products"]
        self.cached_products = []

    def __len__(self):
        return 1

    def __iter__(self):
        return iter(self["products"])

    async def __aiter__(self):
        # Note that Liquid's built-in `for` loop does not yet support async iteration.
        return iter(self.__getitem_async__("products"))

    def __getitem__(self, k):
        if not self.cached_products:
            # Blocking IO here
            self.cached_products = get_stuff_from_database()
        return self.cache_products

    async def __getitem_async__(self, k):
        if not self.cached_products:
            # Do async IO here.
            self.cached_products = await get_stuff_from_database_async()
        return self.cache_products
```
