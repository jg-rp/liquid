"""A JSON filter."""

import json
from typing import Any
from typing import Callable
from typing import Optional

from liquid.filter import int_arg
from liquid.filter import liquid_filter


class JSON:
    """Serialize an object to a JSON formatted string.

    Args:
        default: A function passed to `json.dumps`. This function is called
            in the event that the JSONEncoder does not know how to serialize an
            object. Defaults to `None`.
    """

    name = "json"

    def __init__(self, default: Optional[Callable[[Any], Any]] = None):
        self.default = default

    @liquid_filter
    def __call__(
        self,
        obj: object,
        indent: Optional[object] = None,
    ) -> str:
        indent = int_arg(indent) if indent else None
        return json.dumps(obj, default=self.default, indent=indent)
