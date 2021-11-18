"""Golden tests cases for testing liquid's built-in `where` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="array of hashes",
        template=(
            r"{% assign x = a | where: 'title' %}"
            r"{% for obj in x %}"
            r"{% for i in obj %}"
            r"({{ i[0] }},{{ i[1] }})"
            r"{% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,foo)(title,bar)",
        globals={"a": [{"title": "foo"}, {"title": "bar"}, {"title": None}]},
    ),
    Case(
        description="array of hashes with equality test",
        template=(
            r"{% assign x = a | where: 'title', 'bar' %}"
            r"{% for obj in x %}"
            r"{% for i in obj %}"
            r"({{ i[0] }},{{ i[1] }})"
            r"{% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,bar)",
        globals={"a": [{"title": "foo"}, {"title": "bar"}, {"title": None}]},
    ),
    Case(
        description="array of hashes with a missing key",
        template=(
            r"{% assign x = a | where: 'title', 'bar' %}"
            r"{% for obj in x %}"
            r"{% for i in obj %}"
            r"({{ i[0] }},{{ i[1] }})"
            r"{% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,bar)",
        globals={"a": [{"heading": "foo"}, {"title": "bar"}, {"title": None}]},
    ),
    Case(
        description="left value is not an array",
        template=r"{{ a | where: 'title' }}",
        expect="",
        globals={"a": 123},
        error=True,
    ),
    Case(
        description="missing argument",
        template=r"{{ a | where }}",
        expect="",
        globals={"a": [{"title": "foo"}, {"title": "bar"}, {"title": None}]},
        error=True,
    ),
    Case(
        description="too many arguments",
        template=r"{{ a | where: 'title', 'foo', 'bar' }}",
        expect="",
        globals={"a": [{"title": "foo"}, {"title": "bar"}, {"title": None}]},
        error=True,
    ),
    Case(
        description="left value is undefined",
        template=r"{{ nosuchthing | where: 'title' }}",
        expect="",
    ),
    Case(
        description="first argument is undefined",
        template=r"{{ a | where: nosuchthing }}",
        expect="",
        globals={"a": [{"title": "foo"}, {"title": "bar"}, {"title": None}]},
    ),
    Case(
        description="both arguments are undefined",
        template=r"{{ a | where: nosuchthing, nothing }}",
        expect="",
        globals={"a": [{"title": "foo"}, {"title": "bar"}, {"title": None}]},
    ),
]
