"""Test cases for the standard `reject` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="array of strings, default value",
        template=(
            r"{% assign b = a | reject: 'c' %}"
            r"{% for obj in b %}"
            r"{{ obj }}, "
            r"{% endfor %}"
        ),
        expect="x, y, ",
        globals={"a": ["x", "y", "cat"]},
    ),
    Case(
        description="array containing null, default value",
        template=r"{{ a | reject: 'c' }}",
        expect="",
        globals={"a": ["x", "y", "cat", None]},
    ),
    Case(
        description="array containing an int, default value",
        template=r"{{ a | reject: 'c' }}",
        expect="",
        error=True,
        globals={"a": ["x", "y", "cat", 1]},
    ),
    Case(
        description="array of hashes, default value",
        template=(
            r"{% assign b = a | reject: 'title' %}"
            r"{% for obj in b %}"
            r"{% for itm in obj %}({{ itm[0] }},{{ itm[1] }}), {% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,false), (title,), (heading,baz), ",
        globals={
            "a": [
                {"title": "foo"},
                {"title": False},
                {"title": None},
                {"heading": "baz"},
            ]
        },
    ),
    Case(
        description="array of hashes, explicit nil",
        template=(
            r"{% assign b = a | reject: 'title', nil %}"
            r"{% for obj in b %}"
            r"{% for itm in obj %}({{ itm[0] }},{{ itm[1] }}), {% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,false), (title,), (heading,baz), ",
        globals={
            "a": [
                {"title": "foo"},
                {"title": False},
                {"title": None},
                {"heading": "baz"},
            ]
        },
    ),
    Case(
        description="array of hashes, explicit false",
        template=(
            r"{% assign b = a | reject: 'title', false %}"
            r"{% for obj in b %}"
            r"{% for itm in obj %}({{ itm[0] }},{{ itm[1] }}), {% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,bar), (title,), (heading,baz), ",
        globals={
            "a": [
                {"title": False},
                {"title": "bar"},
                {"title": None},
                {"heading": "baz"},
            ]
        },
    ),
    Case(
        description="array of hashes, explicit true",
        template=(
            r"{% assign b = a | reject: 'title', true %}"
            r"{% for obj in b %}"
            r"{% for itm in obj %}({{ itm[0] }},{{ itm[1] }}), {% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,bar), (title,), ",
        globals={"a": [{"title": True}, {"title": "bar"}, {"title": None}]},
    ),
    Case(
        description="array of hashes, string value",
        template=(
            r"{% assign b = a | reject: 'title', 'bar' %}"
            r"{% for obj in b %}"
            r"{% for itm in obj %}({{ itm[0] }},{{ itm[1] }}), {% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,foo), (title,), (heading,baz), ",
        globals={
            "a": [
                {"title": "foo"},
                {"title": "bar"},
                {"title": None},
                {"heading": "baz"},
            ]
        },
    ),
    Case(
        description="array of hashes, missing property",
        template=(
            r"{% assign b = a | reject: 'title', 'bar' %}"
            r"{% for obj in b %}"
            r"{% for itm in obj %}({{ itm[0] }},{{ itm[1] }}), {% endfor %}"
            r"{% endfor %}"
        ),
        expect="(heading,foo), (title,), ",
        globals={"a": [{"heading": "foo"}, {"title": "bar"}, {"title": None}]},
    ),
    Case(
        description="missing argument",
        template=(
            r"{% assign b = a | reject %}"
            r"{% for obj in b %}{{ obj }}, {% endfor %}"
        ),
        expect="",
        error=True,
        globals={"a": ["x", "y", "cat"]},
    ),
    Case(
        description="too many arguments",
        template=(
            r"{% assign b = a | reject: 'x', 'y', 'z' %}"
            r"{% for obj in b %}{{ obj }}, {% endfor %}"
        ),
        expect="",
        error=True,
    ),
    Case(
        description="input is undefined",
        template=(
            r"{% assign b = nosuchthing | reject: 'c' %}"
            r"{% for obj in b %}{{ obj }}, {% endfor %}"
        ),
        expect="",
    ),
    Case(
        description="first argument is undefined",
        template=(
            r"{% assign b = a | reject: nosuchthing %}"
            r"{% for obj in b %}{{ obj }}, {% endfor %}"
        ),
        expect="",
        globals={"a": ["x", "y", "cat"]},
    ),
    Case(
        description="second argument is undefined",
        template=(
            r"{% assign b = a | reject: 'title', nosuchthing %}"
            r"{% for obj in b %}"
            r"{% for itm in obj %}({{ itm[0] }},{{ itm[1] }}), {% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,), ",
        globals={"a": [{"title": "foo"}, {"title": "bar"}, {"title": None}]},
    ),
    Case(
        description="input is a hash, default value",
        template=(
            r"{% assign b = h | reject: 'bar' %}"
            r"{% for obj in b %}{{ obj }}, {% endfor %}"
        ),
        expect="",
        globals={"h": {"foo": 1, "bar": 2, "baz": 3}},
    ),
    Case(
        description="input is a hash, default value, no match",
        template=(
            r"{% assign b = h | reject: 'barbar' %}"
            r"{% for obj in b %}"
            r"{% for itm in obj %}({{ itm[0] }},{{ itm[1] }}), {% endfor %}"
            r"{% endfor %}"
        ),
        expect="(foo,1), (bar,2), (baz,3), ",
        globals={"h": {"foo": 1, "bar": 2, "baz": 3}},
    ),
    Case(
        description="input is a hash, default value, nil match",
        template=(
            r"{% assign b = h | reject: 'bar' %}"
            r"{% for obj in b %}"
            r"{% for itm in obj %}({{ itm[0] }},{{ itm[1] }}), {% endfor %}"
            r"{% endfor %}"
        ),
        expect="(foo,1), (bar,), (baz,3), ",
        globals={"h": {"foo": 1, "bar": None, "baz": 3}},
    ),
    Case(
        description="input is a hash, explicit nil match",
        template=(
            r"{% assign b = h | reject: 'bar', nil %}"
            r"{% for obj in b %}"
            r"{% for itm in obj %}({{ itm[0] }},{{ itm[1] }}), {% endfor %}"
            r"{% endfor %}"
        ),
        expect="(foo,1), (bar,), (baz,3), ",
        globals={"h": {"foo": 1, "bar": None, "baz": 3}},
    ),
    Case(
        description="input is a hash, int value, no match",
        template=(
            r"{% assign b = h | reject: 'bar', 1 %}"
            r"{% for obj in b %}"
            r"{% for itm in obj %}({{ itm[0] }},{{ itm[1] }}), {% endfor %}"
            r"{% endfor %}"
        ),
        expect="(foo,1), (bar,2), (baz,3), ",
        globals={"h": {"foo": 1, "bar": 2, "baz": 3}},
    ),
    Case(
        description="input is a hash, int value, match",
        template=(
            r"{% assign b = h | reject: 'bar', 2 %}"
            r"{% for obj in b %}"
            r"{% for itm in obj %}({{ itm[0] }},{{ itm[1] }}), {% endfor %}"
            r"{% endfor %}"
        ),
        expect="",
        globals={"h": {"foo": 1, "bar": 2, "baz": 3}},
    ),
    Case(
        description="nested array of hashes gets flattened",
        template=(
            r"{% assign b = a | reject: 'title', 'bar' %}"
            r"{% for obj in b %}"
            r"{% for itm in obj %}({{ itm[0] }},{{ itm[1] }}), {% endfor %}"
            r"{% endfor %}"
        ),
        expect="(title,foo), (title,), ",
        globals={"a": [[{"title": "foo"}, {"title": "bar"}], [[{"title": None}]]]},
    ),
    Case(
        description="string input becomes a single element array, substring match",
        template=(
            r"{% assign b = s | reject: 'oo' %}"
            r"{% for obj in b %}"
            r"{{ obj }}, "
            r"{% endfor %}"
        ),
        expect="",
        globals={"s": "foobar"},
    ),
    Case(
        description="string input becomes a single element array, no match",
        template=(
            r"{% assign b = s | reject: 'xx' %}"
            r"{% for obj in b %}"
            r"{{ obj }}, "
            r"{% endfor %}"
        ),
        expect="foobar, ",
        globals={"s": "foobar"},
    ),
]
