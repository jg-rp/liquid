# flake8: noqa
# pylint: disable=useless-import-alias,missing-module-docstring

from . import assign_tag
from . import capture_tag
from . import case_tag
from . import comment_tag
from . import cycle_tag
from . import decrement_tag
from . import echo_tag
from . import for_tag
from . import if_tag
from . import ifchanged_tag
from . import illegal
from . import include_tag
from . import increment_tag
from . import liquid_tag
from . import not_liquid
from . import output_statement
from . import raw_tag
from . import render_tag
from . import tablerow_tag
from . import unless_tag
from . import whitespace_control
from . import inline_comment_tag

from . import concat_filter
from . import first_filter
from . import join_filter
from . import last_filter
from . import map_filter
from . import reverse_filter
from . import sort_filter
from . import sort_natural_filter
from . import where_filter
from . import uniq_filter
from . import compact_filter
from . import abs_filter
from . import at_most_filter
from . import at_least_filter
from . import ceil_filter
from . import floor_filter
from . import divided_by_filter
from . import minus_filter
from . import plus_filter
from . import round_filter
from . import times_filter
from . import modulo_filter
from . import size_filter
from . import default_filter
from . import date_filter
from . import capitalize_filter
from . import append_filter
from . import downcase_filter
from . import escape_filter
from . import escape_once_filter
from . import lstrip_filter
from . import newline_to_br_filter
from . import prepend_filter
from . import remove_filter
from . import remove_first_filter
from . import remove_last_filter
from . import replace_filter
from . import replace_first_filter
from . import replace_last_filter
from . import slice_filter
from . import split_filter
from . import upcase_filter
from . import strip_filter
from . import rstrip_filter
from . import strip_html_filter
from . import strip_newlines_filter
from . import truncate_filter
from . import truncatewords_filter
from . import url_encode_filter
from . import url_decode_filter
from . import base64_encode_filter
from . import base64_decode_filter
from . import base64_url_safe_encode_filter
from . import base64_url_safe_decode_filter

from . import range_objects
from . import special
from . import identifiers

test_cases = [
    assign_tag,
    capture_tag,
    case_tag,
    comment_tag,
    cycle_tag,
    decrement_tag,
    echo_tag,
    for_tag,
    if_tag,
    ifchanged_tag,
    illegal,
    include_tag,
    increment_tag,
    liquid_tag,
    not_liquid,
    output_statement,
    raw_tag,
    render_tag,
    tablerow_tag,
    unless_tag,
    whitespace_control,
    concat_filter,
    first_filter,
    join_filter,
    last_filter,
    map_filter,
    reverse_filter,
    sort_filter,
    sort_natural_filter,
    where_filter,
    uniq_filter,
    compact_filter,
    abs_filter,
    at_most_filter,
    at_least_filter,
    ceil_filter,
    floor_filter,
    divided_by_filter,
    minus_filter,
    plus_filter,
    round_filter,
    times_filter,
    modulo_filter,
    size_filter,
    default_filter,
    date_filter,
    capitalize_filter,
    append_filter,
    downcase_filter,
    escape_filter,
    escape_once_filter,
    lstrip_filter,
    newline_to_br_filter,
    prepend_filter,
    remove_filter,
    remove_first_filter,
    remove_last_filter,
    replace_filter,
    replace_first_filter,
    replace_last_filter,
    slice_filter,
    split_filter,
    upcase_filter,
    strip_filter,
    rstrip_filter,
    strip_html_filter,
    strip_newlines_filter,
    truncate_filter,
    truncatewords_filter,
    url_encode_filter,
    url_decode_filter,
    base64_encode_filter,
    base64_decode_filter,
    base64_url_safe_encode_filter,
    base64_url_safe_decode_filter,
    range_objects,
    special,
    inline_comment_tag,
    identifiers,
]
