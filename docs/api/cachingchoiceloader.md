# liquid.loaders.CachingChoiceLoader

A template loader inherits from [`ChoiceLoader`](./choiceloader.md) and caches parsed templates in memory.

## `CachingChoiceLoader`

```python
CachingChoiceLoader(
    loaders: List[BaseLoader],
    *,
    auto_reload: bool = True,
    namespace_key: str = "",
    cache_size: int = 300
)
```

**Parameters**:

- `loaders: List[BaseLoader]` - A list of template loaders implementing `liquid.loaders.BaseLoader`.

- `auto_reload: bool = True` - If `True`, automatically reload a cached template if it has been updated.

- `namespace_key: str = ""` - The name of a global render context variable or loader keyword argument that resolves to the current loader "namespace" or "scope".

- `cache_size: int: 300` - The maximum number of templates to hold in the cache before removing the least recently used template.
