"""Template loader test cases."""

import unittest

from pathlib import Path

from liquid.environment import Environment
from liquid.environment import BoundTemplate
from liquid.template import AwareBoundTemplate

from liquid.loaders import FileSystemLoader, DictLoader
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
        env = Environment(loader=FileSystemLoader(search_path="tests/fixtures/"))
        template = env.get_template(name="dropify/index.liquid")
        self.assertTrue(template.is_up_to_date)

        another = env.get_template(name="dropify/index.liquid")
        self.assertTrue(another.is_up_to_date)

        self.assertEqual(template.tree, another.tree)

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
