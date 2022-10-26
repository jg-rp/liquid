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
    Case(
        description="two column odd range row numbers",
        template=(
            r"{% tablerow i in (1..5) cols:2 %}"
            r"{{ i }} {{ tablerowloop.row }}"
            r"{% endtablerow %}"
        ),
        expect=(
            '<tr class="row1">\n'
            '<td class="col1">1 1</td>'
            '<td class="col2">2 1</td>'
            "</tr>\n"
            '<tr class="row2">'
            '<td class="col1">3 2</td>'
            '<td class="col2">4 2</td>'
            "</tr>\n"
            '<tr class="row3">'
            '<td class="col1">5 3</td>'
            "</tr>\n"
        ),
    ),
    Case(
        description="no cols param",
        template=(
            "\n".join(
                [
                    "{% tablerow i in (1..2) %}",
                    "col: {{ tablerowloop.col }}",
                    "col0: {{ tablerowloop.col0 }}",
                    "col_first: {{ tablerowloop.col_first }}",
                    "col_last: {{ tablerowloop.col_last }}",
                    "first: {{ tablerowloop.first }}",
                    "index: {{ tablerowloop.index }}",
                    "index0: {{ tablerowloop.index0 }}",
                    "last: {{ tablerowloop.last }}",
                    "length: {{ tablerowloop.length }}",
                    "rindex: {{ tablerowloop.rindex }}",
                    "rindex0: {{ tablerowloop.rindex0 }}",
                    "row: {{ tablerowloop.row }}",
                    "{% endtablerow %}",
                ]
            )
        ),
        expect=(
            "\n".join(
                [
                    '<tr class="row1">',
                    '<td class="col1">',
                    "col: 1",
                    "col0: 0",
                    "col_first: true",
                    "col_last: false",
                    "first: true",
                    "index: 1",
                    "index0: 0",
                    "last: false",
                    "length: 2",
                    "rindex: 2",
                    "rindex0: 1",
                    "row: 1",
                    '</td><td class="col2">',
                    "col: 2",
                    "col0: 1",
                    "col_first: false",
                    "col_last: true",
                    "first: false",
                    "index: 2",
                    "index0: 1",
                    "last: true",
                    "length: 2",
                    "rindex: 1",
                    "rindex0: 0",
                    "row: 1",
                    "</td></tr>\n",
                ]
            )
        ),
    ),
    Case(
        description="cols is a string",
        template=(
            r"{% tablerow i in (1..4) cols:'2' %}"
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
        description="cols is a float",
        template=(
            r"{% tablerow i in (1..4) cols:2.6 %}"
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
        description="limit is a string",
        template=(
            r"{% tablerow i in (1..4) limit:'2' %}"
            r"{{ i }} {{ tablerowloop.col_first }}"
            r"{% endtablerow %}"
        ),
        expect=(
            '<tr class="row1">\n'
            '<td class="col1">1 true</td>'
            '<td class="col2">2 false</td>'
            "</tr>\n"
        ),
    ),
    Case(
        description="offset is a string",
        template=(
            r"{% tablerow i in (1..4) offset:'2' %}"
            r"{{ i }} {{ tablerowloop.col_first }}"
            r"{% endtablerow %}"
        ),
        expect=(
            '<tr class="row1">\n'
            '<td class="col1">3 true</td>'
            '<td class="col2">4 false</td>'
            "</tr>\n"
        ),
    ),
    # Case(
    #     description="cols is non number string",
    #     template=(
    #         r"{% tablerow i in (1..4) cols:'foo' %}"
    #         r"{{ i }} {{ tablerowloop.col_first }}"
    #         r"{% endtablerow %}"
    #     ),
    #     expect=(
    #         '<tr class="row1">\n'
    #         '<td class="col1">1 true</td>'
    #         '<td class="col2">2 false</td>'
    #         '<td class="col3">3 false</td>'
    #         '<td class="col4">4 false</td>'
    #         "</tr>\n"
    #     ),
    # ),
    # Case(
    #     description="limit is non number string",
    #     template=(
    #         r"{% tablerow i in (1..4) limit:'foo' %}"
    #         r"{{ i }} {{ tablerowloop.col_first }}"
    #         r"{% endtablerow %}"
    #     ),
    #     expect='<tr class="row1">\n</tr>\n',
    # ),
    # Case(
    #     description="offset is non number string",
    #     template=(
    #         r"{% tablerow i in (1..4) offset:'foo' %}"
    #         r"{{ i }} {{ tablerowloop.col_first }}"
    #         r"{% endtablerow %}"
    #     ),
    #     expect=(
    #         '<tr class="row1">\n'
    #         '<td class="col1">1 true</td>'
    #         '<td class="col2">2 false</td>'
    #         '<td class="col3">3 false</td>'
    #         '<td class="col4">4 false</td>'
    #         "</tr>\n"
    #     ),
    # ),
    # Case(
    #     description="offset is an array",
    #     template=(
    #         r"{% tablerow i in (1..4) offset:foo %}"
    #         r"{{ i }} {{ tablerowloop.col_first }}"
    #         r"{% endtablerow %}"
    #     ),
    #     expect=(
    #         '<tr class="row1">\n'
    #         '<td class="col1">1 true</td>'
    #         '<td class="col2">2 false</td>'
    #         '<td class="col3">3 false</td>'
    #         '<td class="col4">4 false</td>'
    #         "</tr>\n"
    #     ),
    #     globals={"foo": [1, 2, 3]},
    #     error=True,
    # ),
]
