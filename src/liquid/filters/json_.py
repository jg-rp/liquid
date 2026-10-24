import json
from collections.abc import Callable
from typing import Any

from .._filter import FilterContext


class JSON:
    """Serialize an object to a JSON formatted string.

    Parameters
    ----------
    default
        A function passed to ``json.dumps``. This function is called in the event that the
        JSONEncoder does not know how to serialize an object. Defaults to `None`.
    """

    name = "json"

    def __init__(self, default: Callable[[Any], Any] | None = None):
        self.default = default

    def __call__(
        self,
        context: FilterContext,
        left: object,
        indent: object | None = None,
    ) -> str:
        indent = context.to_int(indent) if indent else None
        return json.dumps(left, default=self.default, indent=indent)
