import asyncio

import pytest

from liquid import CachingChoiceLoader
from liquid import ChoiceLoader
from liquid import DictLoader
from liquid import Environment
from liquid.exceptions import TemplateNotFound


def test_choose_between_loaders() -> None:
    loader = ChoiceLoader(
        [
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


def test_choose_between_loaders_async() -> None:
    loader = ChoiceLoader(
        [
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


def test_caching_choice_loader() -> None:
    loader = CachingChoiceLoader(
        [
            DictLoader({"a": "Hello, {{ you }}!"}),
            DictLoader(
                {
                    "a": "unreachable",
                    "b": "the quick brown {{ animal | default: 'fox' }}",
                }
            ),
        ],
    )

    env = Environment(loader=loader)
    assert len(loader.cache) == 0
    template = env.get_template("a")
    assert template.render(you="World") == "Hello, World!"
    assert len(loader.cache) == 1
    template = env.get_template("b")
    assert template.render() == "the quick brown fox"
    assert len(loader.cache) == 2  # noqa: PLR2004

    with pytest.raises(TemplateNotFound):
        env.get_template("c")
