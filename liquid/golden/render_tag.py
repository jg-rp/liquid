"""Golden tests cases for testing liquid's `render` tag."""

from liquid.golden.case import Case
from liquid.golden.case import TEMPLATE_DROP_ATTRS

cases = [
    Case(
        description="string literal name",
        template=r"{% render 'product-hero', product: product %}",
        expect="foo\n- sports - garden ",
        globals={"product": {"title": "foo", "tags": ["sports", "garden"]}},
        partials={
            "product-hero": "\n".join(
                [
                    r"{{ product.title }}",
                    r"{% for tag in product.tags %}- {{ tag }} {% endfor %}",
                ]
            ),
        },
    ),
    Case(
        description="bound variable",
        template=r"{% render 'product-title' with collection.products[1] %}",
        expect="car",
        globals={"collection": {"products": [{"title": "bike"}, {"title": "car"}]}},
        partials={"product-title": r"{{ product-title.title }}"},
    ),
    Case(
        description="bound variable does not exist",
        template=r"{% render 'product-title' with no.such.thing %}",
        expect="",
        globals={},
        partials={"product-title": r"{{ product-title.title }}"},
    ),
    Case(
        description="bound array variable",
        template=r"{% render 'prod' for collection.products %}",
        expect="bikecar",
        globals={"collection": {"products": [{"title": "bike"}, {"title": "car"}]}},
        partials={"prod": r"{{ prod.title }}"},
    ),
    Case(
        description="bound variable with alias",
        template=r"{% render 'product-alias' with collection.products[1] as product %}",
        expect="car",
        globals={"collection": {"products": [{"title": "bike"}, {"title": "car"}]}},
        partials={
            "product-alias": r"{{ product.title }}",
        },
    ),
    Case(
        description="some keyword arguments",
        template=r"{% render 'product-args', foo: 'hello', bar: 'there' %}",
        expect="hello there",
        globals={},
        partials={
            "product-args": r"{{ foo }} {{ bar }}",
        },
    ),
    Case(
        description="some keyword arguments including a range literal",
        template=r"{% render 'product-args', foo: (1..3), bar: 'there' %}",
        expect="1#2#3 there",
        globals={},
        partials={
            "product-args": r"{{ foo | join: '#' }} {{ bar }}",
        },
    ),
    Case(
        description="some keyword arguments no leading coma",
        template=r"{% render 'product-args' foo: 'hello', bar: 'there' %}",
        expect="hello there",
        globals={},
        partials={"product-args": r"{{ foo }} {{ bar }}"},
    ),
    Case(
        description="template drop",
        template=r"{% render 'some/template-attrs.alt.txt' %}",
        expect="template-attrs.alt some template-attrs alt",
        globals={},
        partials={"some/template-attrs.alt.txt": TEMPLATE_DROP_ATTRS},
        standard=False,
    ),
    Case(
        description="template drop no parent",
        template=r"{% render 'template-attrs.alt.txt' %}",
        expect="template-attrs.alt  template-attrs alt",
        globals={},
        partials={"template-attrs.alt.txt": TEMPLATE_DROP_ATTRS},
        standard=False,
    ),
    Case(
        description="template drop no suffix",
        template=r"{% render 'some/template-attrs.txt' %}",
        expect="template-attrs some template-attrs ",
        globals={},
        partials={"some/template-attrs.txt": TEMPLATE_DROP_ATTRS},
        standard=False,
    ),
    Case(
        description="template drop no suffix or extension",
        template=r"{% render 'some/template-attrs' %}",
        expect="template-attrs some template-attrs ",
        globals={},
        partials={"some/template-attrs": TEMPLATE_DROP_ATTRS},
        standard=False,
    ),
    Case(
        description="parent variables go out of scope",
        template=(
            r"{% assign greeting = 'good morning' %}"
            r"{{ greeting }} "
            r"{% render 'outer-scope' %}"
            r"{{ greeting }}"
        ),
        expect="good morning good morning",
        partials={"outer-scope": r"{{ greeting }}"},
    ),
    Case(
        description="for loop variables go out of scope",
        template=(
            r"{% for i in (1..3) %}"
            r"{{ i }}"
            r"{% render 'loop-scope' %}"
            r"{{ i }}"
            r"{% endfor %}"
            r"{{ i }}"
        ),
        expect="112233",
        partials={"loop-scope": r"{{ i }}"},
    ),
    Case(
        description="assigned variables do not leak into outer scope",
        template=(
            r"{% render 'assign-outer-scope', customer: customer %} {{ last_name }}"
        ),
        expect="Hello, Holly ",
        globals={"customer": {"first_name": "Holly"}},
        partials={
            "assign-outer-scope": (
                r"Hello, {{ customer.first_name }}{% assign last_name = 'Smith' %}"
            )
        },
    ),
    Case(
        description="increment is isolated between renders",
        template=r"{% increment foo %} {% render 'increment' %} {% increment foo %}",
        expect="0 0 1",
        partials={"increment": r"{% increment foo %}"},
    ),
    Case(
        description="decrement is isolated between renders",
        template=r"{% decrement foo %} {% render 'decrement' %} {% decrement foo %}",
        expect="-1 -1 -2",
        partials={"decrement": r"{% decrement foo %}"},
    ),
    Case(
        description="forloop helper",
        template=r"{% render 'product' for collection.products %}",
        expect="Product: bike first index:1 Product: car last index:2 ",
        globals={"collection": {"products": [{"title": "bike"}, {"title": "car"}]}},
        partials={
            "product": (
                r"Product: {{ product.title }} "
                r"{% if forloop.first %}first{% endif %}"
                r"{% if forloop.last %}last{% endif %}"
                r" index:{{ forloop.index }} "
            ),
        },
    ),
    Case(
        description="render loops don't add parentloop",
        template=r"{% render 'product' for collection.products %}",
        expect="bike-0 0 1 2 car-1 0 1 2 ",
        globals={"collection": {"products": [{"title": "bike"}, {"title": "car"}]}},
        partials={
            "product": (
                r"{{ product.title }}-{{ forloop.index0 }} "
                r"{% for x in (1..3) %}"
                r"{{ forloop.index0 }}{{ forloop.parentloop.index0 }} "
                r"{% endfor %}"
            ),
        },
    ),
    Case(
        description="render loops can't access parentloop",
        template=(
            r"{% for x in (1..3) %}"
            r"{% render 'product' for collection.products %}"
            r"{% endfor %}"
        ),
        expect="bike-0 car-1 bike-0 car-1 bike-0 car-1 ",
        globals={"collection": {"products": [{"title": "bike"}, {"title": "car"}]}},
        partials={
            "product": (
                r"{{ product.title }}-{{ forloop.index0 }} "
                r"{{ forloop.parentloop.index0 }}"
            ),
        },
    ),
    Case(
        description="assign to keyword argument",
        template=r"{% render 'product-args', foo: 'hello' %}{{ foo }}",
        expect="hello goodbye",
        globals={},
        partials={
            "product-args": r"{{ foo }}{% assign foo='goodbye' %} {{ foo }}",
        },
    ),
]
