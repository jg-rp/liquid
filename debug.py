import difflib
import os
import sys
import textwrap

from liquid import Environment
from liquid.context import Context
from liquid.compiler import Compiler
from liquid.vm import VM
from liquid import code
from liquid.object import CompiledBlock


def main():
    env = Environment()
    # tree = env.parse(
    #     "<html>\n{% assign x = 1 %}{% capture some %}foo\n{% endcapture %}{{ some -}}\n{{ x }}\n{{ some }}</html>"
    # )
    # tree = env.parse("{% if false == false %}foo{% endif %}")

    # "{% for i in (1..3) %}{{ forloop }}{% endfor %}{{ 9999 }}"
    # "{% for i in (1..3) %}{% if i == 2 %}{% continue %}{% endif %}{{ forloop.index }}{% endfor %}{{ 9999 }}"
    # "{% for i in nums %}{{ i }}{% endfor %}"
    template = r"{% assign one = 1 %}{{ one }}"
    # r"{% for i in (0..1) %}{{ forloop.first }}{% for j in (2..3) %}{{ forloop.first }}{% for k in (4..5) %}{{ forloop.first }} {{ i }}{{ j }}{{ k }} {% endfor %}{% endfor %}{% endfor %}"
    tree = env.parse(template)

    ctx = {
        "product": {"title": "foo"},
        "title": "Hello",
        "nums": [1, 2, 3],
        "letters": ["a", "b", "c"],
    }

    compiler = Compiler()
    compiler.compile(tree)

    bytecode = compiler.bytecode()
    print(template)
    print_constants(bytecode.constants)
    print(code.string(bytecode.instructions))

    vm = VM(env, bytecode=bytecode, context=Context(ctx))
    vm.run()

    print(">", vm.current_buffer().getvalue(), "<")


def print_constants(constants):
    print("CONSTANTS:")
    for constant in constants:
        if isinstance(constant, CompiledBlock):
            print(textwrap.indent(code.string(constant.instructions), "\t"))
        else:
            print(textwrap.indent(repr(constant), "\t"))
    print("++++++++++++++++++")


if __name__ == "__main__":
    main()
