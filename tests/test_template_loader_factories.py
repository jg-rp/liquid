"""Template loader factory test cases."""
import unittest

from liquid.loaders import CachingChoiceLoader
from liquid.loaders import CachingFileSystemLoader
from liquid.loaders import ChoiceLoader
from liquid.loaders import DictLoader
from liquid.loaders import FileExtensionLoader
from liquid.loaders import FileSystemLoader
from liquid.loaders import make_choice_loader
from liquid.loaders import make_file_system_loader


class TemplateLoaderFactoryTestCase(unittest.TestCase):
    """Template loader factory test cases."""

    def test_make_file_system_loader(self):
        """Test that we can make a file system loader."""
        loader = make_file_system_loader("tests/fixtures/", ext="", cache_size=0)
        self.assertIsInstance(loader, FileSystemLoader)

    def test_make_file_extension_loader(self):
        """Test that we can make a file extension loader."""
        loader = make_file_system_loader("tests/fixtures/", ext=".liquid", cache_size=0)
        self.assertIsInstance(loader, FileExtensionLoader)

    def test_make_caching_file_system_loader(self):
        """Test that we can make a caching file system loader."""
        loader = make_file_system_loader("tests/fixtures/", ext=".liquid", cache_size=1)
        self.assertIsInstance(loader, CachingFileSystemLoader)

    def test_make_choice_loader(self):
        """Test that we can make a choice loader."""
        loader = make_choice_loader([DictLoader({})], cache_size=0)
        self.assertIsInstance(loader, ChoiceLoader)

    def test_make_caching_choice_loader(self):
        """Test that we can make a caching choice loader."""
        loader = make_choice_loader([DictLoader({})], cache_size=1)
        self.assertIsInstance(loader, CachingChoiceLoader)
