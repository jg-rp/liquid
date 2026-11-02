Liquid data types
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

If an object implementing :meth:`liquid.LiquidObject.__liquid_hasattr__` and 
:meth:`liquid.LiquidObject.__liquid_getattr__()` appears in template data, Liquid will
use those methods to check for property existence and for property resolution.

In this example we explicitly expose some properties of our class to Liquid but keep
others private.

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

There's also :meth:`liquid.LiquidAsyncObject.__liquid_hasattr_async__` and 
:meth:`liquid.LiquidAsyncObject.__liquid_getattr_async__()` if you need to read data for
lazy properties asynchronously.

Iterable drops
^^^^^^^^^^^^^^

An iterable drop implements :meth:`liquid.LiquidIterable.__liquid_iter__` and
:meth:`liquid.LiquidAsyncIterable.__liquid_iter_async__`, which are 

TODO:

Equality and ordering
^^^^^^^^^^^^^^^^^^^^^

TODO: