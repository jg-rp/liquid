"""Test liquid environment options."""

from liquid import Environment


def test_default_string_sequences() -> None:
    """Test that strings are not sequences by default."""
    env = Environment()
    template = env.from_string("{% for x in y %}{{ x }},{% endfor %}{{ y[0] }}")
    assert template.render(y="hello") == "hello,"


def test_enable_string_sequences() -> None:
    class MockEnv(Environment):
        string_sequences = True

    env = MockEnv()
    template = env.from_string("{% for x in y %}{{ x }},{% endfor %}{{ y[0] }}")
    assert template.render(y="hello") == "h,e,l,l,o,h"


def test_default_string_first_and_last() -> None:
    """Test that strings do not respond to first and last by default."""
    env = Environment()
    template = env.from_string("{{ y.first }}{{ y.last }}")
    assert template.render(y="hello") == ""


def test_enable_string_first_and_last() -> None:
    class MockEnv(Environment):
        string_first_and_last = True

    env = MockEnv()
    template = env.from_string("{{ y.first }}{{ y.last }}")
    assert template.render(y="hello") == "ho"
