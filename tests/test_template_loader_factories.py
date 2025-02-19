from liquid import CachingChoiceLoader
from liquid import CachingFileSystemLoader
from liquid import ChoiceLoader
from liquid import DictLoader
from liquid import FileExtensionLoader
from liquid import FileSystemLoader
from liquid import make_choice_loader
from liquid import make_file_system_loader


def test_make_file_system_loader() -> None:
    """Test that we can make a file system loader."""
    loader = make_file_system_loader("tests/fixtures/", ext="", cache_size=0)
    assert isinstance(loader, FileSystemLoader)


def test_make_file_extension_loader() -> None:
    """Test that we can make a file extension loader."""
    loader = make_file_system_loader("tests/fixtures/", ext=".liquid", cache_size=0)
    assert isinstance(loader, FileExtensionLoader)


def test_make_caching_file_system_loader() -> None:
    """Test that we can make a caching file system loader."""
    loader = make_file_system_loader("tests/fixtures/", ext=".liquid", cache_size=1)
    assert isinstance(loader, CachingFileSystemLoader)


def test_make_choice_loader() -> None:
    """Test that we can make a choice loader."""
    loader = make_choice_loader([DictLoader({})], cache_size=0)
    assert isinstance(loader, ChoiceLoader)


def test_make_caching_choice_loader() -> None:
    """Test that we can make a caching choice loader."""
    loader = make_choice_loader([DictLoader({})], cache_size=1)
    assert isinstance(loader, CachingChoiceLoader)
