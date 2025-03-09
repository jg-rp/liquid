"""Built-in primary expressions.

A primary expression is any in line logical expression or primitive.
"""

from .logical import parse_boolean_primitive

parse_primary = parse_boolean_primitive

__all__ = ("parse_primary",)
