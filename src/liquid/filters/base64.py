import base64
import binascii

from .._filter import FilterContext


def base64_encode(context: FilterContext, obj: object) -> str:
    return base64.b64encode(context.to_str(obj, "").encode()).decode()


def base64_decode(context: FilterContext, obj: object) -> str:
    try:
        return base64.b64decode(context.to_str(obj, "")).decode()
    except binascii.Error:
        raise context.error("invalid base64-encoded string")


def base64_url_safe_encode(context: FilterContext, obj: object) -> str:
    return base64.urlsafe_b64encode(context.to_str(obj, "").encode()).decode()


def base64_url_safe_decode(context: FilterContext, obj: object) -> str:
    try:
        return base64.urlsafe_b64decode(context.to_str(obj, "")).decode()
    except binascii.Error:
        raise context.error("invalid base64-encoded string")
