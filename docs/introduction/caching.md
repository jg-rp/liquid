# Caching

## Template Caching

An in-memory template cache is included with every [`Environment`](../api/environment.md). Templates parsed with [`Environment.get_template()`](../api/environment.md#get_template), the [`{% render %}`](../language/tags.md#render) tag or the [`{% include %}`](../language/tags.md#include) tag are stored so as to avoid parsing them multiple times unnecessarily, should that same template be needed again. Templates parsed using [`Environment.from_string()`](../api/environment.md#from_string) are never cached.

The default cache size is `300` (that's 300 templates). You can control the cache capacity with the `cache_size` argument to [`Environment`](../api/environment.md) or [`Template`](../api/template.md). Setting `cache_size` to `0` disables template caching altogether.

```python
from liquid import Environment
env = Environment(cache_size=800)
```

Using an [LRU](<https://en.wikipedia.org/wiki/Cache_replacement_policies#Least_recently_used_(LRU)>) policy, the default cache is most effective in situations where the same template is [rendered](../language/tags.md#render) or [included](../language/tags.md#include) multiple times in a short space of time, or when most of your templates fit in the cache.

## Expression Caching

**_New in version 1.1.0_**

Expression caching is useful in situations where the same Liquid expression appears multiple times in one or more templates. Depending on the nature of your templates, expression caching can significantly improve template parsing performance.

Expression caching is disabled by default. Enable it with the `expression_cache_size` argument to [`Environment`](../api/environment.md) or [`Template`](../api/template.md).

```python
from liquid import Environment
env = Environment(expression_cache_size=80)
```

An [`Environment`](../api/environment.md) will manage one cache for each of the common, built-in expression types, _filtered_, _boolean_ and _loop_ expressions. Each uses an [lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache) from Python's [functools](https://docs.python.org/3/library/functools.html#module-functools) module. You can inspect cache _hits_, _misses_ and _currsize_ for each using the `cache_info()` function of `Environment.parse_filtered_expression_value`, `Environment.parse_boolean_expression_value` and `Environment.parse_loop_expression_value`.

Tests with the [benchmark fixtures](https://github.com/jg-rp/liquid/tree/main/tests/fixtures) show that extra memory used from caching expressions is offset by the reduced size of the resulting syntax trees.

## Caching Template Loaders

**_New in version 1.9.0_**

An [`Environment`](../api/environment.md) template cache does not work well with [context aware loaders](../guides/custom-loaders.md#loading-with-context), because the environment has no way of knowing what context variables might be used to build a cache key. For this reason it is recommended to use [`CachingFileSystemLoader`](../api/cachingfilesystemloader.md) which, by default, replaces the environment cache.

:::info
With hindsight, considering how typical Liquid use cases differ from "traditional" template engine usage, we should never have provided an environment-wide template cache. Come Liquid version 2.0 (unreleased), all template caching will be handled by template loaders.
:::

See [Caching File System Loader](../introduction/loading-templates.md#caching-file-system-loader) for example usage.
