"""A mock JSON encoding filter."""

import json

from liquid.filter import liquid_filter
from liquid.exceptions import FilterArgumentError


@liquid_filter
def json_(mapping):
    """A filter function that dumps a dictionary in JSON."""
    if not isinstance(mapping, dict):
        raise FilterArgumentError(
            f"json expected an object, found {type(mapping).__name__}"
        )
    return json.dumps({k: v for k, v in mapping.items() if k != "collections"})
