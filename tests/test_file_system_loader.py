import asyncio
import tempfile
import time
from pathlib import Path

import pytest

from liquid import BoundTemplate
from liquid import CachingFileSystemLoader
from liquid import Environment
from liquid import FileSystemLoader
from liquid.exceptions import TemplateNotFound


def test_load_template() -> None:
    env = Environment(loader=FileSystemLoader("tests/fixtures/001/templates/"))
    template = env.get_template("index.liquid")
    assert isinstance(template, BoundTemplate)
    assert template.name == "index.liquid"
    assert (
        str(template.path).replace("\\", "/")
        == "tests/fixtures/001/templates/index.liquid"
    )


def test_load_template_async() -> None:
    env = Environment(loader=FileSystemLoader("tests/fixtures/001/templates/"))

    async def coro() -> BoundTemplate:
        return await env.get_template_async("index.liquid")

    template = asyncio.run(coro())
    assert isinstance(template, BoundTemplate)
    assert template.name == "index.liquid"
    assert (
        str(template.path).replace("\\", "/")
        == "tests/fixtures/001/templates/index.liquid"
    )


def test_template_not_found() -> None:
    env = Environment(loader=FileSystemLoader("tests/fixtures/001/templates/"))
    with pytest.raises(TemplateNotFound):
        env.get_template("nosuchthing.liquid")


def test_template_not_found_async() -> None:
    env = Environment(loader=FileSystemLoader("tests/fixtures/001/templates/"))

    async def coro() -> BoundTemplate:
        return await env.get_template_async("nosuchthing.liquid")

    with pytest.raises(TemplateNotFound):
        asyncio.run(coro())


def test_no_such_search_path() -> None:
    env = Environment(loader=FileSystemLoader("no/such/thing/"))
    with pytest.raises(TemplateNotFound):
        env.get_template("index.liquid")


def test_list_of_search_paths() -> None:
    env = Environment(
        loader=FileSystemLoader(
            [
                "tests/fixtures/001/templates/",
                "tests/fixtures/001/snippets",
            ]
        )
    )

    template = env.get_template("index.liquid")
    assert isinstance(template, BoundTemplate)
    assert template.name == "index.liquid"
    assert (
        str(template.path).replace("\\", "/")
        == "tests/fixtures/001/templates/index.liquid"
    )

    template = env.get_template("featured_content.html")
    assert isinstance(template, BoundTemplate)
    assert template.name == "featured_content.html"
    assert (
        str(template.path).replace("\\", "/")
        == "tests/fixtures/001/snippets/featured_content.html"
    )


def test_default_file_extension() -> None:
    env = Environment(loader=FileSystemLoader("tests/fixtures/001/templates/"))
    template = env.get_template("index.liquid")
    assert isinstance(template, BoundTemplate)
    assert template.name == "index.liquid"
    assert (
        str(template.path).replace("\\", "/")
        == "tests/fixtures/001/templates/index.liquid"
    )

    with pytest.raises(TemplateNotFound):
        env.get_template("main")


def test_set_default_file_extension() -> None:
    env = Environment(
        loader=FileSystemLoader("tests/fixtures/001/templates/", ext=".liquid")
    )
    template = env.get_template("index.liquid")
    assert isinstance(template, BoundTemplate)
    assert template.name == "index.liquid"
    assert (
        str(template.path).replace("\\", "/")
        == "tests/fixtures/001/templates/index.liquid"
    )

    template = env.get_template("index")
    assert isinstance(template, BoundTemplate)
    assert template.name == "index.liquid"
    assert (
        str(template.path).replace("\\", "/")
        == "tests/fixtures/001/templates/index.liquid"
    )


def test_stay_in_search_path() -> None:
    env = Environment(loader=FileSystemLoader("tests/fixtures/001/templates/snippets"))
    with pytest.raises(TemplateNotFound):
        env.get_template("../index.liquid")


def test_dont_cache_templates() -> None:
    env = Environment(loader=FileSystemLoader("tests/fixtures/001/templates/"))
    template = env.get_template("index.liquid")
    assert isinstance(template, BoundTemplate)
    assert template.name == "index.liquid"
    assert (
        str(template.path).replace("\\", "/")
        == "tests/fixtures/001/templates/index.liquid"
    )
    assert template.is_up_to_date() is True

    another_template = env.get_template("index.liquid")
    assert template is not another_template


