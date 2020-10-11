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

from typing import NamedTuple
from typing import List
from typing import Dict
from typing import Any
from typing import Mapping
from typing import Optional
from typing import Callable
from typing import Iterator

import yaml

from liquid.environment import Environment
from liquid.template import Template
from liquid.mode import Mode
from liquid.loaders import FileSystemLoader
from liquid.token import Token
from liquid.lex import get_lexer

from tests.mocks.tags.form_tag import CommentFormTag
from tests.mocks.tags.paginate_tag import PaginateTag

from tests.mocks.filters.json import JSON

from tests.mocks.filters.money import Money
from tests.mocks.filters.money import MoneyWithCurrency

from tests.mocks.filters.shop import AssetUrl
from tests.mocks.filters.shop import DefaultPagination
from tests.mocks.filters.shop import GlobalAssetUrl
from tests.mocks.filters.shop import ImgTag
from tests.mocks.filters.shop import LinkTo
from tests.mocks.filters.shop import LinkToType
from tests.mocks.filters.shop import LinkToVendor
from tests.mocks.filters.shop import ShopifyAssetUrl
from tests.mocks.filters.shop import StylesheetTag
from tests.mocks.filters.shop import ScriptTag
from tests.mocks.filters.shop import URLForType
from tests.mocks.filters.shop import URLForVendor
from tests.mocks.filters.shop import ProductImgURL
from tests.mocks.filters.shop import Pluralize
from tests.mocks.filters.shop import Within

from tests.mocks.filters.tag import HighlightActiveTag
from tests.mocks.filters.tag import LinkToAddTag
from tests.mocks.filters.tag import LinkToRemoveTag
from tests.mocks.filters.tag import LinkToTag

from tests.mocks.filters.weight import Weight, WeightWithUnit


class ThemedTemplate(NamedTuple):
    """Parsed template and theme."""

    theme: Template
    template: Template

    def render(self):
        """Render the theme with the template as its content."""
        # Override the theme's "template" drop with that of the content.
        content = self.template.render()
        self.theme.render(template=self.template.drop, content_for_layout=content)


class TemplateSource(NamedTuple):
    """A template's path and source."""

    path: pathlib.Path
    source: str

    def __repr__(self):
        return f"TemplateSource(template={self.path!r}, source='...')"


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

    env.add_filter(JSON.name, JSON(env))
    env.add_filter(Money.name, Money(env))
    env.add_filter(MoneyWithCurrency.name, MoneyWithCurrency(env))
    env.add_filter(AssetUrl.name, AssetUrl(env))
    env.add_filter(DefaultPagination.name, DefaultPagination(env))
    env.add_filter(GlobalAssetUrl.name, GlobalAssetUrl(env))
    env.add_filter(ImgTag.name, ImgTag(env))
    env.add_filter(LinkTo.name, LinkTo(env))
    env.add_filter(LinkToType.name, LinkToType(env))
    env.add_filter(LinkToVendor.name, LinkToVendor(env))
    env.add_filter(ShopifyAssetUrl.name, ShopifyAssetUrl(env))
    env.add_filter(StylesheetTag.name, StylesheetTag(env))
    env.add_filter(ScriptTag.name, ScriptTag(env))
    env.add_filter(URLForType.name, URLForType(env))
    env.add_filter(URLForVendor.name, URLForVendor(env))
    env.add_filter(ProductImgURL.name, ProductImgURL(env))
    env.add_filter(Pluralize.name, Pluralize(env))
    env.add_filter(HighlightActiveTag.name, HighlightActiveTag(env))
    env.add_filter(LinkToAddTag.name, LinkToAddTag(env))
    env.add_filter(LinkToRemoveTag.name, LinkToRemoveTag(env))
    env.add_filter(LinkToTag.name, LinkToTag(env))
    env.add_filter(Weight.name, Weight(env))
    env.add_filter(WeightWithUnit.name, WeightWithUnit(env))
    env.add_filter(Within.name, Within(env))


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
    # "snowboards" has a description, the others do not.
    data["collection"] = data["collections"]["snowboards"]

    data["blogs"] = {blog["handle"]: blog for blog in data["blogs"]}
    # NOTE: Changing 'link_lists' to 'linklists'
    data["linklists"] = {ll["handle"]: ll for ll in data["link_lists"]}
    data["pages"] = {page["handle"]: page for page in data["pages"]}

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


