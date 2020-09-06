"""Profile or benchmark template parsing and/or rendering.

Note that each theme file (aka "layout") is parsed/rendered once for every non
theme template. So, given the four fixtures at the time of writing, with a
total of 34 .liquid files, 4 of which are a theme.liquid, `Template.render`
and/or `env.from_string` will be called 60 times per loop.
"""
import cProfile
import pathlib
import timeit
import sys

from typing import NamedTuple, List, Dict, Any, Mapping

import yaml

from liquid.environment import Environment, Template
from liquid.loaders import FileSystemLoader
from liquid.lex import get_lexer

from tests.mocks.tags.form_tag import CommentFormTag
from tests.mocks.tags.paginate_tag import PaginateTag

from tests.mocks.filters.json import JSON
from tests.mocks.filters.money import Money, MoneyWithCurrency
from tests.mocks.filters.shop import (
    AssetUrl,
    DefaultPagination,
    GlobalAssetUrl,
    ImgTag,
    LinkTo,
    LinkToType,
    LinkToVendor,
    ShopifyAssetUrl,
    StylesheetTag,
    ScriptTag,
    URLForType,
    URLForVendor,
    ProductImgURL,
    Pluralize,
    Within,
)

from tests.mocks.filters.tag import (
    HighlightActiveTag,
    LinkToAddTag,
    LinkToRemoveTag,
    LinkToTag,
)

from tests.mocks.filters.weight import Weight, WeightWithUnit


class ThemedTemplate(NamedTuple):
    """Parsed template and theme."""

    template: Template
    theme: Template

    def render(self):
        """Render the theme with the template as its content."""
        # Override the theme's "template" drop with that of the content.
        self.theme.render(
            template=self.template.drop, content_for_layout=self.template.render()
        )


class TemplateSource(NamedTuple):
    """A template's path and source."""

    path: pathlib.Path
    source: str


class ThemedTemplateSource(NamedTuple):
    """Template and theme source and path."""

    template: TemplateSource
    theme: TemplateSource


def register_mocks(env: Environment):
    """Register mock tags and filters the given environment.

    Mock tags and filters mimic Shopify specific additions to Liquid's builtin
    tags and filters.
    """
    env.add_tag(CommentFormTag)
    env.add_tag(PaginateTag)

    env.filters[JSON.name] = JSON(env)
    env.filters[Money.name] = Money(env)
    env.filters[MoneyWithCurrency.name] = MoneyWithCurrency(env)
    env.filters[AssetUrl.name] = AssetUrl(env)
    env.filters[DefaultPagination.name] = DefaultPagination(env)
    env.filters[GlobalAssetUrl.name] = GlobalAssetUrl(env)
    env.filters[ImgTag.name] = ImgTag(env)
    env.filters[LinkTo.name] = LinkTo(env)
    env.filters[LinkToType.name] = LinkToType(env)
    env.filters[LinkToVendor.name] = LinkToVendor(env)
    env.filters[ShopifyAssetUrl.name] = ShopifyAssetUrl(env)
    env.filters[StylesheetTag.name] = StylesheetTag(env)
    env.filters[ScriptTag.name] = ScriptTag(env)
    env.filters[URLForType.name] = URLForType(env)
    env.filters[URLForVendor.name] = URLForVendor(env)
    env.filters[ProductImgURL.name] = ProductImgURL(env)
    env.filters[Pluralize.name] = Pluralize(env)
    env.filters[HighlightActiveTag.name] = HighlightActiveTag(env)
    env.filters[LinkToAddTag.name] = LinkToAddTag(env)
    env.filters[LinkToRemoveTag.name] = LinkToRemoveTag(env)
    env.filters[LinkToTag.name] = LinkToTag(env)
    env.filters[Weight.name] = Weight(env)
    env.filters[WeightWithUnit.name] = WeightWithUnit(env)
    env.filters[Within.name] = Within(env)


def load_data() -> Dict[str, Any]:
    """Mangle the "vision" database fixture into somthing that resembles a Shopify
    render context.

    We're trying hard to transform input data to match that of the reference
    implementation so that we can do a direct comparison between benchmarks.

    See https://github.com/Shopify/liquid/blob/master/performance/shopify/database.rb
    """
    with open("tests/fixtures/vision.database.yml", "r") as fd:
        data = yaml.load(fd, Loader=yaml.Loader)

    # Collections contain products, but shove a list of collections that a product
    # belongs to into each product object too.
    collection_members = {}

    for collection in data["collections"]:
        collection_members[collection["id"]] = [p["id"] for p in collection["products"]]

    for product in data["products"]:
        product_collections = []
        for collection in data["collections"]:
            if product["id"] in collection_members[collection["id"]]:
                product_collections.append(collection)
        product["collections"] = product_collections

    # Arbitrary top-level objects for tempaltes that expect them.
    data["product"] = data["products"][0]
    data["blog"] = data["blogs"][0]
    data["article"] = data["blog"]["articles"][0]

    data["cart"] = {
        "total_price": sum(
            itm["line_price"] * itm["quantity"] for itm in data["line_items"]
        ),
        "item_count": len(data["line_items"]),
        "items": data["line_items"],
    }

    # Key some objects by their handle
    data["collections"] = {c["handle"]: c for c in data["collections"]}
    data["blogs"] = {blog["handle"]: blog for blog in data["blogs"]}
    # XXX: Changing 'link_lists' to 'linklists'
    data["linklists"] = {ll["handle"]: ll for ll in data["link_lists"]}
    data["pages"] = {page["handle"]: page for page in data["pages"]}

    # "snowboards" has a description, the others do not.
    data["collection"] = data["collections"]["snowboards"]

    return data


