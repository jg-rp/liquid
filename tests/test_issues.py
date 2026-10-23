import pytest

from liquid import Environment, FileSystemLoader, parse, render
from liquid.exceptions import (
    LiquidSyntaxError,
    LiquidValueError,
    NoSuchTemplateError,
    ResourceLimitError,
)


def test_case_tag_raises_when_eof() -> None:
    # Before version 2.2.1 this would loop forever.
    with pytest.raises(LiquidSyntaxError):
        parse("{% case x %}")


def test_issue_202() -> None:
    # Before version 2.2.2 this would raise a ZeroDivisionError.
    #
    # Note that Shopify/liquid in strict2 mode raises syntax error here.
    # Lax and strict mode silently ignore a `cycle` tag with no arguments.
    assert render("{% cycle x: %}", {}) == ""

    with pytest.raises(LiquidSyntaxError):
        render("{% cycle %}", {})


def test_issue_203() -> None:
    env = Environment(
        loader=FileSystemLoader(
            "tests/fixtures/001/templates/",
            ext=".liquid",
        ),
    )

    # Specifically when `ext` is given, these were raising a ValueError
    # when calling `with_suffix` if the path has an empty name.

    with pytest.raises(NoSuchTemplateError):
        env.render("{% render '' %}", {})

    with pytest.raises(NoSuchTemplateError):
        env.render("{% render '.' %}", {})

    with pytest.raises(NoSuchTemplateError):
        env.render("{% render './' %}", {})

    with pytest.raises(NoSuchTemplateError):
        env.render("{% include '' %}", {})

    with pytest.raises(NoSuchTemplateError):
        env.render("{% include '.' %}", {})

    with pytest.raises(NoSuchTemplateError):
        env.render("{% include './' %}", {})


def test_issue_206() -> None:
    # Shopify/liquid in strict2 mode raises a syntax error.
    # Lax and strict modes silently ignore.
    with pytest.raises(LiquidSyntaxError):
        render("{{[[0]]}}", {})

    # Variables that resolve to non-strings too.
    assert render("{{ [x] }}", {"x": False}) == ""


def test_issue_208() -> None:
    parse(f"{{% {'liquid ' * 30} echo 1 %}}")

    with pytest.raises(ResourceLimitError):
        render(f"{{% {'liquid ' * 1000} echo 1 %}}", {})


def test_issue_209() -> None:
    # Before version 2.3.0 these examples would raise a ValueError.
    render(
        "{% tablerow x in y offset:9223372036854775808 cols:1 %}{% endtablerow %}", {}
    )
    render("{% for x in y offset:9223372036854775808 %}{% endfor %}", {})

    with pytest.raises(LiquidValueError):
        render(
            "{% for x in (0..9223372036854775808) offset:9223372036854775808 %}"
            "{% endfor %}",
            {},
        )


def test_issue_215() -> None:
    assert (
        render("{% for i in (1023..1025) %}{{ i }},{% endfor %}", {})
        == "1023,1024,1025,"
    )


def test_issue_217() -> None:
    assert render("{% tablerow _ in _ cols:8 %}{% endtablerow %}", {}) == ""


def test_issue_219() -> None:
    assert render("{% unless x >= y %}A{% endunless %}", {}) == "A"
    assert render("{% unless x <= y %}A{% endunless %}", {}) == "A"
    assert render("{% unless x > y %}A{% endunless %}", {}) == "A"


def test_issue_220() -> None:
    source = "\n".join(  # noqa: FLY002
        [
            "{{ (3..1) }}",
            "{{ (1..0) }}",
            "{{ (5..5) }}",
            "{{ (0..3) }}",
        ]
    )

    assert render(source, {}) == "3..1\n1..0\n5..5\n0..3"


def test_issue_223() -> None:
    assert render("{{ (empty..3) }}", {}) == "0..3"


@pytest.mark.timeout(2)
def test_issue_224() -> None:
    source = "{{" + " " * 3000
    assert render(source, {}) == source

    source = "{%" + " " * 3000
    assert render(source, {}) == source


def test_issue_228() -> None:
    assert render("{% if 1 >= 1 %}true{% else %}false{% endif %}", {}) == "true"
    assert render("{% if 1 <= 1 %}true{% else %}false{% endif %}", {}) == "true"
    assert render("{% if 1.5 >= 1.5 %}true{% else %}false{% endif %}", {}) == "true"
    assert render("{% if 'a' >= 'a' %}true{% else %}false{% endif %}", {}) == "true"
    assert render("{% if 2 >= 1 %}true{% else %}false{% endif %}", {}) == "true"

    assert render("{% if true >= false %}true{% else %}false{% endif %}", {}) == "false"
    assert render("{% if true <= false %}true{% else %}false{% endif %}", {}) == "false"
    assert render("{% if true <= true %}true{% else %}false{% endif %}", {}) == "false"
