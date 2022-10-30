"""Golden tests cases for testing liquid's `include` tag."""

from liquid.golden.case import Case
from liquid.golden.case import TEMPLATE_DROP_ATTRS

cases = [
    Case(
        description="string literal name",
        template=r"{% include 'product-hero' %}",
        expect="foo\n- sports\n- garden\n",
        globals={"product": {"title": "foo", "tags": ["sports", "garden"]}},
        partials={
            "product-hero": (
                r"{{ product.title }}"
                "\n"
                r"{% for tag in product.tags %}"
                r"- {{ tag }}"
                "\n"
                r"{% endfor %}"
            ),
        },
    ),
    Case(
        description="name from identifier",
        template=r"{% include snippet %}",
        expect="foo\n- sports\n- garden\n",
        globals={
            "snippet": "product-hero",
            "product": {"title": "foo", "tags": ["sports", "garden"]},
        },
        partials={
            "product-hero": (
                r"{{ product.title }}"
                "\n"
                r"{% for tag in product.tags %}"
                r"- {{ tag }}"
                "\n"
                r"{% endfor %}"
            ),
        },
    ),
    Case(
        description="bound variable",
        template=r"{% include 'product-title' with collection.products[1] %}",
        expect="car",
        globals={
            "collection": {
                "products": [{"title": "bike"}, {"title": "car"}],
            }
        },
        partials={
            "product-title": r"{{ product-title.title }}",
        },
    ),
    Case(
        description="bound variable does not exist",
        template=r"{% include 'product-title' with no.such.thing %}",
        expect="",
        partials={
            "product-title": r"{{ product-title.title }}",
        },
    ),
    Case(
        description="bound array variable",
        template=r"{% include 'prod' for collection.products %}",
        expect="bikecar",
        globals={
            "collection": {
                "products": [{"title": "bike"}, {"title": "car"}],
            }
        },
        partials={"prod": r"{{ prod.title }}"},
    ),
    Case(
        description="bound variable with alias",
        template=(
            r"{% include 'product-alias' with collection.products[1] as product %}"
        ),
        expect="car",
        globals={
            "collection": {
                "products": [{"title": "bike"}, {"title": "car"}],
            }
        },
        partials={"product-alias": r"{{ product.title }}"},
    ),
    Case(
        description="some keyword arguments",
        template=r"{% include 'product-args', foo: 'hello', bar: 'there' %}",
        expect="hello there",
        partials={"product-args": r"{{ foo }} {{ bar }}"},
    ),
    Case(
        description="some keyword arguments without leading comma",
        template=r"{% include 'product-args' foo: 'hello', bar: 'there' %}",
        expect="hello there",
        partials={"product-args": r"{{ foo }} {{ bar }}"},
    ),
    Case(
        description="some keyword arguments with float literals",
        template=r"{% include 'product-args' foo: 1.1, bar: 'there' %}",
        expect="1.1 there",
        partials={"product-args": r"{{ foo }} {{ bar }}"},
    ),
    Case(
        description="some keyword arguments with range literal",
        template=r"{% include 'product-args' foo: (1..3), bar: 'there' %}",
        expect="1#2#3 there",
        partials={"product-args": r"{{ foo | join: '#' }} {{ bar }}"},
    ),
    Case(
        description="template drop",
        template=r"{% include 'some/template-attrs.alt.txt' %}",
        expect="template-attrs.alt some template-attrs alt",
        partials={"some/template-attrs.alt.txt": TEMPLATE_DROP_ATTRS},
        standard=False,
    ),
    Case(
        description="template drop no parent",
        template=r"{% include 'template-attrs.alt.txt' %}",
        expect="template-attrs.alt  template-attrs alt",
        partials={"template-attrs.alt.txt": TEMPLATE_DROP_ATTRS},
        standard=False,
    ),
    Case(
        description="template drop no suffix",
        template=r"{% include 'some/template-attrs.txt' %}",
        expect="template-attrs some template-attrs ",
        partials={"some/template-attrs.txt": TEMPLATE_DROP_ATTRS},
        standard=False,
    ),
    Case(
        description="template drop no suffix or extension",
        template=r"{% include 'some/template-attrs' %}",
        expect="template-attrs some template-attrs ",
        partials={"some/template-attrs": TEMPLATE_DROP_ATTRS},
        standard=False,
    ),
    Case(
        description="use globals from outer scope",
        template=r"{% include 'outer-scope' %}",
        expect="Hello, Holly",
        globals={"customer": {"first_name": "Holly"}},
        partials={"outer-scope": r"Hello, {{ customer.first_name }}"},
    ),
    Case(
        description="assign persists in outer scope",
        template=r"{% include 'assign-outer-scope' %} {{ last_name }}",
        expect="Hello, Holly Smith",
        globals={"customer": {"first_name": "Holly"}},
        partials={
            "assign-outer-scope": (
                r"Hello, {{ customer.first_name }}{% assign last_name = 'Smith' %}"
            ),
        },
    ),
    Case(
        description="counter from outer scope",
        template=(
            r"{% increment foo %} "
            r"{% include 'increment-outer-scope' %} "
            r"{% increment foo %}"
        ),
        expect="0 1 2",
        partials={"increment-outer-scope": r"{% increment foo %}"},
    ),
    Case(
        description="break from include",
        template=r"{% for tag in product.tags %}{% include 'tag-break' %}{% endfor %}",
        expect="SPORTS",
        globals={"product": {"tags": ["sports", "garden"]}},
        partials={"tag-break": r"{{ tag | upcase }}{% break %}"},
    ),
    Case(
        description="break from nested include",
        template=r"{% for tag in product.tags %}{% include 'tag' %}{% endfor %}",
        expect="SPORTS break!",
        globals={"product": {"tags": ["sports", "garden"]}},
        partials={
            "tag": r"{{ tag | upcase }}{% include 'break' %}",
            "break": r" break!{% break %}",
        },
    ),
    Case(
        description="keyword arguments go out of scope",
        template=r"{% include 'product-args', foo: 'hello', bar: 'there' %}{{ foo }}",
        expect="hello there",
        partials={"product-args": r"{{ foo }} {{ bar }}"},
    ),
    Case(
        description="assign to a keyword argument",
        template=r"{% include 'product-args', foo: 'hello' %} {{ foo }}",
        expect="hello hello goodbye",
        partials={"product-args": r"{{ foo }}{% assign foo = 'goodbye' %} {{ foo }}"},
    ),
]
