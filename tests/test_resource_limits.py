import pytest

from liquid import DictLoader, Environment, ExtendedParser
from liquid.exceptions import ResourceLimitError

# TODO: test render score
# TODO: test render score cumulative


def test_recursive_render() -> None:
    """Test that we get an exception when rendering recursively."""
    env = Environment(
        loader=DictLoader(
            {
                "foo": "{% render 'bar' %}",
                "bar": "{% render 'foo' %}",
            }
        )
    )
    template = env.parse("{% render 'foo' %}")
    with pytest.raises(ResourceLimitError):
        template.render()


def test_recursive_include() -> None:
    """Test that we get an exception when including recursively."""
    env = Environment(
        loader=DictLoader(
            {
                "foo": "{% include 'bar' %}",
                "bar": "{% include 'foo' %}",
            }
        )
    )
    template = env.parse("{% include 'foo' %}")
    with pytest.raises(ResourceLimitError):
        template.render()


def test_set_context_depth_limit_render() -> None:
    """Test that we can set the context depth limit."""
    env = Environment(
        loader=DictLoader(
            {
                "foo": "{% render 'bar' %}",
                "bar": "{% render 'baz' %}",
                "baz": "Hello",
            }
        )
    )

    template = env.parse("{% render 'foo' %}")
    assert template.render() == "Hello"

    env.resource_limits.max_context_depth = 3

    with pytest.raises(ResourceLimitError):
        template.render()


def test_set_context_depth_limit_include() -> None:
    """Test that we can set the context depth limit."""
    env = Environment(
        loader=DictLoader(
            {
                "foo": "{% include 'bar' %}",
                "bar": "{% include 'baz' %}",
                "baz": "Hello",
            }
        )
    )

    template = env.parse("{% include 'foo' %}")
    assert template.render() == "Hello"

    env.resource_limits.max_context_depth = 3

    with pytest.raises(ResourceLimitError):
        template.render()


def test_default_loop_iteration_limit() -> None:
    """Test (effectively) that the default loop limit is None."""
    env = Environment()
    template = env.parse(
        "{% for i in (1..100) %}{% for j in (1..100) %}x{% endfor %}{% endfor %}"
    )

    template.render()


def test_set_loop_iteration_limit() -> None:
    """Test that we can set the loop iteration limit."""
    env = Environment()
    env.resource_limits.max_loop_iterations = 10_000

    env.parse(
        "{% for i in (1..100) %}"
        "{% for j in (1..100) %}"
        "{{ i }},{{ j }}"
        "{% endfor %}"
        "{% endfor %}"
    ).render()

    template = env.parse(
        "{% for i in (1..101) %}"
        "{% for j in (1..100) %}"
        "{{ i }},{{ j }}"
        "{% endfor %}"
        "{% endfor %}"
    )

    with pytest.raises(ResourceLimitError):
        template.render()


def test_render_carries_loop_count() -> None:
    """Test that a `render`ed template carries the loop count from its parent."""
    env = Environment(
        loader=DictLoader(
            {
                "foo": (
                    "{% for i in (1..50) %}"
                    "{% for j in (1..50) %}"
                    "{{ i }},{{ j }}"
                    "{% endfor %}"
                    "{% endfor %}"
                ),
            }
        )
    )

    env.resource_limits.max_loop_iterations = 3000
    template = env.parse("{% for i in (1..10) %}{% render 'foo' %}{% endfor %}")

    with pytest.raises(ResourceLimitError):
        template.render()


def test_nested_renders_carry_loop_count() -> None:
    """Test that multiple, nested renders carry the loop count."""
    env = Environment(
        loader=DictLoader(
            {
                "foo": ("{% for i in (1..50) %}{% render 'bar' %}{% endfor %}"),
                "bar": ("{% for j in (1..50) %}{{ j }}{% endfor %}"),
            }
        )
    )

    env.resource_limits.max_loop_iterations = 3000

    template = env.parse("{% for i in (1..10) %}{% render 'foo' %}{% endfor %}")

    with pytest.raises(ResourceLimitError):
        template.render()


def test_include_contributes_to_count() -> None:
    """Test that `included`ed templates contribute to the loop count."""
    env = Environment(
        loader=DictLoader(
            {
                "foo": (
                    "{% for i in (1..50) %}"
                    "{% for j in (1..50) %}"
                    "{{ i }},{{ j }}"
                    "{% endfor %}"
                    "{% endfor %}"
                ),
            }
        )
    )

    env.resource_limits.max_loop_iterations = 3000

    template = env.parse("{% for i in (1..10) %}{% include 'foo' %}{% endfor %}")

    with pytest.raises(ResourceLimitError):
        template.render()


