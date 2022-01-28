"""Template loader test cases."""
# pylint: disable=missing-class-docstring
import asyncio
import tempfile
import time
import unittest

from pathlib import Path

from typing import Dict

from liquid import Environment
from liquid import Context
from liquid.template import BoundTemplate
from liquid.template import AwareBoundTemplate

from liquid.loaders import BaseLoader
from liquid.loaders import FileSystemLoader
from liquid.loaders import FileExtensionLoader
from liquid.loaders import ChoiceLoader
from liquid.loaders import DictLoader
from liquid.loaders import TemplateSource

from liquid.exceptions import TemplateNotFound


class FileSystemLoaderTestCase(unittest.TestCase):
    """Test loading templates from the file system."""

    def test_load_template(self):
        """Test that we can load a template from the file system."""
        env = Environment(loader=FileSystemLoader(search_path="tests/fixtures/"))
        template = env.get_template(name="dropify/index.liquid")
        self.assertIsInstance(template, BoundTemplate)

    def test_cached_template(self):
        """Test that templates loaded from the file system get cached."""
        env = Environment(
            loader=FileSystemLoader(search_path="tests/fixtures/"),
            auto_reload=True,
        )
        template = env.get_template(name="dropify/index.liquid")
        self.assertTrue(template.is_up_to_date)

        another = env.get_template(name="dropify/index.liquid")
        self.assertTrue(another.is_up_to_date)

        self.assertEqual(template.tree, another.tree)

    def test_auto_reload_template(self):
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

            self.assertNotEqual(template.tree, updated_template.tree)

    def test_without_auto_reload_template(self):
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

    def test_template_cache_size(self):
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
            self.assertFalse(env.auto_reload)

            # Very small cache size.
            env = Environment(
                loader=FileSystemLoader(search_path=tmpdir),
                cache_size=1,
            )

            template = env.get_template(name=str(template_path))
            self.assertTrue(template.is_up_to_date)

            same_template = env.get_template(name=str(template_path))
            self.assertTrue(template.is_up_to_date)

            # Cached tempalate is the same object
            self.assertEqual(template.tree, same_template.tree)

            # Push the first template out of the cache
            another_template = env.get_template(name=str(another_template_path))
            self.assertTrue(another_template.is_up_to_date)
            self.assertEqual(len(env.cache), 1)

    def test_template_not_found(self):
        """Test that we get an error if the template does not exist."""
        env = Environment(loader=FileSystemLoader(search_path="tests/fixtures/"))
        with self.assertRaises(TemplateNotFound):
            env.get_template(name="dropify/nosuchthing.liquid")

    def test_no_such_search_path(self):
        """Test that a non-existant search path does not cause an error."""
        env = Environment(loader=FileSystemLoader(search_path="nosuchthing/foo/"))
        with self.assertRaises(TemplateNotFound):
            env.get_template(name="dropify/nosuchthing.liquid")

    def test_multiple_search_paths(self):
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
        self.assertIsInstance(template, BoundTemplate)
        self.assertEqual(template.path, Path("tests/fixtures/subfolder/fallback.html"))

    def test_stay_in_search_path(self):
        """Test that we can't stray above the search path"""
        env = Environment(
            loader=FileSystemLoader(search_path="tests/fixtures/subfolder")
        )

        with self.assertRaises(TemplateNotFound):
            _ = env.get_template(name="../dropify/index.liquid")


