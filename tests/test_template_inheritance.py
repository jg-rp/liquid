"""Test cases for `extends` and `block` tags."""

import asyncio

import pytest

from liquid import BoundTemplate
from liquid import Environment
from liquid.builtin import DictLoader
from liquid.exceptions import LiquidSyntaxError
from liquid.exceptions import RequiredBlockError
from liquid.exceptions import TemplateInheritanceError
from liquid.exceptions import UndefinedError
from liquid.undefined import StrictUndefined


def test_missing_required_block() -> None:
    """Test that we raise an exception if a required block is missing."""
    source = "{% extends 'foo' %}{% block baz %}{% endblock %}"
    partials = {"foo": "{% block bar required %}{% endblock %}"}

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(extra=True, loader=DictLoader(partials))
    template = env.from_string(source)

    with pytest.raises(RequiredBlockError):
        template.render()

    with pytest.raises(RequiredBlockError):
        asyncio.run(coro(template))


def test_missing_required_block_long_stack() -> None:
    """Test exception due to required block missing in a long stack."""
    source = "{% extends 'bar' %}"
    partials = {
        "foo": "{% block baz required %}{% endblock %}",
        "bar": "{% extends 'foo' %}{% block some %}hello{% endblock %}",
    }

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(extra=True, loader=DictLoader(partials))
    template = env.from_string(source)

    with pytest.raises(RequiredBlockError):
        template.render()

    with pytest.raises(RequiredBlockError):
        asyncio.run(coro(template))


def test_immediate_override_required_block() -> None:
    """Test that we can override a required block in the immediate child."""
    source = "{% extends 'foo' %}{% block bar %}hello{% endblock %}"
    partials = {"foo": "{% block bar required %}{% endblock %}"}
    expect = "hello"

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(extra=True, loader=DictLoader(partials))
    template = env.from_string(source)

    result = template.render()
    assert result == expect
    assert asyncio.run(coro(template)) == expect


def test_override_required_block_in_leaf() -> None:
    """Test that we can override a required block."""
    source = "{% extends 'foo' %}{% block baz %}hello{% endblock %}"
    partials = {
        "foo": "{% block baz required %}{% endblock %}",
        "bar": "{% extends 'foo' %}",
    }
    expect = "hello"

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(extra=True, loader=DictLoader(partials))
    template = env.from_string(source)

    result = template.render()
    assert result == expect
    assert asyncio.run(coro(template)) == expect


def test_override_required_block_in_stack() -> None:
    """Test that we can override a required block somewhere on the block stack."""
    source = "{% extends 'bar' %}"
    partials = {
        "foo": "{% block baz %}{% endblock %}",
        "bar": "{% extends 'foo' %}{% block baz %}hello{% endblock %}",
    }
    expect = "hello"

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(extra=True, loader=DictLoader(partials))
    template = env.from_string(source)

    result = template.render()
    assert result == expect
    assert asyncio.run(coro(template)) == expect


def test_override_required_block_not_in_base() -> None:
    """Test that we can override a required block from a non-base template."""
    source = "{% extends 'bar' %}{% block content %}hello{% endblock %}"
    partials = {
        "foo": "{% block content %}{% endblock %}",
        "bar": "{% extends 'foo' %}{% block content required %}{% endblock %}",
    }
    expect = "hello"

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(extra=True, loader=DictLoader(partials))
    template = env.from_string(source)

    result = template.render()
    assert result == expect
    assert asyncio.run(coro(template)) == expect


def test_missing_required_block_not_in_base() -> None:
    """Test required block from a non-base template."""
    source = "{% extends 'bar' %}"
    partials = {
        "foo": "{% block content %}{% endblock %}",
        "bar": "{% extends 'foo' %}{% block content required %}{% endblock %}",
    }

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(extra=True, loader=DictLoader(partials))
    template = env.from_string(source)

    with pytest.raises(RequiredBlockError):
        template.render()

    with pytest.raises(RequiredBlockError):
        asyncio.run(coro(template))


def test_override_required_block_directly() -> None:
    """Test that we raise an exception if rendering a required block directly."""
    source = "{% block foo required %}{% endblock %}"

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(
        extra=True,
    )
    template = env.from_string(source)

    with pytest.raises(RequiredBlockError):
        template.render()

    with pytest.raises(RequiredBlockError):
        asyncio.run(coro(template))


def test_too_many_extends() -> None:
    """Test that we raise an exception if more than one `extends` tag exists."""
    source = "{% extends 'foo' %}{% extends 'bar' %}"

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(
        extra=True,
    )
    template = env.from_string(source)

    with pytest.raises(TemplateInheritanceError):
        template.render()

    with pytest.raises(TemplateInheritanceError):
        asyncio.run(coro(template))


