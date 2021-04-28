Strictness
==========

Templates are parsed and rendered in `strict` mode by default. Where syntax and
render-time type errors raise an exception as soon as possible. You can change the error
tolerance mode with the ``tolerance`` argument to the ``Environment`` or ``Template``
constructor.

Available modes are ``Mode.STRICT``, ``Mode.WARN`` and ``Mode.LAX``.

.. code-block:: python

    from liquid import Environment, FileSystemLoader, Mode

    env = Environment(
        loader=FileSystemLoader("templates/"),
        tolerance=Mode.LAX,
    )

By default, references to undefined variables are silently ignored. In
`strict variables` mode, any operation on an undefined variable will raise an
``UndefinedError``.

.. code-block:: python

    from liquid import Environment, StrictUndefined

    env = Environment(
        loader=FileSystemLoader("templates/"),
        undefined=StrictUndefined,
