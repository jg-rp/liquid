# liquid.loaders.make_choice_loader

**_New in version 1.12.0_**

A _choice loader_ factory returning one of `CachingChoiceLoader` or `ChoiceLoader` depending on the given arguments.

```python
make_choice_loader(
    loaders: List[BaseLoader],
    *,
    auto_reload: bool = True,
    namespace_key: str = "",
    cache_size: int = 300
) -> BaseLoader
```

A `CachingChoiceLoader` is returned if _cache_size_ > 0, otherwise a `ChoiceLoader` is returned. _auto_reload_ and _namespace_key_ are ignored if _cache_key_ is less than 1.

**Parameters**:

- `loaders: List[BaseLoader]` - A list of template loaders implementing `liquid.loaders.BaseLoader`.

- `auto_reload: bool = True` - If `True`, automatically reload a cached template if it has been updated.

- `namespace_key: str = ""` - The name of a global render context variable or loader keyword argument that resolves to the current loader "namespace" or "scope".

- `cache_size: int: 300` - The maximum number of templates to hold in the cache before removing the least recently used template.