def test_invalid_block_name() -> None:
    """Test that we raise an exception given an invalid block name."""
    source = "{% extends 'foo' %}"
    partials = {
        "foo": "{% block 47 %}{% endblock %}",
    }

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(extra=True, loader=DictLoader(partials))
    template = env.from_string(source)

    with pytest.raises(LiquidSyntaxError):
        template.render()

    with pytest.raises(LiquidSyntaxError):
        asyncio.run(coro(template))


def test_block_drop_properties() -> None:
    """Test that we handle undefined block drop properties."""
    source = (
        "{% extends 'foo' %}"
        "{% block bar %}{{ block.nosuchthing }} and sue{% endblock %}"
    )
    partials = {"foo": "hello, {% block bar %}{{ you }}{% endblock %}"}

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(
        extra=True, loader=DictLoader(partials), undefined=StrictUndefined
    )
    template = env.from_string(source)

    with pytest.raises(UndefinedError):
        template.render()

    with pytest.raises(UndefinedError):
        asyncio.run(coro(template))


def test_block_no_super_block() -> None:
    """Test that we handle undefined block.super."""
    source = "hello, {% block bar %}{{ block.super }}{{ you }}{% endblock %}"

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(extra=True, undefined=StrictUndefined)
    template = env.from_string(source)

    with pytest.raises(UndefinedError):
        template.render()

    with pytest.raises(UndefinedError):
        asyncio.run(coro(template))


def test_duplicate_block_names() -> None:
    """Test that we raise an exception when a template has duplicate block names."""
    source = (
        "{% extends 'foo' %}{% block bar %}{% endblock %}{% block bar %}{% endblock %}"
    )
    partials = {"foo": "{% block bar %}{% endblock %}"}

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(extra=True, loader=DictLoader(partials))
    template = env.from_string(source)

    with pytest.raises(TemplateInheritanceError):
        template.render()

    with pytest.raises(TemplateInheritanceError):
        asyncio.run(coro(template))


def test_endblock_name() -> None:
    """Test that we can name `endblock` tags."""
    source = "{% extends 'foo' %}"
    partials = {"foo": "{% block baz %}hello{% endblock baz %}"}
    expect = "hello"

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(extra=True, loader=DictLoader(partials))
    template = env.from_string(source)

    result = template.render()
    assert result == expect
    assert asyncio.run(coro(template)) == expect


def test_mismatched_endblock_name() -> None:
    """Test that we raise an exception if an endblock label does not match."""
    source = "{% extends 'foo' %}"
    partials = {"foo": "{% block baz %}hello{% endblock something %}"}

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(extra=True, loader=DictLoader(partials))
    template = env.from_string(source)

    with pytest.raises(TemplateInheritanceError):
        template.render()

    with pytest.raises(TemplateInheritanceError):
        asyncio.run(coro(template))

    with pytest.raises(TemplateInheritanceError):
        env.from_string(partials["foo"])


def test_override_nested_block_and_outer_block() -> None:
    """Test that we can override a nested block and its outer block."""
    source = (
        '{% extends "foo" %}'
        "{% block title %}Home{% endblock %}"
        "{% block head %}{{ block.super }}Hello{% endblock %}"
    )
    partials = {
        "foo": (
            "{% block head %}"
            "<title>{% block title %}{% endblock %} - Welcome</title>"
            "{% endblock %}"
        )
    }
    expect = "<title>Home - Welcome</title>Hello"

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(extra=True, loader=DictLoader(partials))
    template = env.from_string(source)

    result = template.render()
    assert result == expect
    assert asyncio.run(coro(template)) == expect


def test_recursive_extends() -> None:
    """Test that we handle recursive extends."""
    loader = DictLoader(
        {
            "some": "{% extends 'other' %}",
            "other": "{% extends 'some' %}",
        }
    )

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(extra=True, loader=loader)
    template = env.get_template("some")

    with pytest.raises(TemplateInheritanceError):
        template.render()

    with pytest.raises(TemplateInheritanceError):
        asyncio.run(coro(template))


def test_overridden_block_to_many_blocks() -> None:
    """Test that we can override a block with many sub-blocks."""
    loader = DictLoader(
        {
            "base": "{% block head %}Hello - Welcome{% endblock %}",
            "other": (
                "{% extends 'base' %}"
                "{% block head %}"
                "{{ block.super }}:"
                "{% block foo %}!{% endblock %} - "
                "{% block bar %}{% endblock %}"
                "{% endblock %}"
            ),
            "some": (
                "{% extends 'other' %}"
                "{% block foo %}foo{{ block.super }}{% endblock %}"
                "{% block bar %}bar{% endblock %}"
            ),
        }
    )
    expect = "Hello - Welcome:foo! - bar"

    async def coro(template: BoundTemplate) -> str:
        return await template.render_async()

    env = Environment(extra=True, loader=loader)
    template = env.get_template("some")

    result = template.render()
    assert result == expect
    assert asyncio.run(coro(template)) == expect
