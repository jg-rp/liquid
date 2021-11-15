"""Golden tests cases for testing liquid's `tablerow` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="one row",
        template=r"{% tablerow tag in collection.tags %}{{ tag }}{% endtablerow %}",
        expect=(
            '<tr class="row1">\n'
            '<td class="col1">tag1</td>'
            '<td class="col2">tag2</td>'
            '<td class="col3">tag3</td>'
            '<td class="col4">tag4</td>'
            "</tr>\n"
        ),
        globals={
            "collection": {
                "tags": [
                    "tag1",
                    "tag2",
                    "tag3",
                    "tag4",
                ]
            }
        },
    ),
    Case(
        description="one row with limit",
        template=(
            r"{% tablerow tag in collection.tags limit: 2 %}"
            r"{{ tag }}"
            r"{% endtablerow %}"
        ),
        expect=(
            '<tr class="row1">\n'
            '<td class="col1">tag1</td>'
            '<td class="col2">tag2</td>'
            "</tr>\n"
        ),
        globals={
            "collection": {
                "tags": [
                    "tag1",
                    "tag2",
                    "tag3",
                    "tag4",
                ]
            }
        },
    ),
    Case(
        description="one row with offset",
        template=(
            r"{% tablerow tag in collection.tags offset: 2 %}"
            r"{{ tag }}"
            r"{% endtablerow %}"
        ),
        expect=(
            '<tr class="row1">\n'
            '<td class="col1">tag3</td>'
            '<td class="col2">tag4</td>'
            "</tr>\n"
        ),
        globals={
            "collection": {
                "tags": [
                    "tag1",
                    "tag2",
                    "tag3",
                    "tag4",
                ]
            }
        },
    ),
    Case(
        description="two columns",
        template=(
            r"{% tablerow tag in collection.tags cols:2 %}"
            r"{{ tag }}"
            r"{% endtablerow %}"
        ),
        expect=(
            '<tr class="row1">\n'
            '<td class="col1">tag1</td>'
            '<td class="col2">tag2</td>'
            "</tr>\n"
            '<tr class="row2">'
            '<td class="col1">tag3</td>'
            '<td class="col2">tag4</td>'
            "</tr>\n"
        ),
        globals={
            "collection": {
                "tags": [
                    "tag1",
                    "tag2",
                    "tag3",
                    "tag4",
                ]
            }
        },
    ),
    Case(
        description="two column range",
        template=(
            r"{% tablerow i in (1..4) cols:2 %}"
            r"{{ i }} {{ tablerowloop.col_first }}"
            r"{% endtablerow %}"
        ),
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
        description="two column odd range",
        template=(
            r"{% tablerow i in (1..5) cols:2 %}"
            r"{{ i }} {{ tablerowloop.col_first }}"
            r"{% endtablerow %}"
        ),
        expect=(
            '<tr class="row1">\n'
            '<td class="col1">1 true</td>'
            '<td class="col2">2 false</td>'
            "</tr>\n"
            '<tr class="row2">'
            '<td class="col1">3 true</td>'
            '<td class="col2">4 false</td>'
            "</tr>\n"
            '<tr class="row3">'
            '<td class="col1">5 true</td>'
            "</tr>\n"
        ),
    ),
]
