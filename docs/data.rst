Liquid data model
=================

Python Liquid's built-in tags and filters work with JSON-like data – objects, arrays,
strings, numbers, ``true``, ``false`` and ``null``.

In Python that's :class:`dict` (or any :class:`collections.abc.Mapping`), :class:`list`
(or any :class:`collections.abc.Sequence`), :class:`str`, :class:`int`, :class:`float`,
:class:`decimal.Decimal`, :class:`bool` and :class:`None`.

All other objects are accessed through the *Drop interface*.

Drops
-----

A drop is a Python object implementing some or all of the Drop interface. Drops are often
used for lazy or dynamic properties that rely on external data or are computed using
render context state.

If an object implementing :meth:`__liquid_hasattr__() <liquid.LiquidObject.__liquid_hasattr__>`
and  :meth:`__liquid_getattr__() <liquid.LiquidObject.__liquid_getattr__()>` appears in
template data, Liquid will use those methods to check for property existence and to
perform property resolution.

In this example we expose some properties of our class to Liquid but keep others private.

.. code-block:: python

    from liquid import Environment, RenderContext, StrictUndefined

    class MyDataObject:
        def __init__(self, a: str, b: int, secret: object) -> None:
            self.a = a
            self.b = b
            self.secret = secret

        def __liquid_hasattr__(self, name: str, context: RenderContext) -> bool:
            return name in ("a", "b")

        def __liquid_getattr__(self, name: str, context: RenderContext) -> object:
            if name in ("a", "b"):
                return getattr(self, name)
            raise AttributeError(f"no such attribute {name!r}")


    env = Environment()

    source = """\
    a => {{ obj.a }}
    b => {{ obj.b }}
    secret => {{ obj.secret }}
    """

    data = {
        "obj": MyDataObject("foo", 42, "secret"),
    }

    template = env.parse(source)
    print(template.render(data))
    # a => foo
    # b => 42
    # secret =>


    env.undefined_type = StrictUndefined
    print(template.render(data))
    # liquid.exceptions.UndefinedVariableError: obj.secret is undefined
    #   -> '' 3:13
    #   |
    # 3 | secret => {{ obj.secret }}
    #   |              ^^^^^^^^^^ obj.secret is undefined

There's also :meth:`__liquid_hasattr_async__() <liquid.LiquidAsyncObject.__liquid_hasattr_async__>`
and  :meth:`__liquid_getattr_async__() <liquid.LiquidAsyncObject.__liquid_getattr_async__()>`
if you need to read data for lazy properties asynchronously.

Iterable drops
^^^^^^^^^^^^^^

When looping over an object with the ``{% for %}`` tag, Liquid will look for methods
:meth:`__liquid_iter__() <liquid.LiquidIterable.__liquid_iter__>` and
:meth:`__liquid_iter_async__() <liquid.LiquidAsyncIterable.__liquid_iter_async__>`,
giving priority to the iterable drop interface over Python sequences and mappings. 

.. code-block:: python

    from liquid import AsyncIterableDrop, IterableDrop, render, slice_sequence

    class MyIterable:
        def __init__(self) -> None:
            self.some_sequence = [1, 2, 3]

        def __liquid_iter__(
            self, offset: int, limit: int | None, reversed_: bool
        ) -> IterableDrop[object]:
            return IterableDrop(
                *slice_sequence(self.some_sequence, offset, limit, reversed_)
            )

        async def __liquid_iter_async__(
            self, offset: int, limit: int | None, reversed_: bool
        ) -> IterableDrop[object] | AsyncIterableDrop[object]:
            # Do IO here.
            return IterableDrop(
                *slice_sequence(self.some_sequence, offset, limit, reversed_)
            )


    source = "{% for x in y %}{{ x }},{% endfor %}"

    data = {"y": MyIterable()}

    print(render(source, data))
    # 1,2,3,

Type coercion
^^^^^^^^^^^^^

