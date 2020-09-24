import difflib
import os
import sys

from liquid import Environment
from liquid.context import Context
from liquid.compiler import Compiler
from liquid.vm import VM
from liquid import code


def main():
    env = Environment()
    # tree = env.parse(
    #     "<html>\n{% assign x = 1 %}{% capture some %}foo\n{% endcapture %}{{ some -}}\n{{ x }}\n{{ some }}</html>"
    # )
    # tree = env.parse("{% if false == false %}foo{% endif %}")
    tree = env.parse(
        "{% for i in nums %}{{ i }}{% endfor %}"
        # r"{% for i in nums %}{% for j in letters %}{% if j == 'b' %}{% continue %}{% endif %}{{ i }}{{ j }} {% endfor %}{% endfor %}"
    )

    ctx = {
        "product": {"title": "foo"},
        "title": "Hello",
        "nums": [1, 2, 3],
        "letters": ["a", "b", "c"],
    }

    compiler = Compiler()
    compiler.compile(tree)

    bytecode = compiler.bytecode()
    print(bytecode.constants)
    print(code.string(bytecode.instructions))

    vm = VM(env, bytecode=bytecode, context=Context(ctx))
    vm.run()

    print(">", vm.current_buffer().getvalue(), "<")


if __name__ == "__main__":
    main()