class TemplateDropTestCase(unittest.TestCase):
    def setUp(self):
        self.env = Environment(
            loader=DictLoader(
                {
                    "somename": "{{ template.name }}",
                    "somedir/somename.liquid": "{{ template.directory }}",
                    "somename.somesuffix.liquid": "{{ template.suffix }}",
                }
            )
        )

        self.env.template_class = AwareBoundTemplate

    def test_template_name(self):
        """Test that templates have access to their name."""
        template = self.env.get_template(name="somename")
        self.assertEqual(template.render(), "somename")

    def test_template_directory(self):
        """Test that templates have access to their directory name."""
        template = self.env.get_template(name="somedir/somename.liquid")
        self.assertEqual(template.render(), "somedir")

    def test_template_suffix(self):
        """Test that templates have access to their suffix."""
        template = self.env.get_template(name="somename.somesuffix.liquid")
        self.assertEqual(template.render(), "somesuffix")

    def test_drop_contains(self):
        """Test that we can check drop membership."""
        template = self.env.get_template(name="somename")
        assert isinstance(template, AwareBoundTemplate)
        self.assertEqual("name" in template.drop, True)
        self.assertEqual("foo" in template.drop, False)

    def test_drop_length(self):
        """Test that we get the length of a template drop"""
        template = self.env.get_template(name="somename")
        assert isinstance(template, AwareBoundTemplate)
        self.assertEqual(len(template.drop), 3)

    def test_iter_drop(self):
        """Test that we can iterate a template drop."""
        template = self.env.get_template(name="somename")
        assert isinstance(template, AwareBoundTemplate)
        keys = list(template.drop)
        self.assertEqual(keys, ["directory", "name", "suffix"])


class MatterDictLoader(DictLoader):
    def __init__(
        self,
        templates: Dict[str, str],
        matter: Dict[str, Dict[str, object]],
    ):
        super().__init__(templates)
        self.matter = matter

    def get_source(self, _: Environment, template_name: str) -> TemplateSource:
        try:
            source = self.templates[template_name]
        except KeyError as err:
            raise TemplateNotFound(template_name) from err

        return TemplateSource(
            source=source,
            filename=template_name,
            uptodate=None,
            matter=self.matter.get(template_name),
        )


class MatterLoaderTestCase(unittest.TestCase):
    def test_matter_loader(self):
        """Test that template loaders can add to render context."""
        loader = MatterDictLoader(
            templates={
                "some": "Hello, {{ you }}{{ username }}!",
                "other": "Goodbye, {{ you }}{{ username }}.",
                "thing": "{{ you }}{{ username }}",
            },
            matter={
                "some": {"you": "World"},
                "other": {"username": "Smith"},
            },
        )

        env = Environment(loader=loader)

        template = env.get_template("some")
        self.assertEqual(template.render(), "Hello, World!")

        template = env.get_template("other")
        self.assertEqual(template.render(), "Goodbye, Smith.")

        template = env.get_template("thing")
        self.assertEqual(template.render(), "")

    def test_matter_global_priority(self):
        """Test that matter variables take priority over globals."""
        loader = MatterDictLoader(
            templates={"some": "Hello, {{ you }}!"},
            matter={"some": {"you": "Liquid"}},
        )

        env = Environment(loader=loader, globals={"you": "World"})
        template = env.get_template("some", globals={"you": "Jinja"})

        self.assertEqual(template.render(), "Hello, Liquid!")

    def test_matter_local_priority(self):
        """Test that render args take priority over matter variables."""
        loader = MatterDictLoader(
            templates={"some": "Hello, {{ you }}!"},
            matter={"some": {"you": "Liquid"}},
        )

        env = Environment(loader=loader)
        template = env.get_template("some")

        self.assertEqual(template.render(you="John"), "Hello, John!")


class ChoiceLoaderTestCase(unittest.TestCase):
    """Test loading templates from a list of loaders."""

    def test_choose_between_loaders(self):
        """Test that we can load templates from a list of loaders."""
        loader = ChoiceLoader(
            loaders=[
                DictLoader({"a": "Hello, {{ you }}!"}),
                DictLoader(
                    {
                        "a": "unreachable",
                        "b": "the quick brown {{ animal | default: 'fox' }}",
                    }
                ),
            ]
        )

        env = Environment(loader=loader)

        template = env.get_template("a")
        self.assertEqual(template.render(you="World"), "Hello, World!")

        template = env.get_template("b")
        self.assertEqual(template.render(), "the quick brown fox")

        with self.assertRaises(TemplateNotFound):
            env.get_template("c")


