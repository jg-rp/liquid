"""Golden tests cases for testing liquid's built-in `sort` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="array of strings",
        template=r"{{ a | sort | join: '#' }}",
        expect="A#B#C#a#b",
        globals={"a": ["b", "a", "C", "B", "A"]},
    ),
    Case(
        description="array of objects",
        template=(
            r"{% assign x = a | sort: 'title' %}"
            r"{% for obj in x %}"
            r"{% for i in obj %}"
            r"({{ i[0] }},{{ i[1] }})"
            r"{% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,Baz)(title,bar)(title,foo)",
        globals={"a": [{"title": "foo"}, {"title": "Baz"}, {"title": "bar"}]},
    ),
    Case(
        description="array of objects with missing key",
        template=(
            r"{% assign x = a | sort: 'title' %}"
            r"{% for obj in x %}"
            r"{% for i in obj %}"
            r"({{ i[0] }},{{ i[1] }})"
            r"{% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,bar)(title,foo)(heading,Baz)",
        globals={"a": [{"title": "foo"}, {"heading": "Baz"}, {"title": "bar"}]},
    ),
    Case(
        description="empty array",
        template=r"{{ a | sort | join: '#' }}",
        expect="",
        globals={"a": []},
    ),
    Case(
        description="too many arguments",
        template=r"{{ a | sort: 'title', 'foo' | join: '#' }}",
        expect="",
        globals={"a": ["b", "a"]},
        error=True,
    ),
    Case(
        description="left value is not an array",
        template=r"{{ a | sort | join: '#' }}",
        expect="123",
        globals={"a": 123},
    ),
    Case(
        description="left value is undefined",
        template=r"{{ nosuchthing | sort | join: '#' }}",
        expect="",
    ),
    Case(
        description="argument is undefined",
        template=r"{{ a | sort: nosuchthing | join: '#' }}",
        expect="a#b",
        globals={"a": ["b", "a"]},
    ),
    Case(
        description="sort a string",
        template=r"{{ 'BzAa4' | sort | join: '#' }}",
        expect="BzAa4",
    ),
    Case(
        description="array of integers",
        template=r"{{ a | sort | join: '#' }}",
        expect="1#3#30#1000",
        globals={"a": [1, 1000, 3, 30]},
    ),
    Case(
        description="incompatible types",
        template=r"{{ a | sort }}",
        expect="",
        globals={"a": [[], {}, 1, "4"]},
        error=True,
    ),
    Case(
        description="property, array contains primitive",
        template="\n".join(
            [
                "{% assign sorted = a | sort: 'foo' -%}",
                "{% for item in sorted -%}",
                "{% for pair in item -%}",
                "({{ pair[0] }}, {{ pair[1] }})",
                "{% endfor -%}",
                "{% endfor %}",
            ]
        ),
        expect="",
        globals={
            "a": [
                {"foo": 4},
                {"foo": 2},
                {"foo": 9},
                False,
            ]
        },
    ),
    Case(
        description="property, array contains array",
        template="\n".join(
            [
                "{% assign sorted = a | sort: 'foo' -%}",
                "{% for item in sorted -%}",
                "{% for pair in item -%}",
                "({{ pair[0] }}, {{ pair[1] }})",
                "{% endfor -%}",
                "{% endfor %}",
            ]
        ),
        expect="",
        globals={
            "a": [
                {"foo": 4},
                {"foo": 2},
                {"foo": 9},
                [42, 7],
            ]
        },
    ),
    Case(
        description="property with a dot, string match",
        template="\n".join(
            [
                "{% assign sorted = a | sort: 'foo.bar' -%}",
                "{% for item in sorted -%}",
                "{% for pair in item -%}",
                "({{ pair[0] }}, {{ pair[1] }})",
                "{% endfor -%}",
                "{% endfor %}",
            ]
        ),
        expect="".join(
            [
                "(foo.bar, -1)\n",
                "(foo.bar, 2)\n",
                "(foo.bar, 4)\n",
                "(foo.bar, 9)\n",
            ]
        ),
        globals={
            "a": [
                {"foo.bar": 4},
                {"foo.bar": 2},
                {"foo.bar": 9},
                {"foo.bar": -1},
            ]
        },
    ),
    Case(
        description="property with a dot, path match",
        template="\n".join(
            [
                "{% assign sorted = a | sort: 'foo.bar' -%}",
                "{% for item in sorted -%}",
                "{% for pair in item.foo -%}",
                "({{ pair[0] }}, {{ pair[1] }})",
                "{% endfor -%}",
                "{% endfor %}",
            ]
        ),
        expect="".join(
            [
                "(bar, -1)\n",
                "(bar, 2)\n",
                "(bar, 4)\n",
                "(bar, 9)\n",
            ]
        ),
        globals={
            "a": [
                {"foo": {"bar": 4}},
                {"foo": {"bar": 2}},
                {"foo": {"bar": 9}},
                {"foo": {"bar": -1}},
            ]
        },
    ),
    Case(
        description="property with a dot, string and path match",
        template="\n".join(
            [
                "{% assign sorted = a | sort: 'foo.bar' -%}",
                "{% for item in sorted -%}",
                "{% for pair in item -%}",
                "({{ pair[0] }}, ",
                "{%- if pair[1].bar -%}",
                "{{ pair[1].bar }}{%else%}{{ pair[1] -}}",
                "{% endif %})",
                "{% endfor -%}",
                "{% endfor %}",
            ]
        ),
        expect="".join(
            [
                "(foo,-1)\n",
                "(foo,2)\n",
                "(foo.bar,4)\n",
                "(foo,9)\n",
            ]
        ),
        globals={
            "a": [
                {"foo.bar": 4},
                {"foo": {"bar": 2}},
                {"foo": {"bar": 9}},
                {"foo": {"bar": -1}},
            ]
        },
    ),
    Case(
        description="property with a bracketed index, silently does not sort",
        template="\n".join(
            [
                "{% assign sorted = a | sort: 'foo[1]' -%}",
                "{% for item in sorted -%}",
                "{% for pair in item -%}",
                "({{ pair[0] }}, {{ pair[1] | join: '#' }})",
                "{% endfor -%}",
                "{% endfor %}",
            ]
        ),
        expect="".join(
            [
                "(foo, 3#4#5)\n",
                "(foo, 3#2#5)\n",
                "(foo, 3#9#5)\n",
                "(foo, 3#-1#5)\n",
            ]
        ),
        globals={
            "a": [
                {"foo": [3, 4, 5]},
                {"foo": [3, 2, 5]},
                {"foo": [3, 9, 5]},
                {"foo": [3, -1, 5]},
            ]
        },
    ),
]