Liquid applies automatic type coercion when an object passed to a filter or tag is not
of the expected type. If an object implements
:meth:`__liquid__() <liquid.LiquidPrimitive.__liquid__>`, it will be called during type
coercion with a context hint indicating which type is needed.

This table summarizes when each hint is used by Liquid. The special value
``liquid.NOTHING`` can be returned from ``__liquid__`` when there is no other reasonable
value to return.

============ ========================================================================
**Hint**     **Usage**
------------ ------------------------------------------------------------------------
``array``    When a list (or any Sequence) argument is expected.
``boolean``  When ``True`` or ``False`` is expected.
``index``    When a drop is used as a sequence index during variable path resolution.
``numeric``  When an integer, float or decimal argument is expected.
``object``   When a drop appears on the right hand side of an equality expression.
``output``   When a drop is serialized for output.
``property`` When a drop is used as a mapping key during variable path resolution.
``string``   When a string argument is expected.
============ ========================================================================

Notice that ``"output"`` is distinct from ``"string"``, giving objects the chance to have
a different string representation for output than when used as a string argument.

Also note that Liquid will not use ``__str__`` for serializing objects for output if
``__liquid__`` is defined.

.. code-block:: python

    from __future__ import annotations

    from typing import TYPE_CHECKING

    from liquid import NOTHING, render

    if TYPE_CHECKING:
        from liquid import ContextHint, RenderContext


    class MyObject:
        def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
            match hint:
                case "output" | "string":
                    return str(self)
                case "object":
                    return self
                case "boolean":
                    return True
                case "array":
                    return [1, 2, 3]
                case "numeric":
                    return 42
                case _:
                    return NOTHING

        def __str__(self) -> str:
            return "MyObject"


    source = """\
    {{ x }}
    {{ x | upcase }}
    {{ x | plus: 8 }}
    {% if x %}TRUE{% endif %}
    {% for y in x %}{{ y }},{% endfor %}
    """

    print(render(source, {"x": MyObject()}))
    # MyObject
    # MYOBJECT
    # 50
    # TRUE
    # 1,2,3,

Output representation
^^^^^^^^^^^^^^^^^^^^^

When rendered with the output statement (``{{ obj }}``), if an objects implements
:meth:`__liquid__() <liquid.LiquidPrimitive.__liquid__>`, Liquid will call ``__liquid__``
with the ``"output"`` hint and serialize the result according to
:meth:`liquid.Environment.serialize`.

.. code-block:: python

    from liquid import NOTHING, render

    class MyObject:
        def __liquid__(self, hint, context):
            if hint == "output":
                return "Hi 👋"

            if hint == "string":
                return "some string"

            return NOTHING

        def __str__(self) -> str:
            return "MyObject"


    source = """\
    {{ x }}
    {{ x | upcase }}
    """

    print(render(source, {"x": MyObject()}))
    # Hi 👋
    # SOME STRING

If HTML auto escaping is enabled and the result of ``__liquid__("output")`` contains
markup that you don't want to be escaped, wrap the result in ``markupsafe.Markup``.

.. code-block:: python

    import markupsafe

    from liquid import NOTHING, Environment


    class MyHTMLSafeObject:
        def __liquid__(self, hint, context):
            if hint == "output":
                return markupsafe.Markup('<script>alert("Hi 👋")</scipt>')
            return NOTHING


    class MyUnsafeObject:
        def __liquid__(self, hint, context):
            if hint == "output":
                return '<script>alert("Hi 👋")</scipt>'
            return NOTHING


    env = Environment(autoescape=True)

    source = """\
    {{ safe }}
    {{ unsafe }}
    """

    print(env.render(source, {"safe": MyHTMLSafeObject(), "unsafe": MyUnsafeObject()}))
    # <script>alert("Hi 👋")</scipt>
    # &lt;script&gt;alert(&#34;Hi 👋&#34;)&lt;/scipt&gt;