class FileExtensionLoaderTestCase(unittest.TestCase):
    """Test loading templates from the file system with automatic extensions."""

    def test_load_template_with_missing_extension(self):
        """Test that we can load a template from the file system when a file extension
        is missing."""
        env = Environment(
            loader=FileExtensionLoader(
                search_path="tests/fixtures/",
                ext=".liquid",
            )
        )
        template = env.get_template(name="dropify/index")
        self.assertIsInstance(template, BoundTemplate)

    def test_stay_in_search_path(self):
        """Test that we can't stray above the search path"""
        env = Environment(
            loader=FileExtensionLoader(
                search_path="tests/fixtures/subfolder",
                ext=".liquid",
            )
        )

        with self.assertRaises(TemplateNotFound):
            _ = env.get_template(name="../dropify/index")

    def test_multiple_search_paths(self):
        """Test that we can search multiple directories for templates."""
        env = Environment(
            loader=FileExtensionLoader(
                search_path=[
                    "tests/fixtures/",
                    "tests/fixtures/subfolder/",
                ],
                ext=".liquid",
            )
        )

        template = env.get_template(name="fallback.html")
        self.assertIsInstance(template, BoundTemplate)
        self.assertEqual(template.path, Path("tests/fixtures/subfolder/fallback.html"))

    def test_template_not_found(self):
        """Test that we get an error if the template does not exist."""
        env = Environment(
            loader=FileExtensionLoader(
                search_path="tests/fixtures/",
                ext=".liquid",
            )
        )
        with self.assertRaises(TemplateNotFound):
            env.get_template(name="dropify/nosuchthing")


class BadLoader(BaseLoader):
    pass


class BaseLoaderTestCase(unittest.TestCase):
    """Test case for the abstract base loader."""

    def test_get_source_is_required(self):
        """Test that the `get_source` method is required."""
        env = Environment(loader=BadLoader())

        with self.assertRaises(TemplateNotFound):
            env.get_template(name="somename")


class MockContextLoader(DictLoader):
    def __init__(self, templates: Dict[str, str]):
        self.kwargs = {}
        super().__init__(templates)

    def get_source_with_context(
        self, context: Context, template_name: str, **kwargs: str
    ) -> TemplateSource:
        self.kwargs.update(kwargs)
        self.kwargs["uid"] = context.resolve("uid", default=None)
        return super().get_source(context.env, template_name)

    async def get_source_with_context_async(
        self, context: Context, template_name: str, **kwargs: str
    ) -> TemplateSource:
        self.kwargs.update(kwargs)
        self.kwargs["uid"] = context.resolve("uid", default=None)
        return await super().get_source_async(context.env, template_name)


class ContextLoaderTestCase(unittest.TestCase):
    """Test case for a loader that used context."""

    def test_keyword_arguments(self):
        """Test that keyword arguments passed to `get_template_with_context` are
        available to a context loader."""
        loader = MockContextLoader({"snippet": "hello"})
        env = Environment(loader=loader, cache_size=0)
        template = env.from_string("{% include 'snippet' %}")

        template.render()
        self.assertIn("tag", loader.kwargs)
        self.assertEqual(loader.kwargs["tag"], "include")

        # and async
        loader.kwargs.clear()
        self.assertNotIn("tag", loader.kwargs)

        async def coro():
            return await template.render_async()

        asyncio.run(coro())
        self.assertIn("tag", loader.kwargs)
        self.assertEqual(loader.kwargs["tag"], "include")

    def test_resolve_from_context(self):
        """Test context loaders can resolve render context variables."""
        loader = MockContextLoader({"snippet": "hello"})
        env = Environment(loader=loader, cache_size=0)
        template = env.from_string("{% include 'snippet' %}", globals={"uid": 1234})

        template.render()
        self.assertIn("uid", loader.kwargs)
        self.assertEqual(loader.kwargs["uid"], 1234)

        # and async
        loader.kwargs.clear()
        self.assertNotIn("uid", loader.kwargs)

        async def coro():
            return await template.render_async()

        asyncio.run(coro())
        self.assertIn("uid", loader.kwargs)
        self.assertEqual(loader.kwargs["uid"], 1234)
