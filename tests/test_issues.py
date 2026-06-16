import pytest

from liquid import parse
from liquid.exceptions import LiquidSyntaxError


def test_case_tag_raises_when_eof():
    # Before version 2.2.1 this would loop forever.
    with pytest.raises(LiquidSyntaxError):
        parse("{% case x %}")
