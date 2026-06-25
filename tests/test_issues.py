import pytest

from liquid import Environment
from liquid import FileSystemLoader
from liquid import StrictUndefined
from liquid import parse
from liquid import render
from liquid.exceptions import BlockNestingError
from liquid.exceptions import LiquidSyntaxError
from liquid.exceptions import TemplateNotFoundError
from liquid.exceptions import UndefinedError


def test_case_tag_raises_when_eof():
    # Before version 2.2.1 this would loop forever.
    with pytest.raises(LiquidSyntaxError):
        parse("{% case x %}")


def test_issue_202() -> None:
    # Before version 2.2.2 this would raise a ZeroDivisionError.
    #
    # Note that raising a syntax error here matches Shopify/liquid in strict2
    # mode. Lax and strict mode silently ignore a `cycle` tag with no
    # arguments.
    with pytest.raises(LiquidSyntaxError):
        render("{% cycle x: %}")

    with pytest.raises(LiquidSyntaxError):
        render("{% cycle %}")


def test_issue_203() -> None:
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


def test_issue_206() -> None:
    source = "{{[[0]]}}"
    assert render(source) == ""

    # And with strict undefined.
    env = Environment(undefined=StrictUndefined)

    with pytest.raises(UndefinedError):
        env.render(source)

    # Variables that resolve to non-strings too.
    assert render("{{ [x] }}", x=False) == ""


def test_issue_208() -> None:
    parse(f"{{% {'liquid ' * 30} echo 1 %}}")

    with pytest.raises(BlockNestingError):
        render(f"{{% {'liquid ' * 31} echo 1 %}}")
