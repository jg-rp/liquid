"""Template loader test cases."""
import asyncio
import pickle
import sys
import tempfile
import time
import unittest
from pathlib import Path
from typing import Dict

from mock import patch

from liquid import Context
from liquid import Environment
from liquid.exceptions import TemplateNotFound
from liquid.loaders import BaseLoader
from liquid.loaders import ChoiceLoader
from liquid.loaders import DictLoader
from liquid.loaders import FileExtensionLoader
from liquid.loaders import FileSystemLoader
from liquid.loaders import PackageLoader
from liquid.loaders import TemplateSource
from liquid.template import AwareBoundTemplate
from liquid.template import BoundTemplate


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

            # Cached template is the same object
            self.assertIs(template.tree, same_template.tree)

            # Push the first template out of the cache
            another_template = env.get_template(name=str(another_template_path))
            self.assertTrue(another_template.is_up_to_date)
            self.assertEqual(len(env.cache), 1)

    def test_disable_template_cache(self):
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
            self.assertFalse(env.auto_reload)

            template = env.get_template(name=str(template_path))
            self.assertTrue(template.is_up_to_date)

            same_template = env.get_template(name=str(template_path))
            self.assertTrue(template.is_up_to_date)

            # Cached template is the same object
            self.assertIsNot(template.tree, same_template.tree)

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
        """Test that we can't stray above the search path."""
        env = Environment(
            loader=FileSystemLoader(search_path="tests/fixtures/subfolder")
        )

        with self.assertRaises(TemplateNotFound):
            _ = env.get_template(name="../dropify/index.liquid")

    def test_pickle_loaded_template(self):
        """Test that templates loaded with a file system loader are pickleable."""
        env = Environment(loader=FileSystemLoader(search_path="tests/fixtures/"))
        template = env.get_template(name="dropify/index.liquid")
        pickle.dumps(template)

        async def coro():
            template = await env.get_template_async(name="dropify/index.liquid")
            pickle.dumps(template)

        asyncio.run(coro())


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
        """Test that we get the length of a template drop."""
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
        """Test that we can't stray above the search path."""
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
    """Test case for a loader that references a render context."""

    def test_keyword_arguments(self):
        """Test that keyword arguments passed to `get_template_with_context` are
        available to a context-aware loader."""
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


class MockBootstrapLoader(BaseLoader):
    def __init__(self, namespaces: Dict[str, Dict[str, str]]):
        self.namespaces = namespaces

    def get_source(self, _: Environment, __: str) -> TemplateSource:
        raise TemplateNotFound(
            f"{self.__class__.__name__} requires a namespace argument"
        )

    def get_source_with_args(
        self, _: Environment, template_name: str, **kwargs: object
    ) -> TemplateSource:
        try:
            namespace = kwargs["uid"]
        except KeyError as err:
            raise TemplateNotFound(
                f"{self.__class__.__name__} requires a namespace argument"
            ) from err

        try:
            source = self.namespaces[namespace][template_name]
        except KeyError as err:
            raise TemplateNotFound(f"{namespace}:{template_name}") from err

        return TemplateSource(source, template_name, None)


