.. _context:

Render Context
==============

Among other things, a render context includes namespaces for `global` variables passed
down from the ``Environment`` and `local` variables assigned with the built-in
``{% assign %}`` or ``{% capture %}`` tags.

The ``Environment`` constructor accepts ``globals``, a dictionary of variables made
available to all templates rendered from that environment. 

.. code-block:: python

    from liquid import Environment

    env = Environment(globals={"site_name": "Google"})

    template = env.from_string("""
        <html>
        <h1>{{ site_name }}</h1>
        {% for i in (1..3) %}
          <p>hello {{ some }} {{ i }}</p>
        {% endfor %}
        </html>
    """)

    print(template.render(some="thing"))

As does ``Template``, ``Environment.get_template`` and ``Environment.from_string``,
where the dictionary of variables is added to the resulting render context each time you
call ``render``.

.. code-block:: python

    from liquid import Environment

    env = Environment()

    template = env.get_template("index.html", globals={"page": "home"})
    print(template.render(some="thing"))