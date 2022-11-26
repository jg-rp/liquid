"""Profile or benchmark template parsing and/or rendering.

Note that each theme file (aka "layout") is parsed/rendered once for every non
theme template. So, given the four fixtures at the time of writing, with a
total of 34 .liquid files, 4 of which are a theme.liquid, `Template.render`
and/or `env.from_string` will be called 60 times per loop.
"""
# pylint: disable=missing-function-docstring
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
from liquid.template import BoundTemplate
from liquid.template import AwareBoundTemplate
from liquid.mode import Mode
from liquid.loaders import FileSystemLoader
from liquid.token import Token
from liquid.lex import get_lexer

from tests.mocks.tags.form_tag import CommentFormTag
from tests.mocks.tags.paginate_tag import PaginateTag

from tests.mocks.filters.json import json_

from tests.mocks.filters.money import money_
from tests.mocks.filters.money import money_with_currency

from tests.mocks.filters.shop import asset_url
from tests.mocks.filters.shop import default_pagination
from tests.mocks.filters.shop import global_asset_url
from tests.mocks.filters.shop import img_tag
from tests.mocks.filters.shop import link_to
from tests.mocks.filters.shop import link_to_type
from tests.mocks.filters.shop import link_to_vendor
from tests.mocks.filters.shop import shopify_asset_url
from tests.mocks.filters.shop import stylesheet_tag
from tests.mocks.filters.shop import script_tag
from tests.mocks.filters.shop import url_for_type
from tests.mocks.filters.shop import url_for_vendor
from tests.mocks.filters.shop import product_img_url
from tests.mocks.filters.shop import pluralize
from tests.mocks.filters.shop import within

from tests.mocks.filters.tag import highlight_active_tag
from tests.mocks.filters.tag import link_to_add_tag
from tests.mocks.filters.tag import link_to_remove_tag
from tests.mocks.filters.tag import link_to_tag

from tests.mocks.filters.weight import weight
from tests.mocks.filters.weight import weight_with_unit


class ThemedTemplate(NamedTuple):
    """Parsed template and theme."""

    theme: BoundTemplate
    template: BoundTemplate

    def render(self):
        """Render the theme with the template as its content."""
        # Override the theme's "template" drop with that of the content.
        content = self.template.render()
        assert isinstance(self.template, AwareBoundTemplate)
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

    env.add_filter("json", json_)
    env.add_filter("money", money_)
    env.add_filter("money_with_currency", money_with_currency)
    env.add_filter("asset_url", asset_url)
    env.add_filter("default_pagination", default_pagination)
    env.add_filter("global_asset_url", global_asset_url)
    env.add_filter("img_tag", img_tag)
    env.add_filter("link_to", link_to)
    env.add_filter("link_to_type", link_to_type)
    env.add_filter("link_to_vendor", link_to_vendor)
    env.add_filter("shopify_asset_url", shopify_asset_url)
    env.add_filter("stylesheet_tag", stylesheet_tag)
    env.add_filter("script_tag", script_tag)
    env.add_filter("url_for_type", url_for_type)
    env.add_filter("url_for_vendor", url_for_vendor)
    env.add_filter("product_img_url", product_img_url)
    env.add_filter("pluralize", pluralize)
    env.add_filter("highlight_active_tag", highlight_active_tag)
    env.add_filter("link_to_add_tag", link_to_add_tag)
    env.add_filter("link_to_remove_tag", link_to_remove_tag)
    env.add_filter("link_to_tag", link_to_tag)
    env.add_filter("weight", weight)
    env.add_filter("weight_with_unit", weight_with_unit)
    env.add_filter("within", within)


def load_data() -> Dict[str, Any]:
    """Mangle the "vision" database fixture into something that resembles a Shopify
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

    # Arbitrary top-level objects for templates that expect them.
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
        "[parse_and_render(env, templates) for _ in range(60)]",
        globals={
            "parse_and_render": parse_and_render,
            "env": env,
            "templates": templates,
        },
        locals={},
        sort="cumtime",
    )


def setup_render(search_path: str) -> List[ThemedTemplate]:
    env, template_sources = setup_parse(search_path)
    parsed_templates = parse(env, template_sources)
    return parsed_templates


def setup_parse(search_path: str):
    context_data = load_data()
    env = Environment(
        loader=FileSystemLoader("."),
        globals=context_data,
        tolerance=Mode.STRICT,
        strict_filters=True,
    )
    register_mocks(env)

    env.template_class = AwareBoundTemplate

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
        # profile_render(search_path)
        profile_parse_and_render(search_path)
        # profile_parse(search_path)
        # profile_lex(search_path)
        # profile_compile(search_path)
    else:
        sys.stderr.write("usage: python performance.py [--profile]\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