def test_tablerow_contributes_to_count() -> None:
    """Test that the tablerow tag contributes to the loop count."""
    env = Environment()
    env.resource_limits.max_loop_iterations = 99

    template = env.parse(
        "{% for i in (1..10) %}"
        "{% tablerow i in (1..10) cols:2 %}"
        "{{ i }}"
        "{% endtablerow %}"
        "{% endfor %}"
    )

    with pytest.raises(ResourceLimitError):
        template.render()


@pytest.mark.timeout(2)
def test_nested_tablerow_loop_limit() -> None:
    source = "".join(
        "{% tablerow _ in(1..45) %}"
        "{% tablerow _ in (1..45) %}"
        "{% tablerow _ in (1..45) %}"
        "{% tablerow _ in (1..45) %}"
        "{% tablerow _ in(1..45) %}"
        "x"
        "{% endtablerow %}"
        "{% endtablerow %}"
        "{% endtablerow %}"
        "{% endtablerow %}"
        "{% endtablerow %}"
    )

    env = Environment()
    env.resource_limits.max_loop_iterations = 1000

    with pytest.raises(ResourceLimitError):
        env.render(source)


@pytest.mark.timeout(2)
def test_mixed_loop_limit() -> None:
    source = (
        "{% for _ in(1..45) %}{% tablerow _ in (1..45) %}x{% endtablerow %}{% endfor %}"
    )

    env = Environment()
    env.resource_limits.max_loop_iterations = 1000

    with pytest.raises(ResourceLimitError):
        env.render(source)


def test_set_max_assign_score() -> None:
    env = Environment()
    env.resource_limits.max_assign_score = 5

    env.parse(
        "{% assign a = 1 %}"
        "{% assign b = 2 %}"
        "{% assign c = 3 %}"
        "{% assign d = 4 %}"
        "{% assign e = 5 %}"
    ).render()

    template = env.parse(
        "{% assign a = 1 %}"
        "{% assign b = 2 %}"
        "{% assign c = 3 %}"
        "{% assign d = 4 %}"
        "{% assign e = 5 %}"
        "{% assign f = 6 %}"
    )

    with pytest.raises(ResourceLimitError):
        template.render()


def test_max_cumulative_assign_score() -> None:
    env = Environment(
        loader=DictLoader(
            {
                "foo": (
                    "{% assign a = 1 %}"
                    "{% assign b = 2 %}"
                    "{% assign c = 3 %}"
                    "{% assign d = 4 %}"
                    "{% assign e = 5 %}"
                )
            }
        )
    )

    env.resource_limits.max_assign_score_cumulative = 6

    template = env.parse("{% assign f = 6 %}{% assign g = 7 %}{% render 'foo' %}")

    with pytest.raises(ResourceLimitError):
        template.render()


def test_set_max_render_size() -> None:
    env = Environment()
    env.resource_limits.max_render_size = 5

    env.parse(
        "{% if false %}some literal that is longer then the limit{% endif %}hello"
    ).render()

    template = env.parse(
        "{% if true %}some literal that is longer then the limit{% endif %}hello"
    )

    with pytest.raises(ResourceLimitError):
        template.render()


def test_max_block_depth() -> None:
    env = Environment()
    env.resource_limits.max_block_depth = 3

    env.parse("{% if true %}{% endif %}")
    env.parse("{% if true %}{% if true %}{% endif %}{% endif %}")
    env.parse(
        "{% if true %}{% if true %}{% if true %}{% endif %}{% endif %}{% endif %}"
    )
    env.parse(
        "{% if true %}{% if true %}{% if true %}{% endif %}{% endif %}{% endif %}{% if true %}{% endif %}"
    )

    with pytest.raises(ResourceLimitError):
        env.parse(
            "{% if true %}"
            "  {% if true %}"
            "    {% if true %}"
            "      {% if true %}"
            "      {% endif %}"
            "    {% endif %}"
            "  {% endif %}"
            "{% endif %}"
        )


def test_max_block_depth_with_liquid_tag() -> None:
    env = Environment()
    env.resource_limits.max_block_depth = 3

    env.parse("{% if true %}{% endif %}")
    env.parse("{% if true %}{% liquid liquid echo 1 %}{% endif %}")
    env.parse("{% liquid liquid liquid echo 1 %}")

    with pytest.raises(ResourceLimitError):
        env.parse("{% if true %}{% liquid liquid liquid echo 1 %}{% endif %}")

    with pytest.raises(ResourceLimitError):
        env.parse("{% liquid liquid liquid liquid echo 1 %}")


def test_max_expression_depth() -> None:
    env = Environment()
    source = "{{ " + " and ".join(["true"] * 21) + " }}"
    assert env.render(source) == "true"

    env.resource_limits.max_expression_depth = 20

    with pytest.raises(ResourceLimitError):
        env.render(source)

    env = Environment(parser=ExtendedParser)
    assert env.render(source) == "true"

    env.resource_limits.max_expression_depth = 20

    with pytest.raises(ResourceLimitError):
        env.render(source)