class BootstrapLoaderTestCase(unittest.TestCase):
    """Test cases for a loader that expects a namespace argument."""

    def setUp(self) -> None:
        loader = MockBootstrapLoader(
            namespaces={
                "abc": {"foo": "hello, {{ you }}", "bar": "g'day, {{ you }}"},
                "def": {"bar": "goodbye, {{ you }}"},
            }
        )
        self.env = Environment(loader=loader)

    def test_no_namespace(self) -> None:
        """Test that we get an exception when no namespace is given."""
        with self.assertRaises(TemplateNotFound):
            self.env.get_template("bar")

        with self.assertRaises(TemplateNotFound):
            self.env.get_template_with_args("bar")

        async def coro():
            return await self.env.get_template_with_args_async("bar")

        with self.assertRaises(TemplateNotFound):
            asyncio.run(coro())

    def test_narrow_with_namespace(self) -> None:
        """Test that we can provide arbitrary arguments to a loader."""
        template = self.env.get_template_with_args("foo", uid="abc")
        self.assertEqual(template.render(you="world"), "hello, world")

        with self.assertRaises(TemplateNotFound):
            # The namespace identified by this uid does not have a "foo" template.
            self.env.get_template_with_args("foo", uid="def")

        template = self.env.get_template_with_args("bar", uid="def")
        self.assertEqual(template.render(you="world"), "goodbye, world")

        async def coro():
            template = await self.env.get_template_with_args_async("bar", uid="abc")
            return await template.render_async(you="world")

        self.assertEqual(asyncio.run(coro()), "g'day, world")

    def test_fallback_to_get_source(self) -> None:
        """Test that we use `get_source()` by default."""
        env = Environment()
        with self.assertRaises(TemplateNotFound):
            env.get_template_with_args("foo")


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

    def test_choose_between_loaders_with_arguments(self):
        """Test that we can choose between loaders that require arguments."""
        loader = ChoiceLoader(
            loaders=[
                MockBootstrapLoader(
                    namespaces={
                        "foo": {
                            "a": "Hello, {{ you }}!",
                            "b": "the quick brown {{ animal | default: 'fox' }}",
                        }
                    }
                ),
                DictLoader({"a": "Goodbye, {{ you }}!"}),
            ]
        )

        env = Environment(loader=loader)

        # Template not found with arguments
        with self.assertRaises(TemplateNotFound):
            env.get_template_with_args("c", uid="foo")

        # Get template 'a' without arguments.
        template = env.get_template("a")
        self.assertEqual(template.render(you="World"), "Goodbye, World!")

        # Get template 'a' with uid argument.
        template = env.get_template_with_args("a", uid="foo")
        self.assertEqual(template.render(you="World"), "Hello, World!")

    def test_choose_between_loaders_with_arguments_async(self):
        """Test that we can choose between async loaders that require arguments."""
        loader = ChoiceLoader(
            loaders=[
                MockBootstrapLoader(
                    namespaces={
                        "foo": {
                            "a": "Hello, {{ you }}!",
                            "b": "the quick brown {{ animal | default: 'fox' }}",
                        }
                    }
                ),
                DictLoader({"a": "Goodbye, {{ you }}!"}),
            ]
        )

        env = Environment(loader=loader)

        # Template not found with arguments
        async def coro():
            await env.get_template_with_args_async("c", uid="foo")

        with self.assertRaises(TemplateNotFound):
            asyncio.run(coro())

        # Get template 'a' without arguments.
        async def coro():
            template = env.get_template("a")
            return template.render(you="World")

        self.assertEqual(asyncio.run(coro()), "Goodbye, World!")

        # Get template 'a' with uid argument.
        async def coro():
            template = env.get_template_with_args("a", uid="foo")
            return template.render(you="World")

        self.assertEqual(asyncio.run(coro()), "Hello, World!")

    def test_choose_between_loaders_with_context(self):
        """Test that we can choose between loaders that make use of a render context."""
        context_loader = MockContextLoader({"a": "Hello, {{ you }}!"})

        loader = ChoiceLoader(
            loaders=[
                DictLoader({"b": "Greetings, {{ you }}!"}),
                context_loader,
                DictLoader({"a": "Goodbye, {{ you }}!"}),
            ]
        )

        env = Environment(loader=loader)

        # No matches.
        with self.assertRaises(TemplateNotFound):
            env.from_string("{% include 'c' %}").render()

        # The mock context loader gets access to the active render context when
        # it's used from an `include` or `render` tag.
        template = env.from_string("{% include 'a' %}", globals={"uid": 1234})
        self.assertEqual(template.render(you="World"), "Hello, World!")
        self.assertIn("tag", context_loader.kwargs)
        self.assertEqual(context_loader.kwargs["tag"], "include")
        self.assertIn("uid", context_loader.kwargs)
        self.assertEqual(context_loader.kwargs["uid"], 1234)

    def test_choose_between_loaders_with_context_async(self):
        """Test that we can choose between async loaders that use render context."""
        context_loader = MockContextLoader({"a": "Hello, {{ you }}!"})

        loader = ChoiceLoader(
            loaders=[
                DictLoader({"b": "Greetings, {{ you }}!"}),
                context_loader,
                DictLoader({"a": "Goodbye, {{ you }}!"}),
            ]
        )

        env = Environment(loader=loader)

        # No matches.
        async def coro():
            template_ = env.from_string("{% include 'c' %}")
            await template_.render_async()

        with self.assertRaises(TemplateNotFound):
            asyncio.run(coro())

        # The mock context loader gets access to the active render context when
        # it's used from an `include` or `render` tag.
        template = env.from_string("{% include 'a' %}", globals={"uid": 1234})

        async def coro():
            return await template.render_async(you="World")

        self.assertEqual(asyncio.run(coro()), "Hello, World!")
        self.assertIn("tag", context_loader.kwargs)
        self.assertEqual(context_loader.kwargs["tag"], "include")
        self.assertIn("uid", context_loader.kwargs)
        self.assertEqual(context_loader.kwargs["uid"], 1234)


