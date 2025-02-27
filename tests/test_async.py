"""Test Python Liquid's async API."""

from __future__ import annotations

import asyncio
import operator
import tempfile
import time
from collections import abc
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from typing import Optional

import pytest
from mock import patch

from liquid import CachingFileSystemLoader
from liquid import ChoiceLoader
from liquid import DictLoader
from liquid import Environment
from liquid import FileSystemLoader
from liquid import RenderContext
from liquid import Template
from liquid.exceptions import TemplateNotFound
from liquid.loader import TemplateSource
from liquid.template import BoundTemplate


@dataclass
class Case:
    """Table driven test helper."""

    description: str
    template: str
    context: dict[str, object]
    expect: str
    template_name: str
    calls: int


def test_basic_async() -> None:
    template = Template("{% for x in (1..3) %}{{x}}-{% endfor %}")

    async def coro() -> str:
        return await template.render_async()

    assert asyncio.run(coro()) == "1-2-3-"


def test_load_template_async() -> None:
    env = Environment(loader=FileSystemLoader("tests/fixtures/001/templates/"))

    async def coro() -> None:
        template = await env.get_template_async("index.liquid")
        assert isinstance(template, BoundTemplate)

    asyncio.run(coro())


def test_template_not_found_async() -> None:
    env = Environment(loader=FileSystemLoader("tests/fixtures/001/templates/"))

    async def coro() -> BoundTemplate:
        return await env.get_template_async("nosuchthing.liquid")

    with pytest.raises(TemplateNotFound):
        asyncio.run(coro())


def test_cached_template_async() -> None:
    """Test that async loaded templates are cached."""
    env = Environment(loader=CachingFileSystemLoader("tests/fixtures/001/templates/"))

    async def coro() -> BoundTemplate:
        return await env.get_template_async("index.liquid")

    template = asyncio.run(coro())
    assert template is asyncio.run(coro())


