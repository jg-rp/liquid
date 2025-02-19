import pytest

from liquid import AwareBoundTemplate
from liquid import DictLoader
from liquid import Environment


@pytest.fixture
def env() -> Environment:
    env = Environment(
        loader=DictLoader(
            {
                "somename": "{{ template.name }}",
                "somedir/somename.liquid": "{{ template.directory }}",
                "somename.somesuffix.liquid": "{{ template.suffix }}",
            }
        )
    )

    env.template_class = AwareBoundTemplate
    return env


def test_template_name(env: Environment) -> None:
    """Test that templates have access to their name."""
    template = env.get_template(name="somename")
    assert template.render() == "somename"


def test_template_directory(env: Environment) -> None:
    """Test that templates have access to their directory name."""
    template = env.get_template(name="somedir/somename.liquid")
    assert template.render() == "somedir"


def test_template_suffix(env: Environment) -> None:
    """Test that templates have access to their suffix."""
    template = env.get_template(name="somename.somesuffix.liquid")
    assert template.render() == "somesuffix"


def test_drop_contains(env: Environment) -> None:
    """Test that we can check drop membership."""
    template = env.get_template(name="somename")
    assert isinstance(template, AwareBoundTemplate)
    assert "name" in template.drop
    assert "foo" not in template.drop


def test_drop_length(env: Environment) -> None:
    """Test that we get the length of a template drop."""
    template = env.get_template(name="somename")
    assert isinstance(template, AwareBoundTemplate)
    assert len(template.drop) == 3  # noqa: PLR2004


def test_iter_drop(env: Environment) -> None:
    """Test that we can iterate a template drop."""
    template = env.get_template(name="somename")
    assert isinstance(template, AwareBoundTemplate)
    keys = list(template.drop)
    assert keys == ["directory", "name", "suffix"]
