"""Golden tests cases for testing liquid's built-in `sort_natural` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="array of strings",
        template=r"{{ a | sort_natural | join: '#' }}",
        expect="a#A#b#B#C",
        globals={"a": ["b", "a", "C", "B", "A"]},
    ),
    Case(
        description="array of strings with a nul",
        template=(
            r"{% assign x = a | sort_natural %}"
            r"{% for i in x %}"
            r"{{ i }}"
            r"{% unless forloop.last %}#{% endunless %}"
            r"{% endfor %}"
        ),
        expect="a#A#b#B#C#",
        globals={"a": ["b", "a", None, "C", "B", "A"]},
    ),
    Case(
        description="array of objects with a key",
        template=(
            r"{% assign x = a | sort_natural: 'title' %}"
            r"{% for obj in x %}"
            r"{% for i in obj %}"
            r"({{ i[0] }},{{ i[1] }})"
            r"{% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,bar)(title,Baz)(title,foo)",
        globals={"a": [{"title": "foo"}, {"title": "bar"}, {"title": "Baz"}]},
    ),
    Case(
        description="array of objects with a key gets stringified",
        template=(
            r"{% assign x = a | sort_natural: 'title' %}"
            r"{% for obj in x %}"
            r"{% for i in obj %}"
            r"({{ i[0] }},{{ i[1] }})"
            r"{% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,1111)(title,87)(title,9)",
        globals={"a": [{"title": 9}, {"title": 1111}, {"title": 87}]},
    ),
    Case(
        description="array of objects with a missing key",
        template=(
            r"{% assign x = a | sort_natural: 'title' %}"
            r"{% for obj in x %}"
            r"{% for i in obj %}"
            r"({{ i[0] }},{{ i[1] }})"
            r"{% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,bar)(title,foo)(heading,Baz)",
        globals={"a": [{"title": "foo"}, {"title": "bar"}, {"heading": "Baz"}]},
    ),
    Case(
        description="argument is undefined",
        template=(
            r"{% assign x = a | sort_natural: nosuchthing %}"
            r"{% for obj in x %}"
            r"{% for i in obj %}"
            r"({{ i[0] }},{{ i[1] }})"
            r"{% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,bar)(title,Baz)(title,foo)",
        globals={"a": [{"title": "foo"}, {"title": "bar"}, {"title": "Baz"}]},
    ),
    Case(
        description="empty array",
        template=(
            r"{% assign x = a | sort_natural %}"
            r"{% for i in x %}"
            r"{{ i }}"
            r"{% unless forloop.last %}#{% endunless %}"
            r"{% endfor %}"
        ),
        expect="",
        globals={"a": []},
    ),
    Case(
        description="left value is not an array",
        template=r"{{ a | sort_natural }}",
        expect="123",
        globals={"a": 123},
    ),
    Case(
        description="left value is undefined",
        template=r"{{ nosuchthing | sort_natural }}",
        expect="",
    ),
    Case(
        description="incompatible types",
        template=r"{{ a | sort_natural }}",
        expect="14{}",
        globals={"a": [{}, 1, "4"]},
    ),
    Case(
        description="property, array contains primitive",
        template="\n".join(
            [
                "{% assign sorted = a | sort_natural: 'foo' -%}",
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
                {"foo": "b"},
                {"foo": "a"},
                {"foo": "C"},
                {"foo": "B"},
                {"foo": "A"},
                False,
            ]
        },
    ),
    Case(
        description="property, array contains array",
        template="\n".join(
            [
                "{% assign sorted = a | sort_natural: 'foo' -%}",
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
                {"foo": "b"},
                {"foo": "a"},
                {"foo": "C"},
                {"foo": "B"},
                {"foo": "A"},
                [42, 7],
            ]
        },
    ),
    Case(
        description="property with a dot, string match",
        template="\n".join(
            [
                "{% assign sorted = a | sort_natural: 'foo.bar' -%}",
                "{% for item in sorted -%}",
                "{% for pair in item -%}",
                "({{ pair[0] }}, {{ pair[1] }})",
                "{% endfor -%}",
                "{% endfor %}",
            ]
        ),
        expect="".join(
            [
                "(foo.bar, a)\n",
                "(foo.bar, A)\n",
                "(foo.bar, b)\n",
                "(foo.bar, B)\n",
                "(foo.bar, C)\n",
            ]
        ),
        globals={
            "a": [
                {"foo.bar": "b"},
                {"foo.bar": "a"},
                {"foo.bar": "C"},
                {"foo.bar": "B"},
                {"foo.bar": "A"},
            ]
        },
    ),
    Case(
        description="property with a dot, path match",
        template="\n".join(
            [
                "{% assign sorted = a | sort_natural: 'foo.bar' -%}",
                "{% for item in sorted -%}",
                "{% for pair in item.foo -%}",
                "({{ pair[0] }}, {{ pair[1] }})",
                "{% endfor -%}",
                "{% endfor %}",
            ]
        ),
        expect="".join(
            [
                "(bar, a)\n",
                "(bar, A)\n",
                "(bar, b)\n",
                "(bar, B)\n",
                "(bar, C)\n",
            ]
        ),
        globals={
            "a": [
                {"foo": {"bar": "b"}},
                {"foo": {"bar": "a"}},
                {"foo": {"bar": "C"}},
                {"foo": {"bar": "B"}},
                {"foo": {"bar": "A"}},
            ]
        },
    ),
    Case(
        description="property with a dot, string and path match",
        template="\n".join(
            [
                "{% assign sorted = a | sort_natural: 'foo.bar' -%}",
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
                "(foo,a)\n",
                "(foo,A)\n",
                "(foo.bar,b)\n",
                "(foo,B)\n",
                "(foo,C)\n",
            ]
        ),
        globals={
            "a": [
                {"foo.bar": "b"},
                {"foo": {"bar": "a"}},
                {"foo": {"bar": "C"}},
                {"foo": {"bar": "B"}},
                {"foo": {"bar": "A"}},
            ]
        },
    ),
]
