"""Golden tests cases for testing liquid's `comment` tag.

Some of these test cases are take from Shopify/Liquid unit tests. See 
https://github.com/jg-rp/liquid-1/blob/main/test/unit/tags/comment_tag_unit_test.rb.

The Shopify/Liquid license is included bellow.

Copyright (c) 2005, 2006 Tobias Luetke

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from liquid.golden.case import Case

cases = [
    Case(
        description="don't render comments",
        template=r"{% comment %}foo{% endcomment %}",
        expect="",
    ),
    Case(
        description="respect whitespace control in comments",
        template="\n{%- comment %}foo{% endcomment -%}\t \r",
        expect="",
    ),
    Case(
        description="don't render comments with tags",
        template=(
            r"{% comment %}"
            r"{% if true %}"
            r"{{ title }}"
            r"{% endif %}"
            r"{% endcomment %}"
        ),
        expect="",
    ),
    Case(
        description="comment inside liquid tag",
        template="\n".join(
            [
                r"{% liquid",
                r"    if 1 != 1",
                r"    comment",
                r"    else",
                r"    echo 123",
                r"    endcomment",
                r"    endif",
                r"%}",
            ]
        ),
        expect="",
    ),
    Case(
        description="commented tags are not parsed",
        template=(
            r"{% comment %}"
            r"    {% if true %}"
            r"    {% if ... %}"
            r"    {%- for ? -%}"
            r"    {% while true %}"
            r"    {%"
            r"    unless if"
            r"    %}"
            r"    {% endcase %}"
            r"{% endcomment %}"
        ),
        expect="",
    ),
    # Case(
    #     description="malformed tags are not parsed",
    #     template=r"{% comment %}{% assign foo = '1'{% endcomment %}",
    #     expect="",
    # ),
    # Case(
    #     description="incomplete tags are not parsed",
    #     template=r"{% comment %}{% {{ {%- endcomment %}",
    #     expect="",
    # ),
    Case(
        description="nested comment blocks",
        template=(
            r"{% comment %}"
            r"    {% comment %}"
            r"    {% comment %}{%    endcomment     %}"
            r"    {% endcomment %}"
            r"{% endcomment %}"
        ),
        expect="",
        future=True,
    ),
    Case(
        description="unclosed nested comment blocks",
        template=(
            r"{% comment %}"
            r"    {% comment %}"
            r"    {% comment %}"
            r"    {% endcomment %}"
            r"{% endcomment %}"
        ),
        expect="",
        error=True,
        future=True,
    ),
    Case(
        description="raw inside comment block",
        template=(
            r"{% comment %}"
            r"    {% raw %}"
            r"    {% endcomment %}"
            r"    {% endraw %}"
            r"{% endcomment %}"
        ),
        expect="",
    ),
]
