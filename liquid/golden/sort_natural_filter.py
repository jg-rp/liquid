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
]
