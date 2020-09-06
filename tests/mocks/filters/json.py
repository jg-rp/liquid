import json

from liquid.filter import Filter, no_args
from liquid.exceptions import FilterArgumentError

# pylint: disable=arguments-differ, too-few-public-methods


class JSON(Filter):

    __slots__ = ()

    name = "json"

    @no_args
    def __call__(self, mapping):
        if not isinstance(mapping, dict):
            raise FilterArgumentError(
                f"{self.name}: expected an object, found {type(mapping)}"
            )
        return json.dumps({k: v for k, v in mapping.items() if k != "collections"})
