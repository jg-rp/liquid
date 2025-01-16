"""Golden tests cases for testing liquid's built-in `compact` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="array with a nil",
        template=r"{{ a | compact | join: '#' }}",
        expect="b#a#A",
        globals={"a": ["b", "a", None, "A"]},
    ),
    Case(
        description="empty array",
        template=r"{{ a | compact | join: '#' }}",
        expect="",
        globals={"a": []},
    ),
    Case(
        description="too many arguments",
        template=r"{{ a | compact: 'foo', 'bar' }}",
        expect="",
        error=True,
    ),
    Case(
        description="left value is not an array",
        template=r"{{ a | compact | first }}",
        expect="123",
        globals={"a": 123},
    ),
    Case(
        description="left value is undefined",
        template=r"{{ nosuchthing | compact }}",
        expect="",
    ),
    Case(
        description="property, array of objects",
        template=(
            r"{% assign x = a | compact: 'title' %}"
            r"{% for obj in x %}"
            r"{% for i in obj %}"
            r"({{ i[0] }},{{ i[1] }})"
            r"{% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,foo)(name,a)(title,bar)(name,c)",
        globals={
            "a": [
                {"title": "foo", "name": "a"},
                {"title": None, "name": "b"},
                {"title": "bar", "name": "c"},
            ]
        },
    ),
    Case(
        description="dotted property, string match",
        template=(
            r"{% assign x = a | compact: 'user.title' %}"
            r"{% for obj in x %}"
            r"{% for i in obj %}"
            r"({{ i[0] }},{{ i[1] }})"
            r"{% endfor %}"
            r"{% endfor %}"
        ),
        expect="(user.title,foo)(name,a)(user.title,bar)(name,c)",
        globals={
            "a": [
                {"user.title": "foo", "name": "a"},
                {"user.title": None, "name": "b"},
                {"user.title": "bar", "name": "c"},
            ]
        },
    ),
    Case(
        description="dotted property, path match",
        template=(
            r"{% assign x = a | compact: 'user.title' %}"
            r"{% for obj in x %}"
            r"{% for i in obj %}"
            r"({{ i[0] }},{{ i[1].title }},{{ i[1].name }})"
            r"{% endfor %}"
            r"{% endfor %}"
        ),
        expect="(user,foo,a)(user,bar,c)",
        globals={
            "a": [
                {"user": {"title": "foo", "name": "a"}},
                {"user": {"title": None, "name": "b"}},
                {"user": {"title": "bar", "name": "c"}},
            ]
        },
    ),
]
