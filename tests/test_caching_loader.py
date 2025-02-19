import asyncio
import tempfile
import time
from pathlib import Path

import pytest

from liquid import BoundTemplate
from liquid import CachingChoiceLoader
from liquid import CachingFileSystemLoader
from liquid import Context
from liquid import DictLoader
from liquid import Environment
from liquid.exceptions import CacheCapacityValueError


def test_load_template() -> None:
    """Test that we can load a template from the file system."""
    env = Environment(
        loader=CachingFileSystemLoader(search_path="tests/fixtures/001/templates/")
    )
    template = env.get_template(name="index.liquid")
    assert isinstance(template, BoundTemplate)


def test_load_template_async() -> None:
    """Test that we can load a template from the file system asynchronously."""
    env = Environment(
        loader=CachingFileSystemLoader(search_path="tests/fixtures/001/templates/")
    )

    async def coro() -> BoundTemplate:
        return await env.get_template_async(name="index.liquid")

    template = asyncio.run(coro())
    assert isinstance(template, BoundTemplate)


def test_cached_template() -> None:
    """Test that templates loaded from the file system get cached."""
    loader = CachingFileSystemLoader(search_path="tests/fixtures/001/templates/")
    env = Environment(loader=loader)
    assert env.cache is None
    template = env.get_template(name="index.liquid")
    assert template.is_up_to_date is True
    another = env.get_template(name="index.liquid", globals={"foo": "bar"})
    assert another.is_up_to_date is True
    assert template.tree is another.tree
    assert len(loader.cache) == 1


def test_cached_template_async() -> None:
    """Test that async loaded templates get cached."""
    loader = CachingFileSystemLoader(search_path="tests/fixtures/001/templates/")
    env = Environment(loader=loader)
    assert env.cache is None

    async def get_template() -> BoundTemplate:
        return await env.get_template_async(name="index.liquid", globals={"foo": "bar"})

    async def is_up_to_date(template: BoundTemplate) -> bool:
        return await template.is_up_to_date_async()

    template = asyncio.run(get_template())
    assert asyncio.run(is_up_to_date(template)) is True
    another = asyncio.run(get_template())
    assert asyncio.run(is_up_to_date(another)) is True
    assert template.tree is another.tree
    assert len(loader.cache) == 1


def test_auto_reload_template() -> None:
    """Test templates loaded from the file system are reloaded automatically."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_path = Path(tmpdir) / "somefile.txt"

        # Initial template content
        with template_path.open("w", encoding="UTF-8") as fd:
            fd.write("hello there\n")

        env = Environment(loader=CachingFileSystemLoader(search_path=tmpdir))
        assert env.cache is None

        async def get_template() -> BoundTemplate:
            return await env.get_template_async(name=str(template_path))

        async def is_up_to_date(template: BoundTemplate) -> bool:
            return await template.is_up_to_date_async()

        template = asyncio.run(get_template())
        assert asyncio.run(is_up_to_date(template)) is True

        same_template = asyncio.run(get_template())
        assert asyncio.run(is_up_to_date(template)) is True
        assert template.tree is same_template.tree

        # Update template content.
        time.sleep(0.01)  # Make sure some time has passed.
        template_path.touch()

        # Template has been updated
        assert asyncio.run(is_up_to_date(template)) is False
        updated_template = asyncio.run(get_template())
        assert asyncio.run(is_up_to_date(updated_template)) is True
        assert template.tree is not updated_template.tree


def test_auto_reload_template_async() -> None:
    """Test templates loaded from the file system are reloaded automatically."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_path = Path(tmpdir) / "somefile.txt"

        # Initial template content
        with template_path.open("w", encoding="UTF-8") as fd:
            fd.write("hello there\n")

        env = Environment(loader=CachingFileSystemLoader(search_path=tmpdir))
        assert env.cache is None

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
        assert template.tree is not updated_template.tree


