import difflib
import os
import sys

from liquid import Environment

TEMPLATE = """\
{% assign dow = "Tuesday" %}
Hello {{ user.name }}. It is {% comment %} upper case day of week {% endcomment %} {{ dow | upcase}}.

{% if collection.title == "sale items" %}
    Sale today.
{% else %}
    No sale.
{% endif %}

{% unless user.name == "Bill" %}
    Where is Bill?
{% endunless %}

{% assign array = "1,2,3,4,5,6" | split: "," %}
{% for item in array limit:2 %}
  {{ item }}
{% endfor %}

{% assign handle = "burger" %}
{% case handle %}
    {% when "cake" %}
        This is a cake
    {% when "cookie" %}
        This is a cookie
    {% else %}
        This is not a cake nor a cookie
{% endcase %}

{% for i in (3..5) %}{{ i }} {% endfor %}
{% assign num = 4 %}
{% for i in (1..num) %}{{ i }} {% endfor %}
{% for i in (1..5) %}
  {% if i == 4 %}
    {% continue %}
  {% else %}
    {{ i }} {{ forloop.first }} {{ forloop.last }} {{ forloop.index0 }} {{ forloop.rindex0 }} {{ forloop.index }} {{ forloop.rindex }}
  {% endif %}
{% endfor %}

{% for product in collection.products %}
    {{ product.title }}
    {% for tag in product.tags %}
       {{ product.title }} - {{ tag }}
    {% endfor %}
{% else %}
    No products.
{% endfor %}

{% raw %}{{ nosuchthing }} a tag starts with {% more literal {% endraw %}

{% assign favorite_food = "pizza" %}
{% assign age = 35 %}

{% capture about_me %}
I am {{ age }} and my favorite food is {{ favorite_food }}.
{% endcapture %}

{{ about_me }}
{{ about_me }}

{% cycle 'one', 'two', 'three' %}
{% cycle 'one', 'two', 'three' %}
{% cycle 'one', 'two', 'three' %}
{% cycle 'one', 'two', 'three' %}

{% cycle 'group 1': 'one', 'two', 'three' %}
{% cycle 'group 1': 'one', 'two', 'three' %}
{% cycle 'group 2': 'one', 'two', 'three' %}
{% cycle 'group 2': 'one', 'two', 'three' %}

{% assign my_number = 10 %}

{% increment my_number %}
{% increment my_number %}
{% increment my_number %}
{% decrement my_number %}

{{ my_number }}

{% decrement variable %}
{% decrement variable %}
{% decrement variable %}

<table>
{% tablerow product in collection.products cols:2 %}
  {{ product.title | upcase }}
{% endtablerow %}
</table>

{{ 3.14 }} {{ 3.14 | floor }} {{ 3.14 | ceil }} {{ 3.14 | round: 1}}

{{ now | date: "%a, %b %d, %y" }}
"""


NAMESPACE = {
    "user": {"name": "Bob", "age": 29},
    "collection": {
        "title": "gifts",
        "products": [
            {"title": "Cool Shirt", "name": "1", "tags": ["foo", "bar"]},
            {"title": "Alien Poster", "name": "2", "tags": ["baz"]},
            {"title": "Batman Poster", "name": "3"},
            {"title": "Bullseye Shirt", "name": "4"},
            {"title": "Another Classic Vinyl", "name": "5"},
            {"title": "Awesome Jeans", "name": "6"},
        ],
    },
    "product": {"title": "Cool Shirt", "name": "shirt", "tags": ["some", "thing"]},
    "customer": {"first_name": "Martina"},
}

GLOBAL_FILTERS = {}


def diff(got, want):
    sys.stdout.writelines(difflib.unified_diff(want, got))


def render(template, expected=None):
    env = Environment()
    env.filters.update(GLOBAL_FILTERS)

    tmpl = env.from_string(template)
    result = tmpl.render(**NAMESPACE)

    if expected:
        lines = result.splitlines()
        diff(lines, expected)

    return result


def main():
    args = sys.argv[1:]
    n_args = len(args)

    expected = None

    if n_args == 0:
        template = TEMPLATE
    elif n_args == 1:
        path, _ = os.path.splitext(args[0])
        with open(args[0], "r") as fd:
            template = fd.read()
        with open(f"{path}.txt", "r") as fd:
            expected = fd.readlines()
    else:
        raise Exception("unexpected extra arguments")

    output = render(template, expected)
    return output


if __name__ == "__main__":
    # main()
    sys.stdout.write(main())
    sys.stdout.write("\n")
