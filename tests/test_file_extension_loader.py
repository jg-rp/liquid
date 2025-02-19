from pathlib import Path

import pytest

from liquid import BoundTemplate
from liquid import Environment
from liquid import FileExtensionLoader
from liquid.exceptions import TemplateNotFound


def test_load_template_with_missing_extension() -> None:
    """Test that we can load a template from the file system when a file extension
    is missing."""
    env = Environment(
        loader=FileExtensionLoader(
            search_path="tests/fixtures/001/templates",
            ext=".liquid",
        )
    )
    template = env.get_template(name="index")
    assert isinstance(template, BoundTemplate)


def test_stay_in_search_path() -> None:
    """Test that we can't stray above the search path."""
    env = Environment(
        loader=FileExtensionLoader(
            search_path="tests/fixtures/subfolder",
            ext=".liquid",
        )
    )

    with pytest.raises(TemplateNotFound):
        env.get_template(name="../001/templates/index")


def test_multiple_search_paths() -> None:
    """Test that we can search multiple directories for templates."""
    env = Environment(
        loader=FileExtensionLoader(
            search_path=[
                "tests/fixtures/",
                "tests/fixtures/subfolder/",
            ],
            ext=".liquid",
        )
    )

    template = env.get_template(name="fallback.html")
    assert isinstance(template, BoundTemplate)
    assert template.path == Path("tests/fixtures/subfolder/fallback.html")


def test_template_not_found() -> None:
    """Test that we get an error if the template does not exist."""
    env = Environment(
        loader=FileExtensionLoader(
            search_path="tests/fixtures/001/templates/",
            ext=".liquid",
        )
    )
    with pytest.raises(TemplateNotFound):
        env.get_template(name="nosuchthing")