def test_without_auto_reload_template() -> None:
    """Test that auto_reload can be disabled."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_path = Path(tmpdir) / "somefile.txt"

        # Initial template content
        with template_path.open("w", encoding="UTF-8") as fd:
            fd.write("hello there\n")

        env = Environment(
            loader=CachingFileSystemLoader(search_path=tmpdir, auto_reload=False)
        )
        assert env.cache is None

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
        assert template.tree is updated_template.tree


def test_load_with_args() -> None:
    """Test that we default to an empty namespace, ignoring extra args."""
    loader = CachingFileSystemLoader(search_path="tests/fixtures/001/templates/")
    env = Environment(loader=loader)
    assert env.cache is None

    template = env.get_template_with_args(name="index.liquid", foo="bar")
    assert isinstance(template, BoundTemplate)

    _template = asyncio.run(
        env.get_template_with_args_async(name="index.liquid", foo="bar")
    )
    assert isinstance(_template, BoundTemplate)
    assert _template == template


def test_load_from_namespace_with_args() -> None:
    """Test that we can provide a namespace with args."""
    loader = CachingFileSystemLoader(
        search_path="tests/fixtures/001/templates/", namespace_key="foo"
    )
    env = Environment(loader=loader)
    assert env.cache is None

    template = env.get_template_with_args(name="index.liquid")
    assert isinstance(template, BoundTemplate)

    _template = asyncio.run(
        env.get_template_with_args_async(name="index.liquid", foo="namespace")
    )
    assert isinstance(_template, BoundTemplate)
    assert _template is not template
    assert _template.render() == "namespaced template"


def test_load_with_context() -> None:
    """Test that we can load a cached template referencing a render context."""
    loader = CachingFileSystemLoader(
        search_path="tests/fixtures/001/templates/", namespace_key="foo"
    )
    env = Environment(loader=loader)
    assert env.cache is None
    context = Context(env=env, globals={"foo": "namespace"})
    template = env.get_template_with_context(context, "index.liquid")
    assert template.render() == "namespaced template"


def test_load_with_context_async() -> None:
    """Test that we can load a cached template referencing a render context."""
    loader = CachingFileSystemLoader(
        search_path="tests/fixtures/001/templates/", namespace_key="foo"
    )
    env = Environment(loader=loader)
    assert env.cache is None
    context = Context(env=env, globals={"foo": "namespace"})

    async def coro() -> BoundTemplate:
        return await env.get_template_with_context_async(context, "index.liquid")

    assert asyncio.run(coro()).render() == "namespaced template"


def test_load_with_context_no_namespace() -> None:
    """Test that we can load a cached template referencing a render context."""
    loader = CachingFileSystemLoader(search_path="tests/fixtures/001/templates/")
    env = Environment(loader=loader)
    assert env.cache is None
    context = Context(env=env, globals={"foo": "namespace"})
    template = env.get_template_with_context(context, "index.liquid")
    assert template.render() != "namespaced template"


def test_load_with_context_missing_namespace() -> None:
    """Test that we fall back to an unscoped template name."""
    loader = CachingFileSystemLoader(
        search_path="tests/fixtures/001/templates/", namespace_key="foo"
    )
    env = Environment(loader=loader)
    assert env.cache is None
    context = Context(env=env)
    template = env.get_template_with_context(context, "index.liquid")
    assert template.render() != "namespaced template"


def test_zero_capacity_cache() -> None:
    """Test that we get an exception when cache size is zero."""
    with pytest.raises(CacheCapacityValueError):
        CachingFileSystemLoader("tests/fixtures/", cache_size=0)


def test_negative_capacity_cache() -> None:
    """Test that we get an exception when cache size is negative."""
    with pytest.raises(CacheCapacityValueError):
        CachingFileSystemLoader("tests/fixtures/", cache_size=-1)


def test_caching_choice_loader() -> None:
    """Simple choice loader from two dictionaries."""
    loader = CachingChoiceLoader(
        [
            DictLoader({"a": "Hello, {{ you }}!"}),
            DictLoader(
                {
                    "a": "Goodbye, {{ you }}!",
                    "b": "g'day, {{ you }}!",
                }
            ),
        ]
    )

    env = Environment(loader=loader)

    # The environment-wide cache should be disabled.
    assert env.cache is None

    # The template cache should start empty
    assert len(loader.cache) == 0

    assert env.get_template("a").render(you="World") == "Hello, World!"
    assert len(loader.cache) == 1
    assert env.get_template("b").render(you="World") == "g'day, World!"
    assert len(loader.cache) == 2  # noqa: PLR2004

    # Clear the cache
    loader.cache.clear()

    assert len(loader.cache) == 0
    template = env.get_template("a")
    assert len(loader.cache) == 1
    same_template = env.get_template("a")
    assert len(loader.cache) == 1
    assert template is same_template