def lex(
    templates: List[ThemedTemplateSource],
    tokenizer: Callable[[str], Iterator[Token]],
):
    """Tokenize a list of templates using the given environment."""
    for bundle in templates:
        list(tokenizer(bundle.theme.source))
        list(tokenizer(bundle.template.source))


# pylint: disable=redefined-builtin
def parse(
    env: Environment,
    templates: List[ThemedTemplateSource],
    globals: Optional[Mapping[str, object]] = None,
) -> List[ThemedTemplate]:
    """Parse a list of templates using the given environment."""
    parsed_templates = []
    for bundle in templates:
        parsed_theme = env.from_string(
            bundle.theme.source, path=bundle.theme.path, globals=globals
        )

        parsed_template = env.from_string(
            bundle.template.source, path=bundle.template.path, globals=globals
        )

        parsed_templates.append(ThemedTemplate(parsed_theme, parsed_template))

    return parsed_templates


def render(templates: List[ThemedTemplate]):
    """Render each of the given templates."""
    for template in templates:
        template.render()


# pylint: disable=redefined-builtin
def parse_and_render(
    env: Environment,
    templates: List[ThemedTemplateSource],
    globals: Optional[Mapping[str, object]] = None,
):
    parsed_templates = parse(env, templates, globals=globals)
    render(parsed_templates)


def profile_lex(search_path: str):
    _, templates = setup_parse(search_path)

    cProfile.runctx(
        "[lex(templates, tokenizer) for _ in range(10)]",
        globals={"lex": lex, "templates": templates, "tokenizer": get_lexer()},
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
        "[render(templates) for _ in range(60)]",
        globals={"render": render, "templates": templates},
        locals={},
        sort="cumtime",
    )


def profile_parse_and_render(search_path: str):
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

    for template in parsed_templates:
        assert template.template.bytecode is None
        assert template.theme.bytecode is None

    return parsed_templates


def setup_parse(search_path: str):
    context_data = load_data()
    env = Environment(
        loader=FileSystemLoader("."), globals=context_data, tollerence=Mode.STRICT
    )
    register_mocks(env)
    templates = load_templates(search_path)

    return env, templates


def print_result(name: str, times: List[float], n_iterations: int, n_templates: int):
    best = min(times)
    n_calls = n_iterations * n_templates
    per_sec = round(n_calls / best, 2)

    per_i = best / n_iterations
    i_per_s = 1 / per_i

    print(f"{name:>31}: {best:.2}s ({per_sec:.2f} ops/s, {i_per_s:.2f} i/s)")


def benchmark(search_path: str, number: int = 100, repeat: int = 5):
    # Benchmark

    templates = load_templates(search_path)
    n_templates = len(templates) * 2
    n_calls = number * n_templates

    print(
        (
            f"Best of {repeat} rounds with {number} iterations per round "
            f"and {n_templates} ops per iteration ({n_calls} ops per round)."
        )
    )

    print_result(
        "lex template (not expressions)",
        timeit.repeat(
            "lex(templates, tokenizer)",
            setup="env, templates = setup_parse(search_path)",
            globals={
                **globals(),
                "search_path": search_path,
                "tokenizer": get_lexer(),
            },
            number=number,
            repeat=repeat,
        ),
        number,
        n_templates,
    )

    print_result(
        "lex and parse",
        timeit.repeat(
            "parse(env, templates)",
            setup="env, templates = setup_parse(search_path)",
            globals={**globals(), "search_path": search_path},
            number=number,
            repeat=repeat,
        ),
        number,
        n_templates,
    )

    print_result(
        "render",
        timeit.repeat(
            "render(templates)",
            setup="templates = setup_render(search_path)",
            globals={**globals(), "search_path": search_path},
            number=number,
            repeat=repeat,
        ),
        number,
        n_templates,
    )

    print_result(
        "lex, parse and render",
        timeit.repeat(
            "parse_and_render(env, templates)",
            setup="env, templates = setup_parse(search_path)",
            globals={**globals(), "search_path": search_path},
            number=number,
            repeat=repeat,
        ),
        number,
        n_templates,
    )


def main():
    search_path = "tests/fixtures/"

    args = sys.argv[1:]
    n_args = len(args)

    if n_args == 0:
        benchmark(search_path)
    elif n_args == 1 and args[0] == "--profile":
        profile_render(search_path)
        # profile_parse_and_render(search_path)
        # profile_parse(search_path)
        # profile_lex(search_path)
        # profile_compile(search_path)
    else:
        sys.stderr.write("usage: python performance.py [--profile]\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
