Filter
======

Liquid filters are implemented as callables. They can be functions or classes with a
``__call__`` method.

.. autotype:: liquid.Filter
    :no-index:

The first argument passed to the callable is always an instance of
:class:`FilterContext`. It has useful methods for coercing arguments to acceptable types
and raising exceptions.

The second argument is the result of evaluating the filter's *left* value. That's
everything to the left of the filter operator (``|``). Conventionally we give the second
argument the name ``left`` and the type ``object``.

Remaining arguments are defined by the filter.

For example, this is the complete implementation of the built-in ``append`` filter.

.. code-block:: python

    from liquid import FilterContext

    def append(context: FilterContext, left: object, right: object) -> str:
        return context.to_str(left, "") + context.to_str(right, "")

API
---

.. autoclass:: liquid.FilterContext
    :members:
