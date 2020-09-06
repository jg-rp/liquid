Liquid
======

Liquid is a Python implementation of the .. Liquid: https://shopify.github.io/liquid/
template engine. A non evaling templating language suitable for end users.

Installing
----------

Install and update using `pip`_:

.. code-block:: text

    $ pip install -U liquid

.. _pip: https://pip.pypa.io/en/stable/quickstart/


API
---

An application typically creates a single `Environment`, with a template `Loader`, then
loads and renders templates from that environment. Similar to that of the .. Jinja: 
https://github.com/pallets/jinja high-level API.

.. code-block:: python

    from liquid import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader("templates/"))
    template = env.get_template("index.html")

    print(template.render(some="variable", other="thing"))


The `Environment` constructor and `get_template` method of an environment also accept
`globals`, a dictionary of variables made available to all templates rendered from
the environment or for each call to `render`, respectively.

.. code-block:: python

    from liquid import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader("templates/"), globals={"site_name": "Google"})
    template = env.get_template("index.html", globals={"title": "Home Page"})

    print(template.render(some="variable", other="thing"))


Templates are rendered in `lax` mode by default, where syntax and render-time type
errors are ignored as much as possible. You can change the error tollerence mode
with the `tollerence` argument to the `Environment` constructor.

Available modes are ``Mode.STRICT``, ``Mode.WARN`` and ``Mode.LAX``.

.. code-block:: python

    from liquid import Environment, FileSystemLoader, Mode

    env = Environment(loader=FileSystemLoader("templates/"), tollerence=Mode.WARN)


Limitations
-----------

The following limitations might be removed in future releases. These limitations apply
as of version 0.5.

Performance
***********

This project was conceived as the engine behind a Shopify theme local development
environment. As such, performance was not a particularly high priority.

There is no "compile" phase. Templates are tokenized, parsed and rendered directly from
the parse tree. The parse tree is not very compact, so consumes more memory than is ideal
for production deployments.

As there is no bytecode to speak of, persistent caching of parsed templates is limited
to pickling and compressing parse trees, which is not very portable.

TODO: Benchmark


Compatibility
-------------

We strive to be 100% compatible with the reference implementation of .. Liquid: 
https://shopify.github.io/liquid/, written in Ruby. That is, given an equivalent render
context, a template rendered with Python Liquid should produce the same output as when
rendered with Ruby Liquid.

Known Issues
************

- Error handling. Python Liquid might not handle syntax or type errors in the same
  way as the reference implementation. We might fail earlier or later, and will 
  almost certainly produce a differed error message.

TODO

Custom Filters
--------------

TODO


Custom Tags
-----------

TODO


Custom Loaders
--------------

TODO


Frequently Asked Questions
--------------------------

TODO
