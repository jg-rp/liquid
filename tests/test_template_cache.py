"""Template cache test cases."""
# pylint: disable=missing-class-docstring
import unittest

from liquid.utils import LRUCache


class TemplateCacheTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.cache = LRUCache(capacity=5)
        self.cache["foo"] = "bar"
        self.cache["some"] = "other"

    def test_copy(self):
        """Test that we can copy a cache."""
        copy = self.cache.copy()
        self.assertEqual(self.cache.items(), copy.items())

        copy["some"] = "different"
        self.assertNotEqual(self.cache.items(), copy.items())

    def test_set_default(self):
        """Test that we can set a default value for cache keys."""
        self.cache.setdefault("foo", "baz")
        self.assertEqual(self.cache["foo"], "bar")

        val = self.cache.setdefault("hello", "there")
        self.assertEqual(self.cache["hello"], val)

    def test_clear(self):
        """Test that we can clear all items from the cache."""
        self.assertEqual(len(self.cache), 2)
        self.cache.clear()
        self.assertEqual(len(self.cache), 0)

    def test_contains(self):
        """Test that we can check for membership."""
        self.assertEqual("foo" in self.cache, True)

    def test_delete(self):
        """Test that we can remove items from the cache."""
        self.assertEqual(len(self.cache), 2)
        del self.cache["foo"]
        self.assertEqual("foo" in self.cache, False)
        self.assertEqual(len(self.cache), 1)

    def test_values(self):
        """Test that we can get a list of cache values."""
        self.assertEqual(self.cache.values(), ["other", "bar"])

    def test_keys(self):
        """Test that we can get a list of cache keys."""
        self.assertEqual(self.cache.keys(), ["some", "foo"])

    def test_reversed(self):
        """Test that we can get a list of cache keys, oldest first."""
        self.assertEqual(list(reversed(self.cache)), ["foo", "some"])

    def test_capacity(self):
        """Test that the cache does not exceed capacity."""
        self.cache["a"] = 1
        self.cache["b"] = 2
        self.cache["c"] = 3
        self.assertEqual(len(self.cache), 5)

        self.cache["d"] = 4
        self.assertEqual(len(self.cache), 5)

    def test_priority(self):
        """Test that recently used items are not removed from the cache."""
        self.cache["a"] = 1
        self.cache["b"] = 2
        self.cache["c"] = 3
        self.assertEqual(len(self.cache), 5)

        self.assertEqual("foo" in self.cache, True)
        self.cache["d"] = 4
        self.assertEqual("foo" in self.cache, False)

        self.assertEqual("some" in self.cache, True)
        self.cache["some"] = "updated"
        self.cache["e"] = 5
        self.assertEqual("some" in self.cache, True)
        self.assertEqual("a" in self.cache, False)
