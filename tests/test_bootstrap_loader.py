import asyncio

import pytest

from liquid import Environment
from liquid.exceptions import TemplateNotFound
from liquid.loaders import BaseLoader
from liquid.loaders import TemplateSource


class MockBootstrapLoader(BaseLoader):
    def __init__(self, namespaces: dict[str, dict[str, str]]):
        self.namespaces = namespaces

    def get_source(self, _: Environment, __: str) -> TemplateSource:
        raise TemplateNotFound(
            f"{self.__class__.__name__} requires a namespace argument"
        )

    def get_source_with_args(
        self,
        env: Environment,  # noqa: ARG002
        template_name: str,
        **kwargs: object,
    ) -> TemplateSource:
        try:
            namespace = kwargs["uid"]
        except KeyError as err:
            raise TemplateNotFound(
                f"{self.__class__.__name__} requires a namespace argument"
            ) from err

        try:
            source = self.namespaces[str(namespace)][template_name]
        except KeyError as err:
            raise TemplateNotFound(f"{namespace}:{template_name}") from err

        return TemplateSource(source, template_name, None)


@pytest.fixture
def env() -> Environment:
    loader = MockBootstrapLoader(
        namespaces={
            "abc": {"foo": "hello, {{ you }}", "bar": "g'day, {{ you }}"},
            "def": {"bar": "goodbye, {{ you }}"},
        }
    )

    return Environment(loader=loader)


def test_no_namespace(env: Environment) -> None:
    """Test that we get an exception when no namespace is given."""
    with pytest.raises(TemplateNotFound):
        env.get_template("bar")

    with pytest.raises(TemplateNotFound):
        env.get_template_with_args("bar")

    async def coro() -> None:
        await env.get_template_with_args_async("bar")

    with pytest.raises(TemplateNotFound):
        asyncio.run(coro())


def test_narrow_with_namespace(env: Environment) -> None:
    """Test that we can provide arbitrary arguments to a loader."""
    template = env.get_template_with_args("foo", uid="abc")
    assert template.render(you="world") == "hello, world"

    with pytest.raises(TemplateNotFound):
        # The namespace identified by this uid does not have a "foo" template.
        env.get_template_with_args("foo", uid="def")

    template = env.get_template_with_args("bar", uid="def")
    assert template.render(you="world") == "goodbye, world"

    async def coro() -> str:
        template = await env.get_template_with_args_async("bar", uid="abc")
        return await template.render_async(you="world")

    assert asyncio.run(coro()) == "g'day, world"


def test_fallback_to_get_source(env: Environment) -> None:
    """Test that we use `get_source()` by default."""
    env = Environment()
    with pytest.raises(TemplateNotFound):
        env.get_template_with_args("foo")
