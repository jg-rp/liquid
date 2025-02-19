import asyncio
import pickle
import tempfile
import time
from pathlib import Path

import pytest

from liquid import BoundTemplate
from liquid import Environment
from liquid import FileSystemLoader
from liquid.exceptions import TemplateNotFound


def test_load_template() -> None:
    """Test that we can load a template from the file system."""
    env = Environment(
        loader=FileSystemLoader(search_path="tests/fixtures/001/templates/")
    )
    template = env.get_template(name="index.liquid")
    assert isinstance(template, BoundTemplate)


def test_cached_template() -> None:
    """Test that templates loaded from the file system get cached."""
    env = Environment(
        loader=FileSystemLoader(search_path="tests/fixtures/001/templates/"),
        auto_reload=True,
    )
    template = env.get_template(name="index.liquid")
    assert template.is_up_to_date is True

    another = env.get_template(name="index.liquid")
    assert another.is_up_to_date is True

    assert template.tree == another.tree


def test_auto_reload_template() -> None:
    """Test templates loaded from the file system are reloaded automatically."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_path = Path(tmpdir) / "somefile.txt"

        # Initial template content
        with template_path.open("w", encoding="UTF-8") as fd:
            fd.write("hello there\n")

        env = Environment(
            loader=FileSystemLoader(search_path=tmpdir),
            auto_reload=True,
        )

        template = env.get_template(name=str(template_path))
        assert template.is_up_to_date is True

        same_template = env.get_template(name=str(template_path))
        assert template.is_up_to_date is True

        assert template.tree == same_template.tree

        # Update template content.
        time.sleep(0.01)  # Make sure some time has passed.
        template_path.touch()

        # Template has been updated
        assert template.is_up_to_date is False

        updated_template = env.get_template(name=str(template_path))  # type: ignore
        assert updated_template.is_up_to_date is True

        assert template.tree != updated_template.tree


def test_without_auto_reload_template() -> None:
    """Test that auto_reload can be disabled."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_path = Path(tmpdir) / "somefile.txt"

        # Initial template content
        with template_path.open("w", encoding="UTF-8") as fd:
            fd.write("hello there\n")

        env = Environment(
            loader=FileSystemLoader(search_path=tmpdir),
            auto_reload=False,
        )

        template = env.get_template(name=str(template_path))
        assert template.is_up_to_date is True

        same_template = env.get_template(name=str(template_path))
        assert template.is_up_to_date is True

        assert template.tree == same_template.tree

        # Update template content.
        time.sleep(0.01)  # Make sure some time has passed.
        template_path.touch()

        # Template has been updated
        assert template.is_up_to_date is False

        updated_template = env.get_template(name=str(template_path))  # type: ignore
        assert updated_template.is_up_to_date is False

        assert template.tree == updated_template.tree


def test_template_cache_size() -> None:
    """Test that we can control the template cache size."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_path = Path(tmpdir) / "somefile.txt"
        another_template_path = Path(tmpdir) / "otherfile.txt"

        # Initial template content
        with template_path.open("w", encoding="UTF-8") as fd:
            fd.write("hello there\n")

        with another_template_path.open("w", encoding="UTF-8") as fd:
            fd.write("goodbye there\n")

        # Cache size of zero sets auto_reload to False
        env = Environment(
            loader=FileSystemLoader(search_path=tmpdir),
            cache_size=0,
        )
        assert env.auto_reload is False

        # Very small cache size.
        env = Environment(
            loader=FileSystemLoader(search_path=tmpdir),
            cache_size=1,
        )

        template = env.get_template(name=str(template_path))
        assert template.is_up_to_date is True

        same_template = env.get_template(name=str(template_path))
        assert template.is_up_to_date is True

        # Cached template is the same object
        assert template.tree is same_template.tree

        # Push the first template out of the cache
        another_template = env.get_template(name=str(another_template_path))
        assert another_template.is_up_to_date is True
        assert env.cache is not None
        assert len(env.cache) == 1


def test_disable_template_cache() -> None:
    """Test that we can disable the template cache."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_path = Path(tmpdir) / "somefile.txt"

        # Initial template content
        with template_path.open("w", encoding="UTF-8") as fd:
            fd.write("hello there\n")

        # Cache size of zero sets auto_reload to False
        env = Environment(
            loader=FileSystemLoader(search_path=tmpdir),
            cache_size=0,
        )
        assert env.auto_reload is False

        template = env.get_template(name=str(template_path))
        assert template.is_up_to_date is True

        same_template = env.get_template(name=str(template_path))
        assert template.is_up_to_date is True

        # Cached template is the same object
        assert template.tree is not same_template.tree


def test_template_not_found() -> None:
    """Test that we get an error if the template does not exist."""
    env = Environment(
        loader=FileSystemLoader(search_path="tests/fixtures/001/templates")
    )
    with pytest.raises(TemplateNotFound):
        env.get_template(name="nosuchthing.liquid")


def test_no_such_search_path() -> None:
    """Test that a non-existant search path does not cause an error."""
    env = Environment(loader=FileSystemLoader(search_path="nosuchthing/foo/"))
    with pytest.raises(TemplateNotFound):
        env.get_template(name="nosuchthing.liquid")


def test_multiple_search_paths() -> None:
    """Test that we can search multiple directories for templates."""
    env = Environment(
        loader=FileSystemLoader(
            search_path=[
                "tests/fixtures/",
                "tests/fixtures/subfolder/",
            ]
        )
    )

    template = env.get_template(name="fallback.html")
    assert isinstance(template, BoundTemplate)
    assert template.path == Path("tests/fixtures/subfolder/fallback.html")


def test_stay_in_search_path() -> None:
    """Test that we can't stray above the search path."""
    env = Environment(loader=FileSystemLoader(search_path="tests/fixtures/subfolder"))

    with pytest.raises(TemplateNotFound):
        env.get_template(name="../001/templates/index.liquid")


def test_pickle_loaded_template() -> None:
    """Test that templates loaded with a file system loader are pickleable."""
    env = Environment(
        loader=FileSystemLoader(search_path="tests/fixtures/001/templates/")
    )
    template = env.get_template(name="index.liquid")
    pickle.dumps(template)

    async def coro() -> None:
        template = await env.get_template_async(name="index.liquid")
        pickle.dumps(template)

    asyncio.run(coro())
