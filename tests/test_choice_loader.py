import asyncio

import pytest

from liquid import DictLoader
from liquid import Environment
from liquid import RenderContext
from liquid.exceptions import TemplateNotFound
from liquid.loaders import BaseLoader
from liquid.loaders import ChoiceLoader
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

    template = env.get_template("a")
    assert template.render(you="World") == "Hello, World!"

    template = env.get_template("b")
    assert template.render() == "the quick brown fox"

    with pytest.raises(TemplateNotFound):
        env.get_template("c")


def test_choose_between_loaders_with_arguments() -> None:
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
    with pytest.raises(TemplateNotFound):
        env.get_template_with_args("c", uid="foo")

    # Get template 'a' without arguments.
    template = env.get_template("a")
    assert template.render(you="World") == "Goodbye, World!"

    # Get template 'a' with uid argument.
    template = env.get_template_with_args("a", uid="foo")
    assert template.render(you="World") == "Hello, World!"


def test_choose_between_loaders_with_arguments_async() -> None:
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
    async def coro() -> None:
        await env.get_template_with_args_async("c", uid="foo")

    with pytest.raises(TemplateNotFound):
        asyncio.run(coro())

    # Get template 'a' without arguments.
    async def coro_() -> str:
        template = env.get_template("a")
        return await template.render_async(you="World")

    assert asyncio.run(coro_()) == "Goodbye, World!"

    # Get template 'a' with uid argument.
    async def coro__() -> str:
        template = env.get_template_with_args("a", uid="foo")
        return await template.render_async(you="World")

    assert asyncio.run(coro__()) == "Hello, World!"


def test_choose_between_loaders_with_context() -> None:
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
    with pytest.raises(TemplateNotFound):
        env.from_string("{% include 'c' %}").render()

    # The mock context loader gets access to the active render context when
    # it's used from an `include` or `render` tag.
    template = env.from_string("{% include 'a' %}", globals={"uid": 1234})
    assert template.render(you="World") == "Hello, World!"
    assert "tag" in context_loader.kwargs
    assert context_loader.kwargs["tag"] == "include"
    assert "uid" in context_loader.kwargs
    assert context_loader.kwargs["uid"] == 1234  # noqa: PLR2004


def test_choose_between_loaders_with_context_async() -> None:
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
    async def coro() -> None:
        template_ = env.from_string("{% include 'c' %}")
        await template_.render_async()

    with pytest.raises(TemplateNotFound):
        asyncio.run(coro())

    # The mock context loader gets access to the active render context when
    # it's used from an `include` or `render` tag.
    template = env.from_string("{% include 'a' %}", globals={"uid": 1234})

    async def coro_() -> str:
        return await template.render_async(you="World")

    assert asyncio.run(coro_()) == "Hello, World!"
    assert "tag" in context_loader.kwargs
    assert context_loader.kwargs["tag"] == "include"
    assert "uid" in context_loader.kwargs
    assert context_loader.kwargs["uid"] == 1234  # noqa: PLR2004