def test_cache_templates() -> None:
    env = Environment(loader=CachingFileSystemLoader("tests/fixtures/001/templates/"))
    template = env.get_template("index.liquid")
    assert isinstance(template, BoundTemplate)
    assert template.name == "index.liquid"
    assert (
        str(template.path).replace("\\", "/")
        == "tests/fixtures/001/templates/index.liquid"
    )
    assert template.is_up_to_date() is True

    another_template = env.get_template("index.liquid")
    assert template is another_template


def test_auto_reload_cached_templates() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "some.txt"

        # Write some content to temporary file
        with path.open("w", encoding="UTF-8") as fd:
            fd.write("Hello, {{ you }}!")

        env = Environment(loader=CachingFileSystemLoader(tmp))
        template = env.get_template("some.txt")
        assert template.is_up_to_date()

        same_template = env.get_template("some.txt")
        assert same_template.is_up_to_date()
        assert same_template is template

        # Update template source
        time.sleep(0.01)
        path.touch()

        assert template.is_up_to_date() is False
        updated_template = env.get_template("some.txt")
        assert updated_template is not template


def test_auto_reload_cached_templates_async() -> None:
    async def coro() -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "some.txt"

            # Write some content to temporary file
            with path.open("w", encoding="UTF-8") as fd:
                fd.write("Hello, {{ you }}!")

            env = Environment(loader=CachingFileSystemLoader(tmp))
            template = await env.get_template_async("some.txt")
            assert await template.is_up_to_date_async()

            same_template = await env.get_template_async("some.txt")
            assert await same_template.is_up_to_date_async()
            assert same_template is template

            # Update template source
            time.sleep(0.01)
            path.touch()

            assert await template.is_up_to_date_async() is False
            updated_template = await env.get_template_async("some.txt")
            assert updated_template is not template

    asyncio.run(coro())


def test_dont_auto_reload_cached_templates() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "some.txt"

        # Write some content to temporary file
        with path.open("w", encoding="UTF-8") as fd:
            fd.write("Hello, {{ you }}!")

        env = Environment(loader=CachingFileSystemLoader(tmp, auto_reload=False))
        template = env.get_template("some.txt")
        assert template.is_up_to_date()

        same_template = env.get_template("some.txt")
        assert same_template.is_up_to_date()
        assert same_template is template

        # Update template source
        time.sleep(0.01)
        path.touch()

        assert template.is_up_to_date() is False
        updated_template = env.get_template("some.txt")
        assert updated_template is template


def test_dont_auto_reload_cached_templates_async() -> None:
    async def coro() -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "some.txt"

            # Write some content to temporary file
            with path.open("w", encoding="UTF-8") as fd:
                fd.write("Hello, {{ you }}!")

            env = Environment(loader=CachingFileSystemLoader(tmp, auto_reload=False))
            template = await env.get_template_async("some.txt")
            assert await template.is_up_to_date_async()

            same_template = await env.get_template_async("some.txt")
            assert await same_template.is_up_to_date_async()
            assert same_template is template

            # Update template source
            time.sleep(0.01)
            path.touch()

            assert await template.is_up_to_date_async() is False
            updated_template = await env.get_template_async("some.txt")
            assert updated_template is template

    asyncio.run(coro())


def test_cache_capacity() -> None:
    loader = CachingFileSystemLoader("tests/fixtures/001/templates/", capacity=2)
    env = Environment(loader=loader)
    assert len(loader.cache) == 0
    _template = env.get_template("index.liquid")
    assert len(loader.cache) == 1
    _template = env.get_template("index.liquid")
    assert len(loader.cache) == 1
    _template = env.get_template("header.liquid")
    assert len(loader.cache) == 2
    assert list(loader.cache.keys()) == ["header.liquid", "index.liquid"]
    _template = env.get_template("footer.liquid")
    assert len(loader.cache) == 2
    assert list(loader.cache.keys()) == ["footer.liquid", "header.liquid"]
