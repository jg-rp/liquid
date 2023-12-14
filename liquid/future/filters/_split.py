"""An implementation of the `split` filter."""

from typing import List

from liquid import soft_str
from liquid.filter import string_filter


@string_filter
def split(val: str, sep: str) -> List[str]:
    """Split string _val_ on delimiter _sep_.

    If _sep_ is empty or _undefined_, _val_ is split into a list of single
    characters. If _val_ is empty or equal to _sep_, an empty list is returned.
    """
    if not sep:
        return list(val)

    sep = soft_str(sep)
    if not val or val == sep:
        return []

    return val.split(sep)
