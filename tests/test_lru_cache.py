import pytest

from liquid.utils.lru_cache import LRUCache
from liquid.utils.lru_cache import ThreadSafeLRUCache


def test_negative_cache_capacity() -> None:
    with pytest.raises(ValueError, match="cache capacity must be greater than zero"):
        LRUCache(-1)


def test_zero_cache_capacity() -> None:
    with pytest.raises(ValueError, match="cache capacity must be greater than zero"):
        LRUCache(0)


def test_get_item_from_empty_cache() -> None:
    cache = LRUCache[str, int](2)
    with pytest.raises(KeyError):
        cache["foo"]


def test_get_from_empty_cache() -> None:
    cache = LRUCache[str, int](2)
    assert cache.get("foo") is None


def test_get_from_empty_cache_with_default() -> None:
    cache = LRUCache[str, int](2)
    assert cache.get("foo", 42) == 42


def test_set_item() -> None:
    cache = LRUCache[str, int](2)
    cache["foo"] = 47
    assert len(cache) == 1
    assert cache["foo"] == 47


def test_cap() -> None:
    cache = LRUCache[str, int](2)
    cache["foo"] = 47
    assert len(cache) == 1
    assert "foo" in cache
    cache["bar"] = 99
    assert len(cache) == 2
    assert "foo" in cache
    assert "bar" in cache
    cache["baz"] = 88
    assert len(cache) == 2
    assert "bar" in cache
    assert "baz" in cache
    assert "foo" not in cache
    assert cache["bar"] == 99
    assert cache["baz"] == 88


def test_move_to_front() -> None:
    cache = LRUCache[str, int](2)
    cache["foo"] = 47
    assert list(cache.items()) == [("foo", 47)]
    cache["bar"] = 99
    assert list(cache.items()) == [("bar", 99), ("foo", 47)]
    cache["foo"] = 11
    assert list(cache.items()) == [("foo", 11), ("bar", 99)]
    cache["baz"] = 88
    assert list(cache.items()) == [("baz", 88), ("foo", 11)]


def test_delete() -> None:
    cache = LRUCache[str, int](2)
    cache["foo"] = 47
    cache["bar"] = 99
    assert list(cache.items()) == [("bar", 99), ("foo", 47)]
    del cache["bar"]
    assert list(cache.items()) == [("foo", 47)]


def test_contains() -> None:
    cache = LRUCache[str, int](2)
    cache["foo"] = 47
    cache["bar"] = 99
    assert "foo" in cache
    assert "bar" in cache
    del cache["bar"]
    assert "bar" not in cache


def test_keys() -> None:
    cache = LRUCache[str, int](2)
    cache["foo"] = 47
    assert list(cache.keys()) == ["foo"]
    cache["bar"] = 99
    assert list(cache.keys()) == ["bar", "foo"]
    cache["foo"] = 11
    assert list(cache.keys()) == ["foo", "bar"]
    cache["baz"] = 88
    assert list(cache.keys()) == ["baz", "foo"]


def test_values() -> None:
    cache = LRUCache[str, int](2)
    cache["foo"] = 47
    assert list(cache.values()) == [47]
    cache["bar"] = 99
    assert list(cache.values()) == [99, 47]
    cache["foo"] = 11
    assert list(cache.values()) == [11, 99]
    cache["baz"] = 88
    assert list(cache.values()) == [88, 11]


def test_thread_safe_negative_cache_capacity() -> None:
    with pytest.raises(ValueError, match="cache capacity must be greater than zero"):
        ThreadSafeLRUCache(-1)


def test_thread_safe_zero_cache_capacity() -> None:
    with pytest.raises(ValueError, match="cache capacity must be greater than zero"):
        ThreadSafeLRUCache(0)


def test_thread_safe_get_item_from_empty_cache() -> None:
    cache = ThreadSafeLRUCache[str, int](2)
    with pytest.raises(KeyError):
        cache["foo"]


def test_thread_safe_get_from_empty_cache() -> None:
    cache = ThreadSafeLRUCache[str, int](2)
    assert cache.get("foo") is None


def test_thread_safe_get_from_empty_cache_with_default() -> None:
    cache = ThreadSafeLRUCache[str, int](2)
    assert cache.get("foo", 42) == 42


def test_thread_safe_set_item() -> None:
    cache = ThreadSafeLRUCache[str, int](2)
    cache["foo"] = 47
    assert len(cache) == 1
    assert cache["foo"] == 47


def test_thread_safe_cap() -> None:
    cache = ThreadSafeLRUCache[str, int](2)
    cache["foo"] = 47
    assert len(cache) == 1
    assert "foo" in cache
    cache["bar"] = 99
    assert len(cache) == 2
    assert "foo" in cache
    assert "bar" in cache
    cache["baz"] = 88
    assert len(cache) == 2
    assert "bar" in cache
    assert "baz" in cache
    assert "foo" not in cache
    assert cache["bar"] == 99
    assert cache["baz"] == 88


def test_thread_safe_move_to_front() -> None:
    cache = ThreadSafeLRUCache[str, int](2)
    cache["foo"] = 47
    assert list(cache.items()) == [("foo", 47)]
    cache["bar"] = 99
    assert list(cache.items()) == [("bar", 99), ("foo", 47)]
    cache["foo"] = 11
    assert list(cache.items()) == [("foo", 11), ("bar", 99)]
    cache["baz"] = 88
    assert list(cache.items()) == [("baz", 88), ("foo", 11)]


def test_thread_safe_delete() -> None:
    cache = ThreadSafeLRUCache[str, int](2)
    cache["foo"] = 47
    cache["bar"] = 99
    assert list(cache.items()) == [("bar", 99), ("foo", 47)]
    del cache["bar"]
    assert list(cache.items()) == [("foo", 47)]


def test_thread_safe_contains() -> None:
    cache = ThreadSafeLRUCache[str, int](2)
    cache["foo"] = 47
    cache["bar"] = 99
    assert "foo" in cache
    assert "bar" in cache
    del cache["bar"]
    assert "bar" not in cache


def test_thread_safe_keys() -> None:
    cache = ThreadSafeLRUCache[str, int](2)
    cache["foo"] = 47
    assert list(cache.keys()) == ["foo"]
    cache["bar"] = 99
    assert list(cache.keys()) == ["bar", "foo"]
    cache["foo"] = 11
    assert list(cache.keys()) == ["foo", "bar"]
    cache["baz"] = 88
    assert list(cache.keys()) == ["baz", "foo"]


def test_thread_safe_values() -> None:
    cache = ThreadSafeLRUCache[str, int](2)
    cache["foo"] = 47
    assert list(cache.values()) == [47]
    cache["bar"] = 99
    assert list(cache.values()) == [99, 47]
    cache["foo"] = 11
    assert list(cache.values()) == [11, 99]
    cache["baz"] = 88
    assert list(cache.values()) == [88, 11]
