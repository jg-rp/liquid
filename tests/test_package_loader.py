import asyncio
from pathlib import Path

import pytest

from liquid import Environment
from liquid import PackageLoader
from liquid.exceptions import TemplateNotFound


def test_load_from_package_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(Path(__file__).parent / "fixtures"))
    loader = PackageLoader("mock_package", package_path="")
    env = Environment(loader=loader)

    with pytest.raises(TemplateNotFound):
        env.get_template("some.liquid")

    template = env.get_template("other.liquid")
    assert template.render(you="World") == "g'day, World!\n"


def test_load_from_package_directory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(Path(__file__).parent / "fixtures"))
    loader = PackageLoader("mock_package", package_path="templates")
    env = Environment(loader=loader)

    template = env.get_template("some.liquid")
    assert template.render(you="World") == "Hello, World!\n"


def test_load_from_package_root_async(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(Path(__file__).parent / "fixtures"))
    loader = PackageLoader("mock_package", package_path="")
    env = Environment(loader=loader)

    async def coro() -> None:
        with pytest.raises(TemplateNotFound):
            await env.get_template_async("some.liquid")

        template = await env.get_template_async("other.liquid")
        assert await template.render_async(you="World") == "g'day, World!\n"

    asyncio.run(coro())


def test_no_such_package() -> None:
    with pytest.raises(ModuleNotFoundError):
        PackageLoader("nosuchthing")


def test_dont_escape_package_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(Path(__file__).parent / "fixtures"))
    loader = PackageLoader("mock_package", package_path="")
    env = Environment(loader=loader)

    with pytest.raises(TemplateNotFound):
        env.get_template("../secret.liquid")
