import textwrap

from liquid import Environment
from liquid.context import Context
from liquid.compiler import Compiler
from liquid.vm import VM
from liquid import code
from liquid.object import CompiledBlock

from performance import load_data, register_mocks, load_templates


def debug():
    ctx = load_data()

    env = Environment(globals=ctx)
    register_mocks(env)

    # tree = env.parse(
    #     "<html>\n{% assign x = 1 %}{% capture some %}foo\n{% endcapture %}{{ some -}}\n{{ x }}\n{{ some }}</html>"
    # )
    # tree = env.parse("{% if false == false %}foo{% endif %}")

    # "{% for i in (1..3) %}{{ forloop }}{% endfor %}{{ 9999 }}"
    # "{% for i in (1..3) %}{% if i == 2 %}{% continue %}{% endif %}{{ forloop.index }}{% endfor %}{{ 9999 }}"
    # "{% for i in nums %}{{ i }}{% endfor %}"
    # template = r"{% assign one = 1 %}{{ one }}"
    # template = r"{% tablerow tag in tags cols:2 %}{{ tag }}{% endtablerow %}"
    # template = r"{% for tag in product.tags %}{% assign x = tag %}{% endfor %}{{ x }}"
    # template = r"{% if true %}  {% elsif false %} {% else %} {% endif %}"
    # template= r"{% for i in (0..1) %}{{ forloop.first }}{% for j in (2..3) %}{{ forloop.first }}{% for k in (4..5) %}{{ forloop.first }} {{ i }}{{ j }}{{ k }} {% endfor %}{% endfor %}{% endfor %}"

    template = (
        r"{% if collection.description.size > 0 %}"
        r"<div class='latest-news'>{{ collection.description }}</div>"
        r"{% endif %}"
    )
    #     template = r"""
    # <div id="product-left">
    # {% for image in product.images %}
    #     {% if forloop.first %}
    #         <div id="product-image">
    #             <a href="{{ image | product_img_url: 'large' }}" rel="lightbox[images]" title="{{ product.title | escape }}">
    #                 <img src="{{ image | product_img_url: 'medium' }}" alt="{{ product.title | escape }}" />
    #             </a>
    #         </div>
    #     {% else %}
    #         <div class="product-images">
    #             <a href="{{ image | product_img_url: 'large' }}" rel="lightbox[images]" title="{{ product.title | escape }}">
    #                 <img src="{{ image | product_img_url: 'small' }}" alt="{{ product.title | escape }}" />
    #             </a>
    #         </div>
    #     {% endif %}
    # {% endfor %}
    # </div>"""

    # templates = load_templates("tests/fixtures/tribble/")
    # template = templates[4]
    tree = env.parse(template)

    # ctx = {
    #     "product": {
    #         "title": "foo",
    #         "tags": [
    #             "tag1",
    #             "tag2",
    #             "tag3",
    #             "tag4",
    #         ],
    #     },
    #     "title": "Hello",
    #     "nums": [1, 2, 3],
    #     "letters": ["a", "b", "c"],
    #     "tags": [
    #         "tag1",
    #         "tag2",
    #         "tag3",
    #         "tag4",
    #     ],
    # }

    compiler = Compiler()
    compiler.compile(tree)

    bytecode = compiler.bytecode()
    # print(template)
    print_constants(bytecode.constants)
    print(code.string(bytecode.instructions))

    vm = VM(env, bytecode=bytecode, context=Context(ctx, filters=env.filters))
    vm.run()

    print(">", vm.current_buffer.getvalue(), "<")


def print_constants(constants):
    print("CONSTANTS:")
    for constant in constants:
        if isinstance(constant, CompiledBlock):
            print(textwrap.indent(code.string(constant.instructions), "\t"))
        else:
            print(textwrap.indent(repr(constant), "\t"))
    print("++++++++++++++++++")


def run(source: str, context=None) -> str:
    env = Environment()
    template = env.from_string(source)
    return template.run(**context)


def main():
    template_source = r"{% unless false %}foo{% endunless %}"
    result = run(template_source, {})
    print(result)


if __name__ == "__main__":
    debug()
    # main()
