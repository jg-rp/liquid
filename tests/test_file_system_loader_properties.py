import re

import pytest
from hypothesis import given
from hypothesis import strategies as st

from liquid import Environment
from liquid import FileSystemLoader
from liquid.exceptions import TemplateNotFoundError


@pytest.fixture(scope="session")
def env() -> Environment:
    return Environment(
        loader=FileSystemLoader(
            "tests/fixtures/001/templates/",
            ext=".liquid",
        ),
    )


# Avoid syntax errors from escaped quotes.
RE_RESERVED = re.compile(r"['\"]|[%}]\}")


@given(st.text().filter(lambda s: not RE_RESERVED.search(s)))
def test_filesystem_loader_handles_strings(env: Environment, text: str) -> None:
    with pytest.raises(TemplateNotFoundError):
        env.render(f"{{% render {repr(text)} %}}")
