"""Golden tests cases for testing liquid's built-in `uniq` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="array of strings",
        template=r"{{ a | uniq | join: '#' }}",
        expect="a#b",
        globals={"a": ["a", "b", "b", "a"]},
    ),
    Case(
        description="array of things",
        template=r"{{ a | uniq | join: '#' }}",
        expect="a#b#1",
        globals={"a": ["a", "b", 1, 1]},
    ),
    Case(
        description="empty array",
        template=r"{{ a | uniq | join: '#' }}",
        expect="",
        globals={"a": []},
    ),
    Case(
        description="unhashable items",
        template=r"{{ a | uniq | join: '#' }}",
        expect=r"a#b#{}",
        globals={"a": ["a", "b", [], {}, {}]},
    ),
    Case(
        description="left value is not an array",
        template=r"{{ a | uniq | join: '#' }}",
        expect="123",
        globals={"a": 123},
    ),
    Case(
        description="left value is undefined",
        template=r"{{ nosuchthing | uniq | join: '#' }}",
        expect="",
    ),
    Case(
        description="too many arguments",
        template=r"{{ nosuchthing | uniq: 'foo', 'bar' }}",
        expect="",
        error=True,
    ),
    Case(
        description="array of objects with key property",
        template=(
            r"{% assign x = a | uniq: 'title' %}"
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
                {"title": "foo", "name": "b"},
                {"title": "bar", "name": "c"},
            ]
        },
    ),
    Case(
        description="array of objects with missing key property",
        template=(
            r"{% assign x = a | uniq: 'title' %}"
            r"{% for obj in x %}"
            r"{% for i in obj %}"
            r"({{ i[0] }},{{ i[1] }})"
            r"{% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,foo)(name,a)(title,bar)(name,c)(heading,bar)(name,c)",
        globals={
            "a": [
                {"title": "foo", "name": "a"},
                {"title": "foo", "name": "b"},
                {"title": "bar", "name": "c"},
                {"heading": "bar", "name": "c"},
                {"heading": "baz", "name": "d"},
            ]
        },
    ),
]
