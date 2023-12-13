"""An implementation of the `split` filter."""

from typing import List

from liquid import soft_str
from liquid.filter import string_filter


@string_filter
def split(val: str, sep: str) -> List[str]:
    """Split string _val_ on delimiter _sep_."""
    if not sep:
        return list(val)

    if not val:
        return []

    if val == sep:
        return []

    return val.split(soft_str(sep))
