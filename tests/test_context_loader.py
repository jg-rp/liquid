import asyncio

from liquid import DictLoader
from liquid import Environment
from liquid import RenderContext
from liquid.loaders import TemplateSource


class MockContextLoader(DictLoader):
    def __init__(self, templates: dict[str, str]):
        self.kwargs: dict[str, object] = {}
        super().__init__(templates)

    def get_source_with_context(
        self, context: RenderContext, template_name: str, **kwargs: str
    ) -> TemplateSource:
        self.kwargs.update(kwargs)
        self.kwargs["uid"] = context.resolve("uid", default=None, token=None)
        return super().get_source(context.env, template_name)

    async def get_source_with_context_async(
        self, context: RenderContext, template_name: str, **kwargs: str
    ) -> TemplateSource:
        self.kwargs.update(kwargs)
        self.kwargs["uid"] = context.resolve("uid", default=None, token=None)
        return await super().get_source_async(context.env, template_name)


def test_keyword_arguments() -> None:
    """Test that keyword arguments passed to `get_template_with_context` are
    available to a context-aware loader."""
    loader = MockContextLoader({"snippet": "hello"})
    env = Environment(loader=loader, cache_size=0)
    template = env.from_string("{% include 'snippet' %}")

    template.render()
    assert "tag" in loader.kwargs
    assert loader.kwargs["tag"] == "include"

    # and async
    loader.kwargs.clear()
    assert "tag" not in loader.kwargs

    async def coro() -> str:
        return await template.render_async()

    asyncio.run(coro())
    assert "tag" in loader.kwargs
    assert loader.kwargs["tag"] == "include"


def test_resolve_from_context() -> None:
    """Test context loaders can resolve render context variables."""
    loader = MockContextLoader({"snippet": "hello"})
    env = Environment(loader=loader, cache_size=0)
    template = env.from_string("{% include 'snippet' %}", globals={"uid": 1234})

    template.render()
    assert "uid" in loader.kwargs
    assert loader.kwargs["uid"] == 1234  # noqa: PLR2004

    # and async
    loader.kwargs.clear()
    assert "uid" not in loader.kwargs

    async def coro() -> str:
        return await template.render_async()

    asyncio.run(coro())
    assert "uid" in loader.kwargs
    assert loader.kwargs["uid"] == 1234  # noqa: PLR2004
