import asyncio
import sys
from pathlib import Path

import pytest
from mock import patch

from liquid import BoundTemplate
from liquid import Environment
from liquid.exceptions import TemplateNotFound
from liquid.loaders import PackageLoader


def test_no_such_package() -> None:
    """Test that we get an exception at construction time if the
    package doesn't exist."""
    with pytest.raises(ModuleNotFoundError):
        Environment(loader=PackageLoader("nosuchthing"))


def test_package_root() -> None:
    """Test that we can load templates from a package's root."""
    with patch.object(sys, "path", [str(Path(__file__).parent)] + sys.path):
        loader = PackageLoader("mock_package", package_path="")

    env = Environment(loader=loader)

    with pytest.raises(TemplateNotFound):
        env.get_template("some")

    template = env.get_template("other")
    assert template.render(you="World") == "g'day, World!\n"


def test_package_directory() -> None:
    """Test that we can load templates from a package directory."""
    with patch.object(sys, "path", [str(Path(__file__).parent)] + sys.path):
        loader = PackageLoader("mock_package", package_path="templates")

    env = Environment(loader=loader)
    template = env.get_template("some")
    assert template.render(you="World") == "Hello, World!\n"


def test_package_with_list_of_paths() -> None:
    """Test that we can load templates from multiple paths in a package."""
    with patch.object(sys, "path", [str(Path(__file__).parent)] + sys.path):
        loader = PackageLoader(
            "mock_package", package_path=["templates", "templates/more_templates"]
        )

    env = Environment(loader=loader)
    template = env.get_template("some.liquid")
    assert template.render(you="World") == "Hello, World!\n"

    template = env.get_template("more_templates/thing.liquid")
    assert template.render(you="World") == "Goodbye, World!\n"

    template = env.get_template("thing.liquid")
    assert template.render(you="World") == "Goodbye, World!\n"


def test_package_root_async() -> None:
    """Test that we can load templates from a package's root asynchronously."""
    with patch.object(sys, "path", [str(Path(__file__).parent)] + sys.path):
        loader = PackageLoader("mock_package", package_path="")

    env = Environment(loader=loader)

    async def coro() -> BoundTemplate:
        return await env.get_template_async("other")

    template = asyncio.run(coro())
    assert template.render(you="World") == "g'day, World!\n"


def test_escape_package_root() -> None:
    """Test that we can't escape the package's package's root."""
    with patch.object(sys, "path", [str(Path(__file__).parent)] + sys.path):
        loader = PackageLoader("mock_package", package_path="")

    env = Environment(loader=loader)

    with pytest.raises(TemplateNotFound):
        env.get_template("../secret.liquid")