def test_async_up_to_date() -> None:
    """Test that async uptodate functions are awaited."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_path = Path(tmpdir) / "some.liquid"

        # Initial template content
        with template_path.open("w", encoding="UTF-8") as fd:
            fd.write("hello there\n")

        env = Environment(
            loader=CachingFileSystemLoader(search_path=tmpdir, auto_reload=True)
        )

        async def coro() -> None:
            template = await env.get_template_async("some.liquid")
            assert isinstance(template, BoundTemplate)
            up_to_date = await template.is_up_to_date_async()
            assert up_to_date is True

            # Update template content.
            time.sleep(0.01)  # Make sure some time has passed.
            template_path.touch()

            # Template is not up to date.
            up_to_date = await template.is_up_to_date_async()
            assert up_to_date is False

            template_ = await env.get_template_async("some.liquid")
            assert isinstance(template_, BoundTemplate)
            assert template_ is not template

            # Template is up to date.
            up_to_date = await template_.is_up_to_date_async()
            assert up_to_date is True

        asyncio.run(coro())


def test_nested_include_async() -> None:
    """Test that nested includes are rendered asynchronously."""

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    with patch(
        "liquid.builtin.loaders.dict_loader.DictLoader.get_source_async", autospec=True
    ) as source:
        source.side_effect = [
            TemplateSource(
                "{% include 'bar' %}",
                "bar",
                None,
            ),
            TemplateSource(
                "{% for x in (1..3) %}{{x}}-{% endfor %}",
                "foo",
                None,
            ),
        ]

        env = Environment()
        template = env.from_string("{% include 'foo' %}")

        result = asyncio.run(coro(template))

        source.assert_awaited()
        assert source.await_count == 2  # noqa: PLR2004
        assert result == "1-2-3-"


TEST_CASES: list[Case] = [
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


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_include_and_render_async(case: Case) -> None:
    env = Environment()
    template = env.from_string(case.template, globals=case.context)

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    with patch("liquid.builtin.DictLoader.get_source_async", autospec=True) as source:
        source.side_effect = [
            TemplateSource(
                "{% for x in (1..3) %}{{x}}-{% endfor %}",
                "foo",
                None,
            )
        ]

        result = asyncio.run(coro(template))
        assert source.call_count == case.calls
        assert result == case.expect


class MockAsyncDrop(abc.Mapping[str, object]):
    def __init__(self, val: object) -> None:
        self.key = "foo"
        self.val = val

        self.call_count = 0
        self.await_count = 0

    def __len__(self) -> int:  # pragma: no cover
        return 1

    def __iter__(self) -> Iterator[str]:  # pragma: no cover
        return iter([self.key])

    def __getitem__(self, k: str) -> object:
        self.call_count += 1
        if k == self.key:
            return self.val
        raise KeyError(k)  # pragma: no cover

    async def __getitem_async__(self, k: str) -> object:
        # Do IO here
        self.await_count += 1
        if k == self.key:
            return self.val
        raise KeyError(k)  # pragma: no cover


def test_await_async_drop() -> None:
    env = Environment()
    template = env.from_string(r"{{ drop.foo }}")
    drop = MockAsyncDrop("hello")

    async def coro() -> str:
        return await template.render_async(drop=drop)

    result = asyncio.run(coro())

    assert result == "hello"
    assert drop.await_count == 1
    assert drop.call_count == 0


def test_call_async_drop() -> None:
    """Test that __getitem_async__ is not called when rendering synchronously."""
    env = Environment()
    template = env.from_string(r"{{ drop.foo }}")
    drop = MockAsyncDrop("hello")
    result = template.render(drop=drop)

    assert result == "hello"
    assert drop.await_count == 0
    assert drop.call_count == 1


class AsyncMatterDictLoader(DictLoader):
    def __init__(
        self,
        templates: dict[str, str],
        matter: dict[str, dict[str, object]],
    ):
        super().__init__(templates)
        self.matter = matter

    async def get_source_async(
        self,
        env: Environment,  # noqa: ARG002
        template_name: str,
        *,
        context: Optional[RenderContext] = None,  # noqa: ARG002
        **kwargs: object,  # noqa: ARG002
    ) -> TemplateSource:
        try:
            source = self.templates[template_name]
        except KeyError as err:
            raise TemplateNotFound(template_name) from err

        return TemplateSource(
            source=source,
            name=template_name,
            uptodate=None,
            matter=self.matter.get(template_name),
        )


def test_matter_loader() -> None:
    """Test that template loaders can add to render context."""
    loader = AsyncMatterDictLoader(
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

    async def coro() -> None:
        template = await env.get_template_async("some")
        assert await template.render_async() == "Hello, World!"

        template = await env.get_template_async("other")
        assert await template.render_async() == "Goodbye, Smith."

        template = await env.get_template_async("thing")
        assert await template.render_async() == ""

    asyncio.run(coro())


def test_matter_global_priority() -> None:
    """Test that matter variables take priority over globals."""
    loader = AsyncMatterDictLoader(
        templates={"some": "Hello, {{ you }}!"},
        matter={"some": {"you": "Liquid"}},
    )

    env = Environment(loader=loader, globals={"you": "World"})

    async def coro() -> None:
        template = await env.get_template_async("some", globals={"you": "Jinja"})
        assert await template.render_async() == "Hello, Liquid!"

    asyncio.run(coro())


def test_matter_local_priority() -> None:
    """Test that render args take priority over matter variables."""
    loader = AsyncMatterDictLoader(
        templates={"some": "Hello, {{ you }}!"},
        matter={"some": {"you": "Liquid"}},
    )

    env = Environment(loader=loader)

    async def coro() -> None:
        template = await env.get_template_async("some")
        assert await template.render_async(you="John") == "Hello, John!"

    asyncio.run(coro())


def test_choose_between_loaders() -> None:
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

    async def coro() -> None:
        template = await env.get_template_async("a")
        assert await template.render_async(you="World") == "Hello, World!"

        template = await env.get_template_async("b")
        assert await template.render_async() == "the quick brown fox"

        with pytest.raises(TemplateNotFound):
            await env.get_template_async("c")

    asyncio.run(coro())