# pylint: disable=redefined-builtin
def load_templates(search_path: str = "tests/fixtures/") -> List[ThemedTemplateSource]:
    """Read template files and bundle them with their themes."""
    paths = list(pathlib.Path(search_path).glob("**/*.liquid"))

    # Don't render or parse *theme.liquid directly
    template_paths = [p for p in paths if p.stem != "theme"]
    theme_paths = [p for p in paths if p.stem == "theme"]

    themes = {}  # Map of theme name to parsed theme Template
    for path in theme_paths:
        with path.open() as fd:
            theme_source = fd.read()
        themes[path.parent.stem] = (path, theme_source)

    templates = []

    for path in template_paths:
        with path.open() as fd:
            template_source = fd.read()

        theme = TemplateSource(*themes[path.parent.stem])
        template = TemplateSource(path, template_source)
        templates.append(ThemedTemplateSource(template, theme))

    return templates


# pylint: disable=redefined-builtin
def lex(env: Environment, templates: List[ThemedTemplateSource]):
    """Tokenize a list of templates using the given environment."""
    lexer = get_lexer(env)
    for bundle in templates:
        list(lexer.tokenize(bundle.theme.source))
        list(lexer.tokenize(bundle.template.source))


# pylint: disable=redefined-builtin
def parse(
    env: Environment,
    templates: List[ThemedTemplateSource],
    globals: Mapping[str, Any] = None,
) -> List[ThemedTemplate]:
    """Parse a list of templates using the given environment."""
    parsed_tempaltes = []
    for bundle in templates:
        parsed_theme = env.from_string(
            bundle.theme.source, path=bundle.theme.path, globals=globals
        )

        parsed_template = env.from_string(
            bundle.template.source, path=bundle.template.path, globals=globals
        )

        parsed_tempaltes.append(ThemedTemplate(parsed_theme, parsed_template))

    return parsed_tempaltes


def render(templates: List[ThemedTemplate]):
    """Render each of the given templates."""
    for template in templates:
        template.render()


# pylint: disable=redefined-builtin
def parse_and_render(
    env: Environment,
    templates: List[ThemedTemplateSource],
    globals: Mapping[str, Any] = None,
):
    parsed_templates = parse(env, templates, globals=globals)
    render(parsed_templates)


def profile_lex(search_path: str):
    env, templates = setup_parse(search_path)

    cProfile.runctx(
        "[lex(env, templates) for _ in range(10)]",
        globals={"lex": lex, "templates": templates, "env": env},
        locals={},
        sort="cumtime",
    )


def profile_parse(search_path: str):
    env, templates = setup_parse(search_path)

    cProfile.runctx(
        "[parse(env, templates) for _ in range(5)]",
        globals={"parse": parse, "templates": templates, "env": env},
        locals={},
        sort="cumtime",
    )


def profile_render(search_path: str):
    templates = setup_render(search_path)

    cProfile.runctx(
        "[render(templates) for _ in range(5)]",
        globals={"render": render, "templates": templates},
        locals={},
        sort="cumtime",
    )


def profile_parse_and_render(search_path):
    env, templates = setup_parse(search_path)

    cProfile.runctx(
        "parse_and_render(env, templates)",
        globals={"parse_and_render": parse_and_render},
        locals={"env": env, "templates": templates},
        sort="cumtime",
    )


def setup_render(search_path: str) -> List[ThemedTemplate]:
    env, template_sources = setup_parse(search_path)
    parsed_templates = parse(env, template_sources)
    return parsed_templates


def setup_parse(search_path):
    context_data = load_data()
    env = Environment(loader=FileSystemLoader("."), globals=context_data)
    register_mocks(env)
    templates = load_templates(search_path)

    return env, templates


def benchmark(search_path: str, number: int = 100):
    # Benchmark
    print(
        timeit.repeat(
            "lex(env, templates)",
            setup="env, templates = setup_parse(search_path)",
            globals={**globals(), "search_path": search_path},
            number=number,
        )
    )

    # print(
    #     timeit.repeat(
    #         "parse(env, templates)",
    #         setup="env, templates = setup_parse(search_path)",
    #         globals={**globals(), "search_path": search_path},
    #         number=number,
    #     )
    # )

    # print(
    #     timeit.repeat(
    #         "render(templates)",
    #         setup="templates = setup_render(search_path)",
    #         globals={**globals(), "search_path": search_path},
    #         number=number,
    #     )
    # )

    # print(
    #     timeit.repeat(
    #         "parse_and_render(env, templates)",
    #         setup="env, templates = setup_parse(search_path)",
    #         globals={**globals(), "search_path": search_path},
    #         number=number,
    #     )
    # )


def main():
    search_path = "tests/fixtures/"

    args = sys.argv[1:]
    n_args = len(args)

    if n_args == 0:
        benchmark(search_path)
    elif n_args == 1 and args[0] == "--profile":
        # profile_render(search_path)
        # profile_parse_and_render(search_path)
        # profile_parse(search_path)
        profile_lex(search_path)
    else:
        sys.stderr.write("usage: python performance.py [--profile]\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
