import pytest

from liquid import Environment
from liquid import FileSystemLoader
from liquid import parse
from liquid.exceptions import LiquidSyntaxError
from liquid.exceptions import TemplateNotFoundError


def test_case_tag_raises_when_eof():
    # Before version 2.2.1 this would loop forever.
    with pytest.raises(LiquidSyntaxError):
        parse("{% case x %}")


def test_issue_203():
    env = Environment(
        loader=FileSystemLoader(
            "tests/fixtures/001/templates/",
            ext=".liquid",
        ),
    )

    # Specifically when `ext` is given, these were raising a ValueError
    # when calling `with_suffix` if the path has an empty name.

    with pytest.raises(TemplateNotFoundError):
        env.render("{% render '' %}")

    with pytest.raises(TemplateNotFoundError):
        env.render("{% render '.' %}")

    with pytest.raises(TemplateNotFoundError):
        env.render("{% render './' %}")

    with pytest.raises(TemplateNotFoundError):
        env.render("{% include '' %}")

    with pytest.raises(TemplateNotFoundError):
        env.render("{% include '.' %}")

    with pytest.raises(TemplateNotFoundError):
        env.render("{% include './' %}")
