import unittest

from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple
from typing import Union

from liquid.expression import Expression
from liquid.expression import IdentifierPathElement
from liquid.expression import Identifier
from liquid.expression import IntegerLiteral
from liquid.expression import RangeLiteral

from liquid.expressions import parse_call_arguments
from liquid.expressions import parse_keyword_arguments
from liquid.expressions import parse_macro_arguments

from liquid.exceptions import Error
from liquid.exceptions import LiquidSyntaxError

Arguments = List[Tuple[Optional[str], Optional[Expression]]]


class Case(NamedTuple):
    """Table-driven test helper."""

    description: str
    expression: str
    expect: Union[Arguments, Error]


# TODO: tests
