# liquid.loaders.CachingFileSystemLoader

A loader that inherits from [`FileExtensionLoader`](./fileextensionloader.md) and caches parsed templates in an LRU cache.

## CachingFileSystemLoader

```python
CachingFileSystemLoader(
    search_path: Union[
        str, Path, Iterable[Union[str, Path]]
    ],
    encoding: str = "utf-8",
    ext: str = ".liquid",
    *,
    auto_reload: bool = True,
    namespace_key: str = "",
    cache_size: int = 300
)
```

**Parameters**:

- `search_path: Union[str, Path, Iterable[Union[str, Path]]]` - One or more paths to search.

- `encoding: str = "utf-8"` - Open template files with the given encoding. Defaults to `"utf-8"`.

- `ext: str = ".liquid"` - A default file extension. Should include a leading period. Defaults to `.liquid`.

- `auto_reload: bool = True` - If `True`, automatically reload a cached template if it has been updated.

- `namespace_key: str = ""` - The name of a global render context variable or loader keyword argument that resolves to the current loader "namespace" or "scope".

  If you're developing a multi-user application, a good namespace might be `uid`, where `uid` is a unique identifier for a user and templates are arranged in folders named for each `uid` inside the search path.

- `cache_size: int: 300` - The maximum number of templates to hold in the cache before removing the least recently used template.
