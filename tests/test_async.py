"""Test Python Liquid's async API."""
import asyncio
import tempfile
import time
import unittest

from collections import abc
from pathlib import Path
from typing import NamedTuple

# assert_awaited* were new in Python 3.8, so we're using the backport.
from mock import patch

from liquid import Template
from liquid import Environment
from liquid import FileSystemLoader

from liquid.template import BoundTemplate


class Case(NamedTuple):
    """Table driven test helper."""

    description: str
    template: str
    context: dict
    expect: str
    template_name: str
    calls: int


class LoadAsyncTestCase(unittest.TestCase):
    """Test that we can load templates asynchronously."""

    def test_basic_async(self):
        """Test that we can render a template asynchronously."""
        template = Template("{% for x in (1..3) %}{{x}}-{% endfor %}")

        async def coro():
            return await template.render_async()

        result = asyncio.run(coro())
        self.assertEqual(result, "1-2-3-")

    def test_load_template_async(self):
        """Test that we can load a template asynchronously."""
        env = Environment(loader=FileSystemLoader("tests/fixtures/dropify/"))

        async def coro():
            return await env.get_template_async("index.liquid")

        template = asyncio.run(coro())
        self.assertIsInstance(template, BoundTemplate)

    def test_cached_template_async(self):
        """Test that async loaded templates are cached."""
        env = Environment(loader=FileSystemLoader("tests/fixtures/dropify/"))

        async def coro():
            return await env.get_template_async("index.liquid")

        with patch(
            "liquid.loaders.FileSystemLoader.get_source_async", autospec=True
        ) as source:
            source.side_effect = [
                (
                    r"hello {{ you }}",
                    "some_template",
                    None,
                )
            ]
            template = asyncio.run(coro())
            self.assertIsInstance(template, BoundTemplate)
            source.assert_awaited_once()

            # Get the same template again.
            template = asyncio.run(coro())
            self.assertIsInstance(template, BoundTemplate)
            self.assertEqual(source.call_count, 1)

    def test_async_up_to_date(self):
        """Test that async uptodate functions are awaited."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "some.liquid"

            # Initial template content
            with template_path.open("w") as fd:
                fd.write("hello there\n")

            env = Environment(
                loader=FileSystemLoader(search_path=tmpdir),
                auto_reload=True,
            )

            async def coro():
                return await env.get_template_async("some.liquid")

            template = asyncio.run(coro())
            self.assertIsInstance(template, BoundTemplate)
            uptodate = asyncio.run(template.is_up_to_date_async())
            self.assertTrue(uptodate)

            # Update template content.
            time.sleep(0.01)  # Make sure some time has passed.
            template_path.touch()

            # Template is not up to date.
            uptodate = asyncio.run(template.is_up_to_date_async())
            self.assertFalse(uptodate)

            template = asyncio.run(coro())
            self.assertIsInstance(template, BoundTemplate)
            # Template is up to date.
            uptodate = asyncio.run(template.is_up_to_date_async())
            self.assertTrue(uptodate)

    def test_nested_include_async(self):
        """Test that nested includes are rendered asynchronously."""

        async def coro(template):
            return await template.render_async()

        with patch(
            "liquid.loaders.DictLoader.get_source_async", autospec=True
        ) as source:
            source.side_effect = [
                (
                    "{% include 'bar' %}",
                    "bar",
                    None,
                ),
                (
                    "{% for x in (1..3) %}{{x}}-{% endfor %}",
                    "foo",
                    None,
                ),
            ]

            env = Environment()
            template = env.from_string("{% include 'foo' %}")

            result = asyncio.run(coro(template))

            source.assert_awaited()
            self.assertEqual(source.await_count, 2)
            self.assertEqual(result, "1-2-3-")

    def test_include_async(self):
        """Test that included templates are rendered asynchronously"""
        test_cases = [
            Case(
                description="simple include",
                template="{% include 'foo' %}",
                context={},
                expect="1-2-3-",
                template_name="foo",
                calls=1,
            ),
            Case(
                description="include with arguments",
                template="{% include 'foo' with foo as bar, baz: 'hello' %}",
                context={},
                expect="1-2-3-",
                template_name="foo",
                calls=1,
            ),
            Case(
                description="include for array",
                template="{% include 'foo' for array %}",
                context={"array": [1, 2]},
                expect="1-2-3-1-2-3-",
                template_name="foo",
                calls=1,  # cached
            ),
        ]

        async def coro(template):
            return await template.render_async()

        for case in test_cases:
            with self.subTest(msg=case.description):
                env = Environment()
                template = env.from_string(case.template, globals=case.context)

                with patch(
                    "liquid.loaders.DictLoader.get_source_async", autospec=True
                ) as source:
                    source.side_effect = [
                        (
                            "{% for x in (1..3) %}{{x}}-{% endfor %}",
                            "foo",
                            None,
                        )
                    ]

                    result = asyncio.run(coro(template))

                    source.assert_awaited_with(env.loader, env=env, template_name="foo")
                    self.assertEqual(source.call_count, case.calls)
                    self.assertEqual(result, case.expect)

    def test_cover_render_async(self):
        """Test that `render`ed templates are loaded asynchronously."""
        test_cases = [
            Case(
                description="simple render",
                template="{% render 'foo' %}",
                context={},
                expect="1-2-3-",
                template_name="foo",
                calls=1,
            ),
            Case(
                description="render with arguments",
                template="{% render 'foo' with foo as bar, baz: 'hello' %}",
                context={},
                expect="1-2-3-",
                template_name="foo",
                calls=1,
            ),
            Case(
                description="render for array",
                template="{% render 'foo' for array %}",
                context={"array": [1, 2]},
                expect="1-2-3-1-2-3-",
                template_name="foo",
                calls=1,  # cached
            ),
        ]

        async def coro(template):
            return await template.render_async()

        for case in test_cases:
            with self.subTest(msg=case.description):
                with patch(
                    "liquid.loaders.DictLoader.get_source_async", autospec=True
                ) as source:
                    source.side_effect = [
                        (
                            "{% for x in (1..3) %}{{x}}-{% endfor %}",
                            "foo",
                            None,
                        )
                    ]

                    env = Environment()
                    template = env.from_string(case.template, globals=case.context)

                    result = asyncio.run(coro(template))

                    source.assert_awaited_with(env.loader, env=env, template_name="foo")
                    self.assertEqual(source.call_count, case.calls)
                    self.assertEqual(result, case.expect)


class MockAsyncDrop(abc.Mapping):
    def __init__(self, val):
        self.key = "foo"
        self.val = val

        self.call_count = 0
        self.await_count = 0

    def __len__(self):
        return 1

    def __iter__(self):
        return iter([self.key])

    def __getitem__(self, k):
        self.call_count += 1
        if k == self.key:
            return self.val
        raise KeyError(k)

    async def __getitem_async__(self, k):
        # Do IO here
        self.await_count += 1
        if k == self.key:
            return self.val
        raise KeyError(k)


class AsyncDropTestCase(unittest.TestCase):
    """Test that we can get items from a drop asynchronously."""

    def setUp(self) -> None:
        self.drop = MockAsyncDrop("hello")

    def test_awaited(self):
        """Test that __getitem_async__ is awaited when using render_async."""
        env = Environment()
        template = env.from_string(r"{{ drop.foo }}")

        async def coro():
            return await template.render_async(drop=self.drop)

        result = asyncio.run(coro())

        self.assertEqual(result, "hello")
        self.assertEqual(self.drop.await_count, 1)
        self.assertEqual(self.drop.call_count, 0)

    def test_called(self):
        """Test that __getitem_async__ is not called when rendering synchronously."""
        env = Environment()
        template = env.from_string(r"{{ drop.foo }}")
        result = template.render(drop=self.drop)

        self.assertEqual(result, "hello")
        self.assertEqual(self.drop.await_count, 0)
        self.assertEqual(self.drop.call_count, 1)
