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
]
