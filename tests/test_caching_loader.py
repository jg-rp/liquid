import asyncio
import tempfile
import time
import unittest
from pathlib import Path

from liquid import BoundTemplate
from liquid import CachingFileSystemLoader
from liquid import Context
from liquid import Environment


class CachingFileSystemLoaderTestCase(unittest.TestCase):
    def test_load_template(self):
        """Test that we can load a template from the file system."""
        env = Environment(loader=CachingFileSystemLoader(search_path="tests/fixtures/"))
        template = env.get_template(name="dropify/index.liquid")
        self.assertIsInstance(template, BoundTemplate)

    def test_load_template_async(self):
        """Test that we can load a template from the file system asynchronously."""
        env = Environment(loader=CachingFileSystemLoader(search_path="tests/fixtures/"))

        async def coro() -> BoundTemplate:
            return await env.get_template_async(name="dropify/index.liquid")

        template = asyncio.run(coro())
        self.assertIsInstance(template, BoundTemplate)

    def test_cached_template(self):
        """Test that templates loaded from the file system get cached."""
        loader = CachingFileSystemLoader(search_path="tests/fixtures/")
        env = Environment(loader=loader)
        self.assertIsNone(env.cache)
        template = env.get_template(name="dropify/index.liquid")
        self.assertTrue(template.is_up_to_date)
        another = env.get_template(name="dropify/index.liquid", globals={"foo": "bar"})
        self.assertTrue(another.is_up_to_date)
        self.assertIs(template.tree, another.tree)
        self.assertEqual(len(loader.cache), 1)

    def test_cached_template_async(self):
        """Test that async loaded templates get cached."""
        loader = CachingFileSystemLoader(search_path="tests/fixtures/")
        env = Environment(loader=loader)
        self.assertIsNone(env.cache)

        async def get_template() -> BoundTemplate:
            return await env.get_template_async(
                name="dropify/index.liquid", globals={"foo": "bar"}
            )

        async def is_up_to_date(template: BoundTemplate) -> bool:
            return await template.is_up_to_date_async()

        template = asyncio.run(get_template())
        self.assertTrue(asyncio.run(is_up_to_date(template)))
        another = asyncio.run(get_template())
        self.assertTrue(asyncio.run(is_up_to_date(another)))
        self.assertIs(template.tree, another.tree)
        self.assertEqual(len(loader.cache), 1)

    def test_auto_reload_template(self):
        """Test templates loaded from the file system are reloaded automatically."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "somefile.txt"

            # Initial template content
            with template_path.open("w", encoding="UTF-8") as fd:
                fd.write("hello there\n")

            env = Environment(loader=CachingFileSystemLoader(search_path=tmpdir))
            self.assertIsNone(env.cache)

            async def get_template() -> BoundTemplate:
                return await env.get_template_async(name=str(template_path))

            async def is_up_to_date(template: BoundTemplate) -> bool:
                return await template.is_up_to_date_async()

            template = asyncio.run(get_template())
            self.assertTrue(asyncio.run(is_up_to_date(template)))

            same_template = asyncio.run(get_template())
            self.assertTrue(asyncio.run(is_up_to_date(template)))
            self.assertIs(template.tree, same_template.tree)

            # Update template content.
            time.sleep(0.01)  # Make sure some time has passed.
            template_path.touch()

            # Template has been updated
            self.assertFalse(asyncio.run(is_up_to_date(template)))
            updated_template = asyncio.run(get_template())
            self.assertTrue(asyncio.run(is_up_to_date(updated_template)))
            self.assertIsNot(template.tree, updated_template.tree)

    def test_auto_reload_template_async(self):
        """Test templates loaded from the file system are reloaded automatically."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "somefile.txt"

            # Initial template content
            with template_path.open("w", encoding="UTF-8") as fd:
                fd.write("hello there\n")

            env = Environment(loader=CachingFileSystemLoader(search_path=tmpdir))
            self.assertIsNone(env.cache)

            template = env.get_template(name=str(template_path))
            self.assertTrue(template.is_up_to_date)

            same_template = env.get_template(name=str(template_path))
            self.assertTrue(template.is_up_to_date)
            self.assertEqual(template.tree, same_template.tree)

            # Update template content.
            time.sleep(0.01)  # Make sure some time has passed.
            template_path.touch()

            # Template has been updated
            self.assertFalse(template.is_up_to_date)
            updated_template = env.get_template(name=str(template_path))
            self.assertTrue(updated_template.is_up_to_date)
            self.assertIsNot(template.tree, updated_template.tree)

    def test_without_auto_reload_template(self):
        """Test that auto_reload can be disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "somefile.txt"

            # Initial template content
            with template_path.open("w", encoding="UTF-8") as fd:
                fd.write("hello there\n")

            env = Environment(
                loader=CachingFileSystemLoader(search_path=tmpdir, auto_reload=False)
            )
            self.assertIsNone(env.cache)

            template = env.get_template(name=str(template_path))
            self.assertTrue(template.is_up_to_date)

            same_template = env.get_template(name=str(template_path))
            self.assertTrue(template.is_up_to_date)
            self.assertEqual(template.tree, same_template.tree)

            # Update template content.
            time.sleep(0.01)  # Make sure some time has passed.
            template_path.touch()

            # Template has been updated
            self.assertFalse(template.is_up_to_date)
            updated_template = env.get_template(name=str(template_path))
            self.assertFalse(updated_template.is_up_to_date)
            self.assertEqual(template.tree, updated_template.tree)

    def test_load_with_args(self):
        """Test that we default to an empty namespace, ignoring extra args."""
        loader = CachingFileSystemLoader(search_path="tests/fixtures/")
        env = Environment(loader=loader)
        self.assertIsNone(env.cache)

        template = env.get_template_with_args(name="dropify/index.liquid", foo="bar")
        self.assertIsInstance(template, BoundTemplate)

        _template = asyncio.run(
            env.get_template_with_args_async(name="dropify/index.liquid", foo="bar")
        )
        self.assertIsInstance(_template, BoundTemplate)
        self.assertIs(_template, template)

    def test_load_from_namespace_with_args(self):
        """Test that we can provide a namespace with args."""
        loader = CachingFileSystemLoader(
            search_path="tests/fixtures/", namespace_key="foo"
        )
        env = Environment(loader=loader)
        self.assertIsNone(env.cache)

        template = env.get_template_with_args(name="dropify/index.liquid")
        self.assertIsInstance(template, BoundTemplate)

        _template = asyncio.run(
            env.get_template_with_args_async(
                name="dropify/index.liquid", foo="namespace"
            )
        )
        self.assertIsInstance(_template, BoundTemplate)
        self.assertIsNot(_template, template)
        self.assertEqual(_template.render(), "namespaced template")

    def test_load_with_context(self):
        """Test that we can load a cached template referencing a render context."""
        loader = CachingFileSystemLoader(
            search_path="tests/fixtures/", namespace_key="foo"
        )
        env = Environment(loader=loader)
        self.assertIsNone(env.cache)
        context = Context(env=env, globals={"foo": "namespace"})
        template = env.get_template_with_context(context, "dropify/index.liquid")
        self.assertEqual(template.render(), "namespaced template")

    def test_load_with_context_async(self):
        """Test that we can load a cached template referencing a render context."""
        loader = CachingFileSystemLoader(
            search_path="tests/fixtures/", namespace_key="foo"
        )
        env = Environment(loader=loader)
        self.assertIsNone(env.cache)
        context = Context(env=env, globals={"foo": "namespace"})

        async def coro() -> BoundTemplate:
            return await env.get_template_with_context_async(
                context, "dropify/index.liquid"
            )

        self.assertEqual(asyncio.run(coro()).render(), "namespaced template")

    def test_load_with_context_no_namespace(self):
        """Test that we can load a cached template referencing a render context."""
        loader = CachingFileSystemLoader(search_path="tests/fixtures/")
        env = Environment(loader=loader)
        self.assertIsNone(env.cache)
        context = Context(env=env, globals={"foo": "namespace"})
        template = env.get_template_with_context(context, "dropify/index.liquid")
        self.assertNotEqual(template.render(), "namespaced template")

    def test_load_with_context_missing_namespace(self):
        """Test that we fall back to an unscoped template name."""
        loader = CachingFileSystemLoader(
            search_path="tests/fixtures/", namespace_key="foo"
        )
        env = Environment(loader=loader)
        self.assertIsNone(env.cache)
        context = Context(env=env)
        template = env.get_template_with_context(context, "dropify/index.liquid")
        self.assertNotEqual(template.render(), "namespaced template")
