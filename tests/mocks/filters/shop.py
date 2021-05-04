from liquid.filter import liquid_filter
from liquid.filter import string_filter

from liquid.exceptions import FilterArgumentError


TRANSLATION_TABLE = {"'": None, '"': None, "(": None, ")": None, "[": None, "]": None}


def to_handle(s):
    _s = s.lower().translate(TRANSLATION_TABLE)
    # _s = re.sub(r"\W+", "-", _s)
    _s = "-".join(_s.split())
    # if _s.endswith("-"):
    #     _s = _s[:-1]
    # if _s.startswith("-"):
    #     _s = s[1:]

    return _s


def _link_to(link, url, title=""):
    return f'<a href="{url}" title="{title}">{link}</a>'


@liquid_filter
def asset_url(val):
    return f"/files/1/[shop_id]/[shop_id]/assets/{val}"


@liquid_filter
def global_asset_url(val):
    return f"/global/{val}"


@liquid_filter
def shopify_asset_url(val):
    return f"/shopify/{val}"


@liquid_filter
def script_tag(val):
    return f'<script src="{val}" type="text/javascript"></script>'


@liquid_filter
def stylesheet_tag(val, media="all"):
    return f'<link href="{val}" rel="stylesheet" type="text/css"  media="{media}"  />'


@liquid_filter
def link_to(val, url, title=""):
    return _link_to(val, url, title)


@liquid_filter
def within(url, collection):
    # XXX: Strip slash
    return f"/collections/{collection['handle']}/{url}"


@liquid_filter
def img_tag(val, alt=""):
    return f'<img src="{val}" alt="{alt}" />'


@liquid_filter
def url_for_vendor(val):
    return f"/collections/{to_handle(val)}"


@liquid_filter
def url_for_type(val):
    return f"/collections/{to_handle(val)}"


@liquid_filter
def link_to_vendor(val):
    vendor = val
    if not vendor:
        return "Unknown Vendor"

    _url_for_vendor = f'"/collections/{to_handle(val)}"'
    return f'<a href="{_url_for_vendor}" title="{vendor}">{vendor}</a>'


@liquid_filter
def link_to_type(val):
    typ = val
    if not typ:
        return "Unknown Type"

    _url_for_type = f"/collections/{to_handle(val)}"
    return f'<a href="{_url_for_type}" title="{typ}">{typ}</a>'


@string_filter
def product_img_url(url, style="small"):
    if not url.startswith("products/"):
        raise FilterArgumentError(
            "product_img_url: can only be called on product images"
        )

    if style == "original":
        return f"/files/shops/random_number/{url}"

    if style in ("grande", "large", "medium", "compact", "small", "thumb", "icon"):
        # XXX: Does not attempt to mimic reference implementation URL.
        return f"/files/shops/random_number/products/{style}"

    raise FilterArgumentError(
        "product_img_url: valid parameters for filter 'size' are: "
        "original, grande, large, medium, compact, small, thumb and icon"
    )


@liquid_filter
def default_pagination(paginate):
    html = []

    if paginate["previous"]:
        link = _link_to(paginate["previous"]["title"], paginate["previous"]["url"])
        html.append(f'<span class="prev">{link}</span>')

    for part in paginate["parts"]:
        if part["is_link"]:
            link = _link_to(part["title"], part["url"])
            html.append(f'<span class="page">{link}</span>')
        elif (
            part["title"] == paginate["current_page"]
        ):  # XXX: Leading integer comparison.
            title = part["title"]
            html.append(f'<span class="page current">{title}</span>')
        else:
            title = part["title"]
            html.append(f'<span class="deco">{title}</span>')

    if paginate["next"]:
        link = _link_to(paginate["next"]["title"], paginate["next"]["url"])
        html.append(f'<span class="next">#{link}</span>')

    return " ".join(html)


@liquid_filter
def pluralize(val, singular, plural):
    if val == 1:
        return singular
    return plural
