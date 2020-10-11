from liquid.filter import (
    Filter,
    maybe_one_arg,
    no_args,
    one_maybe_two_args,
    string_required,
    two_string_args_required,
    maybe_one_arg_required,
    one_arg_required,
)

from liquid.exceptions import FilterArgumentError


TRANSLATION_TABLE = {"'": None, '"': None, "(": None, ")": None, "[": None, "]": None}


# pylint: disable=arguments-differ, too-few-public-methods


def to_handle(s):
    _s = s.lower().translate(TRANSLATION_TABLE)
    # _s = re.sub(r"\W+", "-", _s)
    _s = "-".join(_s.split())
    # if _s.endswith("-"):
    #     _s = _s[:-1]
    # if _s.startswith("-"):
    #     _s = s[1:]

    return _s


class AssetUrl(Filter):

    __slots__ = ()

    name = "asset_url"

    @no_args
    def __call__(self, val, *args, **kwargs):
        return f"/files/1/[shop_id]/[shop_id]/assets/{val}"


class GlobalAssetUrl(Filter):

    __slots__ = ()

    name = "global_asset_url"

    @no_args
    def __call__(self, val, *args, **kwargs):
        return f"/global/{val}"


class ShopifyAssetUrl(Filter):

    __slots__ = ()

    name = "shopify_asset_url"

    @no_args
    def __call__(self, val, *args, **kwargs):
        return f"/shopify/{val}"


class ScriptTag(Filter):

    __slots__ = ()

    name = "script_tag"

    @no_args
    @string_required
    def __call__(self, val, *args, **kwargs):
        return f'<script src="{val}" type="text/javascript"></script>'


class StylesheetTag(Filter):

    __slots__ = ()

    name = "stylesheet_tag"

    @string_required
    def __call__(self, val, *args, **kwargs):
        if maybe_one_arg(self.name, args, kwargs):
            media = args[0]
        else:
            media = "all"

        return (
            f'<link href="{val}" rel="stylesheet" type="text/css"  media="{media}"  />'
        )


def link_to(link, url, title=""):
    return f'<a href="{url}" title="{title}">{link}</a>'


class LinkTo(Filter):

    __slots__ = ()

    name = "link_to"

    def __call__(self, val, *args, **kwargs):
        url, title = one_maybe_two_args(self.name, args, kwargs)
        if not title:
            title = ""

        return link_to(val, url, title)


class Within(Filter):

    __slots__ = ()

    name = "within"

    @string_required
    @one_arg_required
    def __call__(self, url, collection):
        # XXX: Strip slash
        return f"/collections/{collection['handle']}/{url}"


class ImgTag(Filter):

    __slots__ = ()

    name = "img_tag"

    @string_required
    def __call__(self, val, *args, **kwargs):
        if maybe_one_arg(self.name, args, kwargs):
            alt = args[0]
        else:
            alt = ""

        return f'<img src="{val}" alt="{alt}" />'


class URLForVendor(Filter):

    __slots__ = ()

    name = "url_for_vendor"

    @string_required
    @no_args
    def __call__(self, val, *args, **kwargs):
        return f"/collections/{to_handle(val)}"


class URLForType(Filter):

    __slots__ = ()

    name = "url_for_type"

    @string_required
    @no_args
    def __call__(self, val, *args, **kwargs):
        return f"/collections/{to_handle(val)}"


class LinkToVendor(Filter):

    __slots__ = ()

    name = "link_to_vendor"

    @string_required
    @no_args
    def __call__(self, val, *args, **kwargs):
        vendor = val
        if not vendor:
            return "Unknown Vendor"

        url_for_vendor = f'"/collections/{to_handle(val)}"'
        return f'<a href="{url_for_vendor}" title="{vendor}">{vendor}</a>'


class LinkToType(Filter):

    __slots__ = ()

    name = "link_to_type"

    @string_required
    @no_args
    def __call__(self, val, *args, **kwargs):
        typ = val
        if not typ:
            return "Unknown Type"

        url_for_type = f"/collections/{to_handle(val)}"
        return f'<a href="{url_for_type}" title="{typ}">{typ}</a>'


class ProductImgURL(Filter):

    __slots__ = ()

    name = "product_img_url"

    @string_required
    @maybe_one_arg_required
    def __call__(self, url, style="small"):
        if not url.startswith("products/"):
            raise FilterArgumentError(
                f"{self.name}: can only be called on product images"
            )

        if style == "original":
            return f"/files/shops/random_number/{url}"

        if style in ("grande", "large", "medium", "compact", "small", "thumb", "icon"):
            # XXX: Does not attempt to mimic reference implementation URL.
            return f"/files/shops/random_number/products/{style}"

        raise FilterArgumentError(
            f"{self.name}: valid parameters for filter 'size' are: "
            "original, grande, large, medium, compact, small, thumb and icon"
        )


class DefaultPagination(Filter):

    __slots__ = ()

    name = "default_pagination"

    @no_args
    def __call__(self, paginate):
        html = []

        if paginate["previous"]:
            link = link_to(paginate["previous"]["title"], paginate["previous"]["url"])
            html.append(f'<span class="prev">{link}</span>')

        for part in paginate["parts"]:
            if part["is_link"]:
                link = link_to(part["title"], part["url"])
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
            link = link_to(paginate["next"]["title"], paginate["next"]["url"])
            html.append(f'<span class="next">#{link}</span>')

        return " ".join(html)


class Pluralize(Filter):

    __slots__ = ()

    name = "pluralize"

    @two_string_args_required
    def __call__(self, val, *args, **kwargs):
        singular, plural = args[0], args[1]
        if val == 1:
            return singular
        return plural
