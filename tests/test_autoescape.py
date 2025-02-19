"""HTML escape test cases."""

import operator
from dataclasses import dataclass

import pytest

from liquid import Environment
from liquid import Markup
from liquid import render


@dataclass
class Case:
    """Table driven test case helper."""

    description: str
    template: str
    context: dict[str, object]
    expect: str


class SafeHTMLDrop:
    def __init__(self, some_list: list[object]):
        self.items = some_list

    def __str__(self) -> str:
        return "SafeHTMLDrop"

    def __html__(self) -> str:
        lis = "\n".join(f"<li>{item}</li>" for item in self.items)
        return f"<ul>\n{lis}\n</ul>"


def test_auto_escape_is_disabled_by_default() -> None:
    assert (
        render("{{ name }}", name='<script>alert("XSS!");</script>')
        == '<script>alert("XSS!");</script>'
    )


def test_special_html_method_is_ignored_by_default() -> None:
    assert render("{{ name }}", name=SafeHTMLDrop([1, 2, 3])) == "SafeHTMLDrop"


def test_safe_filter_is_noop_by_default() -> None:
    assert render("{{ '<p>Hello</p>' | safe }}") == "<p>Hello</p>"


TEST_CASES: list[Case] = [
    Case(
        description="script from context",
        template=r"{{ name }}",
        context={"name": '<script>alert("XSS!");</script>'},
        expect="&lt;script&gt;alert(&#34;XSS!&#34;);&lt;/script&gt;",
    ),
    Case(
        description="script from context inside block",
        template=r"{% if true %}{{ name }}{% endif %}",
        context={"name": '<script>alert("XSS!");</script>'},
        expect="&lt;script&gt;alert(&#34;XSS!&#34;);&lt;/script&gt;",
    ),
    Case(
        description="script from context inside block with literal",
        template=r"{% if true %}<br>{{ name }}{% endif %}",
        context={"name": '<script>alert("XSS!");</script>'},
        expect="<br>&lt;script&gt;alert(&#34;XSS!&#34;);&lt;/script&gt;",
    ),
    Case(
        description="capture with HTML literals",
        template=(
            r"{% capture foo %}"
            r'<p class="foo">'
            r"{{ name }}"
            r"</p>"
            r"{% endcapture %}"
            r"{{ foo }}"
        ),
        context={"name": '<script>alert("XSS!");</script>'},
        expect=(
            '<p class="foo">&lt;script&gt;alert(&#34;XSS!&#34;);&lt;/script&gt;</p>'
        ),
    ),
    Case(
        description="drops with __html__ are safe",
        template=(r"{{ foo }}"),
        context={"foo": SafeHTMLDrop([1, 2, 3])},
        expect="<ul>\n<li>1</li>\n<li>2</li>\n<li>3</li>\n</ul>",
    ),
    Case(
        description="filter, upcase",
        template=r"{{ name | upcase }}",
        context={"name": '<script>alert("XSS!");</script>'},
        expect="&lt;SCRIPT&gt;ALERT(&#34;XSS!&#34;);&lt;/SCRIPT&gt;",
    ),
    Case(
        description="filter, upcase safe",
        template=r"{{ name | upcase }}",
        context={"name": Markup('<script>alert("XSS!");</script>')},
        expect='<SCRIPT>ALERT("XSS!");</SCRIPT>',
    ),
    Case(
        description="filter, downcase",
        template=r"{{ name | downcase }}",
        context={"name": '<script>alert("XSS!");</script>'},
        expect="&lt;script&gt;alert(&#34;xss!&#34;);&lt;/script&gt;",
    ),
    Case(
        description="filter, downcase safe",
        template=r"{{ name | downcase }}",
        context={"name": Markup('<script>alert("XSS!");</script>')},
        expect='<script>alert("xss!");</script>',
    ),
    Case(
        description="filter, capitalize",
        template=r"{{ name | capitalize }}",
        context={"name": '<script>alert("XSS!");</script>'},
        expect="&lt;script&gt;alert(&#34;xss!&#34;);&lt;/script&gt;",
    ),
    Case(
        description="filter, capitalize safe",
        template=r"{{ name | capitalize }}",
        context={"name": Markup('<script>alert("XSS!");</script>')},
        expect='<script>alert("xss!");</script>',
    ),
    Case(
        description="filter, append unsafe left value and unsafe argument",
        template=r"{{ some | append: other }}",
        context={"some": "<br>", "other": "<hr>"},
        expect="&lt;br&gt;&lt;hr&gt;",
    ),
    Case(
        description="filter, append safe left value and unsafe argument",
        template=r"{{ some | append: other }}",
        context={"some": Markup("<br>"), "other": "<hr>"},
        expect="<br>&lt;hr&gt;",
    ),
    Case(
        description="filter, append safe left value and safe argument",
        template=r"{{ some | append: other }}",
        context={"some": Markup("<br>"), "other": Markup("<hr>")},
        expect="<br><hr>",
    ),
    Case(
        description="filter, lstrip",
        template=r"{{ some | lstrip }}",
        context={"some": "   <br>"},
        expect="&lt;br&gt;",
    ),
    Case(
        description="filter, lstrip safe",
        template=r"{{ some | lstrip }}",
        context={"some": Markup("   <br>")},
        expect="<br>",
    ),
    Case(
        description="filter, newline to BR",
        template=r"{{ some | newline_to_br }}",
        context={"some": "<em>hello</em>\n<b>goodbye</b>"},
        expect="&lt;em&gt;hello&lt;/em&gt;<br />\n&lt;b&gt;goodbye&lt;/b&gt;",
    ),
    Case(
        description="filter, newline to BR safe",
        template=r"{{ some | newline_to_br }}",
        context={"some": Markup("<em>hello</em>\n<b>goodbye</b>")},
        expect="<em>hello</em><br />\n<b>goodbye</b>",
    ),
    Case(
        description="filter, newline to BR chained filter",
        template=r"{{ some | newline_to_br | upcase }}",
        context={"some": "<em>hello</em>\n<b>goodbye</b>"},
        expect="&LT;EM&GT;HELLO&LT;/EM&GT;<BR />\n&LT;B&GT;GOODBYE&LT;/B&GT;",
    ),
    Case(
        description="filter, newline to BR safe chained filter",
        template=r"{{ some | newline_to_br | upcase }}",
        context={"some": Markup("<em>hello</em>\n<b>goodbye</b>")},
        expect="<EM>HELLO</EM><BR />\n<B>GOODBYE</B>",
    ),
    Case(
        description="filter, prepend unsafe left value and unsafe argument",
        template=r"{{ some | prepend: other }}",
        context={"some": "<br>", "other": "<hr>"},
        expect="&lt;hr&gt;&lt;br&gt;",
    ),
    Case(
        description="filter, prepend safe left value and unsafe argument",
        template=r"{{ some | prepend: other }}",
        context={"some": Markup("<br>"), "other": "<hr>"},
        expect="&lt;hr&gt;<br>",
    ),
    Case(
        description="filter, prepend safe left value and safe argument",
        template=r"{{ some | prepend: other }}",
        context={"some": Markup("<br>"), "other": Markup("<hr>")},
        expect="<hr><br>",
    ),
    Case(
        description="filter, remove unsafe left value and unsafe argument",
        template=r"{{ some | remove: other }}",
        context={"some": "<br><p>hello</p><br>", "other": "<br>"},
        expect="&lt;p&gt;hello&lt;/p&gt;",
    ),
    Case(
        description="filter, remove safe left value and unsafe argument",
        template=r"{{ some | remove: other }}",
        context={"some": Markup("<br><p>hello</p><br>"), "other": "<br>"},
        expect="<p>hello</p>",
    ),
    Case(
        description="filter, remove safe left value and safe argument",
        template=r"{{ some | remove: other }}",
        context={
            "some": Markup("<br><p>hello</p><br>"),
            "other": Markup("<br>"),
        },
        expect="<p>hello</p>",
    ),
    Case(
        description="filter, remove first unsafe left value and unsafe argument",
        template=r"{{ some | remove_first: other }}",
        context={"some": "<br><p>hello</p><br>", "other": "<br>"},
        expect="&lt;p&gt;hello&lt;/p&gt;&lt;br&gt;",
    ),
    Case(
        description="filter, remove first safe left value and unsafe argument",
        template=r"{{ some | remove_first: other }}",
        context={"some": Markup("<br><p>hello</p><br>"), "other": "<br>"},
        expect="<p>hello</p><br>",
    ),
    Case(
        description="filter, remove first safe left value and safe argument",
        template=r"{{ some | remove_first: other }}",
        context={
            "some": Markup("<br><p>hello</p><br>"),
            "other": Markup("<br>"),
        },
        expect="<p>hello</p><br>",
    ),
    Case(
        description="filter, replace unsafe left value and unsafe arguments",
        template=r"{{ some | replace: seq, sub }}",
        context={
            "some": "<br><p>hello</p><br>",
            "seq": "<br>",
            "sub": "<hr>",
        },
        expect="&lt;hr&gt;&lt;p&gt;hello&lt;/p&gt;&lt;hr&gt;",
    ),
    Case(
        description="filter, replace safe left value and unsafe arguments",
        template=r"{{ some | replace: seq, sub }}",
        context={
            "some": Markup("<br><p>hello</p><br>"),
            "seq": "<br>",
            "sub": "<hr>",
        },
        expect="&lt;hr&gt;<p>hello</p>&lt;hr&gt;",
    ),
    Case(
        description="filter, replace safe left value and safe arguments",
        template=r"{{ some | replace: seq, sub }}",
        context={
            "some": Markup("<br><p>hello</p><br>"),
            "seq": Markup("<br>"),
            "sub": Markup("<hr>"),
        },
        expect="<hr><p>hello</p><hr>",
    ),
    Case(
        description="filter, replace first - unsafe left value and unsafe arguments",
        template=r"{{ some | replace_first: seq, sub }}",
        context={
            "some": "<br><p>hello</p><br>",
            "seq": "<br>",
            "sub": "<hr>",
        },
        expect="&lt;hr&gt;&lt;p&gt;hello&lt;/p&gt;&lt;br&gt;",
    ),
    Case(
        description="filter, replace first - safe left value and unsafe arguments",
        template=r"{{ some | replace_first: seq, sub }}",
        context={
            "some": Markup("<br><p>hello</p><br>"),
            "seq": "<br>",
            "sub": "<hr>",
        },
        expect="&lt;hr&gt;<p>hello</p><br>",
    ),
    Case(
        description="filter, replace first - safe left value and safe arguments",
        template=r"{{ some | replace_first: seq, sub }}",
        context={
            "some": Markup("<br><p>hello</p><br>"),
            "seq": Markup("<br>"),
            "sub": Markup("<hr>"),
        },
        expect="<hr><p>hello</p><br>",
    ),
    Case(
        description="filter, slice",
        template=r"{{ some | slice: 4, 12 }}",
        context={"some": "<br><p>hello</p><br>"},
        expect="&lt;p&gt;hello&lt;/p&gt;",
    ),
    Case(
        description="filter, slice safe",
        template=r"{{ some | slice: 4, 12 }}",
        context={"some": Markup("<br><p>hello</p><br>")},
        expect="<p>hello</p>",
    ),
    Case(
        description="filter, split unsafe left value and unsafe argument",
        template=r"{{ some | split: other }}",
        context={"some": "<p>hello</p><br><p>goodbye</p>", "other": "<br>"},
        expect="&lt;p&gt;hello&lt;/p&gt;&lt;p&gt;goodbye&lt;/p&gt;",
    ),
    Case(
        description="filter, split safe left value and unsafe argument",
        template=r"{{ some | split: other }}",
        context={
            "some": Markup("<p>hello</p><br><p>goodbye</p>"),
            "other": "<br>",
        },
        expect="<p>hello</p><p>goodbye</p>",
    ),
    Case(
        description="filter, split safe left value and safe argument",
        template=r"{{ some | split: other }}",
        context={
            "some": Markup("<p>hello</p><br><p>goodbye</p>"),
            "other": Markup("<br>"),
        },
        expect="<p>hello</p><p>goodbye</p>",
    ),
    Case(
        description="filter, strip",
        template=r"{{ some | strip }}",
        context={"some": "\n<p>hello</p>  \n"},
        expect="&lt;p&gt;hello&lt;/p&gt;",
    ),
    Case(
        description="filter, strip safe",
        template=r"{{ some | strip }}",
        context={"some": Markup("\n<p>hello</p>  \n")},
        expect="<p>hello</p>",
    ),
    Case(
        description="filter, right strip",
        template=r"{{ some | rstrip }}",
        context={"some": "\n<p>hello</p>  \n"},
        expect="\n&lt;p&gt;hello&lt;/p&gt;",
    ),
    Case(
        description="filter, right strip safe",
        template=r"{{ some | rstrip }}",
        context={"some": Markup("\n<p>hello</p>  \n")},
        expect="\n<p>hello</p>",
    ),
    Case(
        description="filter, strip html",
        template=r"{{ some | strip_html }}",
        context={"some": "<p>hello</p>"},
        expect="hello",
    ),
    Case(
        description="filter, strip html safe",
        template=r"{{ some | strip_html }}",
        context={"some": Markup("<p>hello</p>")},
        expect="hello",
    ),
    Case(
        description="filter, strip newlines",
        template=r"{{ some | strip_newlines }}",
        context={"some": "\n<p>hello</p>  \n"},
        expect="&lt;p&gt;hello&lt;/p&gt;  ",
    ),
    Case(
        description="filter, strip newlines safe",
        template=r"{{ some | strip_newlines }}",
        context={"some": Markup("\n<p>hello</p>  \n")},
        expect="<p>hello</p>  ",
    ),
    Case(
        description="filter, truncate",
        template=r"{{ some | truncate: 10, '' }}",
        context={"some": "<p>hello</p>"},
        expect="&lt;p&gt;hello&lt;/",
    ),
    Case(
        description="filter, truncate safe",
        template=r"{{ some | truncate: 10, '' }}",
        context={"some": Markup("<p>hello</p>")},
        expect="&lt;p&gt;hello&lt;/",
    ),
    Case(
        description="filter, truncate words",
        template=r"{{ some | truncatewords: 3 }}",
        context={"some": "<em>Ground</em> control to Major Tom."},
        expect="&lt;em&gt;Ground&lt;/em&gt; control to...",
    ),
    Case(
        description="filter, truncate words safe",
        template=r"{{ some | truncatewords: 3 }}",
        context={"some": Markup("<em>Ground</em> control to Major Tom.")},
        expect="&lt;em&gt;Ground&lt;/em&gt; control to...",
    ),
    Case(
        description="filter, URL encode",
        template=r"{{ some | url_encode }}",
        context={"some": "<p>hello</p>"},
        expect=r"%3Cp%3Ehello%3C%2Fp%3E",
    ),
    Case(
        description="filter, URL encode safe",
        template=r"{{ some | url_encode }}",
        context={"some": Markup("<p>hello</p>")},
        expect=r"%3Cp%3Ehello%3C%2Fp%3E",
    ),
    Case(
        description="filter, URL decode",
        template=r"{{ some | url_decode }}",
        context={"some": r"%3Cp%3Ehello%3C%2Fp%3E"},
        expect="&lt;p&gt;hello&lt;/p&gt;",
    ),
    Case(
        description="filter, URL decode safe",
        template=r"{{ some | url_decode }}",
        context={"some": Markup(r"%3Cp%3Ehello%3C%2Fp%3E")},
        expect="&lt;p&gt;hello&lt;/p&gt;",
    ),
    Case(
        description="filter, liquid escape",
        template=r"{{ some | escape }}",
        context={"some": "<p>hello</p>"},
        expect="&lt;p&gt;hello&lt;/p&gt;",
    ),
    Case(
        description="filter, liquid escape markup",
        template=r"{{ some | escape }}",
        context={"some": Markup("<p>hello</p>")},
        expect="&lt;p&gt;hello&lt;/p&gt;",
    ),
    Case(
        description="filter, escape once",
        template=r"{{ some | escape_once }}",
        context={"some": "&lt;p&gt;test&lt;/p&gt;<p>test</p>"},
        expect="&lt;p&gt;test&lt;/p&gt;&lt;p&gt;test&lt;/p&gt;",
    ),
    Case(
        description="filter, escape once markup",
        template=r"{{ some | escape_once }}",
        context={"some": Markup("&lt;p&gt;test&lt;/p&gt;<p>test</p>")},
        expect="&lt;p&gt;test&lt;/p&gt;&lt;p&gt;test&lt;/p&gt;",
    ),
    Case(
        description="filter, escape __html__",
        template=r"{{ some | escape }}",
        context={"some": SafeHTMLDrop([1, 2, 3])},
        expect="SafeHTMLDrop",
    ),
    Case(
        description="filter, join unsafe iterable and default separator",
        template=r"{{ foo | join }}",
        context={"foo": ["<p>hello</p>", "<p>goodbye</p>"]},
        expect="&lt;p&gt;hello&lt;/p&gt; &lt;p&gt;goodbye&lt;/p&gt;",
    ),
    Case(
        description="filter, join unsafe iterable and unsafe separator",
        template=r"{{ foo | join: bar }}",
        context={"foo": ["<p>hello</p>", "<p>goodbye</p>"], "bar": "<hr>"},
        expect="&lt;p&gt;hello&lt;/p&gt;&lt;hr&gt;&lt;p&gt;goodbye&lt;/p&gt;",
    ),
    Case(
        description="filter, join safe iterable and default separator",
        template=r"{{ foo | join }}",
        context={"foo": [Markup("<p>hello</p>"), Markup("<p>goodbye</p>")]},
        expect="<p>hello</p> <p>goodbye</p>",
    ),
    Case(
        description="filter, join safe iterable and unsafe separator",
        template=r"{{ foo | join: bar }}",
        context={
            "foo": [Markup("<p>hello</p>"), Markup("<p>goodbye</p>")],
            "bar": "<hr>",
        },
        expect="&lt;p&gt;hello&lt;/p&gt;&lt;hr&gt;&lt;p&gt;goodbye&lt;/p&gt;",
    ),
    Case(
        description="filter, join safe iterable and safe separator",
        template=r"{{ foo | join: bar }}",
        context={
            "foo": [Markup("<p>hello</p>"), Markup("<p>goodbye</p>")],
            "bar": Markup("<hr>"),
        },
        expect="<p>hello</p><hr><p>goodbye</p>",
    ),
    Case(
        description="filter, join mixed iterable and safe separator",
        template=r"{{ foo | join: bar }}",
        context={
            "foo": [Markup("<p>hello</p>"), "<p>goodbye</p>"],
            "bar": Markup("<hr>"),
        },
        expect="<p>hello</p><hr>&lt;p&gt;goodbye&lt;/p&gt;",
    ),
    Case(
        description="filter, date",
        template=r"{{ foo | date: bar }}",
        context={"foo": "March 14, 2016", "bar": r"%b %d, %y<hr>"},
        expect="Mar 14, 16&lt;hr&gt;",
    ),
    Case(
        description="filter, date with literal format string",
        template=r"{{ foo | date: '%b %d, %y<br>' }}",
        context={"foo": "March 14, 2016"},
        expect="Mar 14, 16<br>",
    ),
    Case(
        description="filter, date with safe format string from context",
        template=r"{{ foo | date: bar }}",
        context={"foo": "March 14, 2016", "bar": Markup(r"%b %d, %y<br>")},
        expect="Mar 14, 16<br>",
    ),
    Case(
        description="filter, safe from unsafe",
        template=r"<p>Hello, {{ you | safe }}</p>",
        context={"you": "<em>World!</em>"},
        expect="<p>Hello, <em>World!</em></p>",
    ),
    Case(
        description="filter, safe from safe",
        template=r"<p>Hello, {{ you | safe }}</p>",
        context={"you": Markup("<em>World!</em>")},
        expect="<p>Hello, <em>World!</em></p>",
    ),
    Case(
        description="tablerow, no markup",
        template=(
            r"{% tablerow i in (1..4) cols:2 %}"
            r"{{ i }} {{ tablerowloop.col_first }}"
            r"{% endtablerow %}"
        ),
        context={},
        expect=(
            '<tr class="row1">\n'
            '<td class="col1">1 true</td>'
            '<td class="col2">2 false</td>'
            "</tr>\n"
            '<tr class="row2">'
            '<td class="col1">3 true</td>'
            '<td class="col2">4 false</td>'
            "</tr>\n"
        ),
    ),
    Case(
        description="tablerow, markup in loop block",
        template=(
            r"{% tablerow i in (1..4) cols:2 %}"
            r"<b>{{ i }}</b> {{ tablerowloop.col_first }}"
            r"{% endtablerow %}"
        ),
        context={},
        expect=(
            '<tr class="row1">\n'
            '<td class="col1"><b>1</b> true</td>'
            '<td class="col2"><b>2</b> false</td>'
            "</tr>\n"
            '<tr class="row2">'
            '<td class="col1"><b>3</b> true</td>'
            '<td class="col2"><b>4</b> false</td>'
            "</tr>\n"
        ),
    ),
    Case(
        description="tablerow, unsafe markup from iterable",
        template=(
            r"{% tablerow tag in collection.tags %}"
            r"{{ tag }}"
            r"{% endtablerow %}"
        ),
        expect=(
            '<tr class="row1">\n'
            '<td class="col1">&lt;b&gt;tag1&lt;/b&gt;</td>'
            '<td class="col2">tag2</td>'
            '<td class="col3">tag3</td>'
            '<td class="col4">tag4</td>'
            "</tr>\n"
        ),
        context={
            "collection": {
                "tags": [
                    "<b>tag1</b>",
                    "tag2",
                    "tag3",
                    "tag4",
                ]
            }
        },
    ),
    Case(
        description="tablerow, safe markup from iterable",
        template=(
            r"{% tablerow tag in collection.tags %}"
            r"{{ tag }}"
            r"{% endtablerow %}"
        ),
        expect=(
            '<tr class="row1">\n'
            '<td class="col1"><b>tag1</b></td>'
            '<td class="col2">tag2</td>'
            '<td class="col3">tag3</td>'
            '<td class="col4">tag4</td>'
            "</tr>\n"
        ),
        context={
            "collection": {
                "tags": [
                    Markup("<b>tag1</b>"),
                    "tag2",
                    "tag3",
                    "tag4",
                ]
            }
        },
    ),
    Case(
        description="liquid tag, echo markup from context",
        template="\n".join(
            [
                r"{% liquid ",
                r"    echo foo",
                r"%}",
            ]
        ),
        context={"foo": "<em>hello</em>"},
        expect="&lt;em&gt;hello&lt;/em&gt;",
    ),
    Case(
        description="liquid tag, echo unsafe markup from string literal",
        template="\n".join(
            [
                r"{% liquid ",
                r"    echo '<em>hello</em>'",
                r"%}",
            ]
        ),
        context={},
        expect="<em>hello</em>",
    ),
    Case(
        description="liquid tag, echo safe markup from context",
        template="\n".join(
            [
                r"{% liquid ",
                r"    echo foo",
                r"%}",
            ]
        ),
        context={"foo": Markup("<em>hello</em>")},
        expect="<em>hello</em>",
    ),
]

ENV = Environment(autoescape=True)


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_auto_escape(case: Case) -> None:
    assert ENV.from_string(case.template).render(**case.context) == case.expect
