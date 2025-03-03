"""Test case for the `Template` API."""

from liquid import Environment
from liquid import Mode
from liquid import Template


def test_implicit_environment() -> None:
    """Test that an Environment is created automatically."""
    template = Template(r"Hello, {{ you }}")
    assert template.env is not None


def test_environment_cache() -> None:
    """Test that we reuse Environments."""
    template = Template(r"Hello, {{ you }}!")
    another = Template(r"Goodbye, {{ you }}.")

    assert template.env == another.env

    lax = Template("something", tolerance=Mode.LAX)
    assert lax.env != template.env


def test_implicit_explicit() -> None:
    """Test that an implicit environment renders the same as an explicit one."""
    env = Environment()

    source = r"Hello, {{ you }}"
    context = {"you": "there"}

    some = env.from_string(source)
    other = Template(source)

    assert some.render(**context) == other.render(**context)
