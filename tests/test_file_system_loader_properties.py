import re

import pytest
from hypothesis import given
from hypothesis import strategies as st

from liquid import Environment, FileSystemLoader
from liquid.exceptions import NoSuchTemplateError


@pytest.fixture(scope="session")
def env() -> Environment:
    return Environment(
        loader=FileSystemLoader("tests/fixtures/001/templates/", ext=".liquid")
    )


# Avoid syntax errors from escaped quotes.
RE_RESERVED = re.compile(r"['\"]|[%}]\}")


@given(st.text().filter(lambda s: not RE_RESERVED.search(s)))
def test_filesystem_loader_handles_strings(env: Environment, text: str) -> None:
    with pytest.raises(NoSuchTemplateError):
        env.render(f"{{% render {text!r} %}}")