class PackageLoaderTestCase(unittest.TestCase):
    """Test loading templates from Python packages."""

    def test_no_such_package(self) -> None:
        """Test that we get an exception at construction time if the
        package doesn't exist."""
        with self.assertRaises(ModuleNotFoundError):
            Environment(loader=PackageLoader("nosuchthing"))

    def test_package_root(self) -> None:
        """Test that we can load templates from a package's root."""
        with patch.object(sys, "path", [str(Path(__file__).parent)] + sys.path):
            loader = PackageLoader("mock_package", package_path="")

        env = Environment(loader=loader)

        with self.assertRaises(TemplateNotFound):
            env.get_template("some")

        template = env.get_template("other")
        self.assertEqual(template.render(you="World"), "g'day, World!\n")

    def test_package_directory(self) -> None:
        """Test that we can load templates from a package directory."""
        with patch.object(sys, "path", [str(Path(__file__).parent)] + sys.path):
            loader = PackageLoader("mock_package", package_path="templates")

        env = Environment(loader=loader)
        template = env.get_template("some")
        self.assertEqual(template.render(you="World"), "Hello, World!\n")

    def test_package_with_list_of_paths(self) -> None:
        """Test that we can load templates from multiple paths in a package."""
        with patch.object(sys, "path", [str(Path(__file__).parent)] + sys.path):
            loader = PackageLoader(
                "mock_package", package_path=["templates", "templates/more_templates"]
            )

        env = Environment(loader=loader)
        template = env.get_template("some.liquid")
        self.assertEqual(template.render(you="World"), "Hello, World!\n")

        template = env.get_template("more_templates/thing.liquid")
        self.assertEqual(template.render(you="World"), "Goodbye, World!\n")

        template = env.get_template("thing.liquid")
        self.assertEqual(template.render(you="World"), "Goodbye, World!\n")

    def test_package_root_async(self) -> None:
        """Test that we can load templates from a package's root asynchronously."""
        with patch.object(sys, "path", [str(Path(__file__).parent)] + sys.path):
            loader = PackageLoader("mock_package", package_path="")

        env = Environment(loader=loader)

        async def coro():
            return await env.get_template_async("other")

        template = asyncio.run(coro())
        self.assertEqual(template.render(you="World"), "g'day, World!\n")

    def test_escape_package_root(self) -> None:
        """Test that we can't escape the package's package's root."""
        with patch.object(sys, "path", [str(Path(__file__).parent)] + sys.path):
            loader = PackageLoader("mock_package", package_path="")

        env = Environment(loader=loader)

        with self.assertRaises(TemplateNotFound):
            env.get_template("../secret.liquid")
