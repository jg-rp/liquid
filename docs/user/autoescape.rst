.. _autoescape:

HTML Auto Escape
================

As of version 0.7.4, Python Liquid offers HTML auto-escaping. Where context variables
are automatically escaped on output. Install optional dependencies for auto-escaping
using the ``autoescape`` extra.

.. code-block:: text

    $ python -m pip install -U python-liquid[autoescape]

Auto-escaping is disabled by default. Enable it by setting the ``Environment`` or 
``Template`` ``autoescape`` argument to ``True``.

.. code-block:: python

    >>> from liquid import Environment
    >>> env = Environment(autoescape=True)
    >>> template = env.from_string("<p>Hello, {{ you }}</p>")
    >>> template.render(you='</p><script>alert("XSS!");</script>')
    '<p>Hello, &lt;/p&gt;&lt;script&gt;alert(&#34;XSS!&#34;);&lt;/script&gt;</p>'

Mark a string as "safe" by making it ``Markup``.

.. code-block:: python

    >>> from liquid import Environment, Markup
    >>> env = Environment(autoescape=True)
    >>> template = env.from_string("<p>Hello, {{ you }}</p>")
    >>> template.render(you=Markup("<em>World!</em>"))
    '<p>Hello, <em>World!</em></p>'

Alternatively use the non-standard ``safe`` filter.

.. code-block:: python

    >>> from liquid import Environment
    >>> env = Environment(autoescape=True)
    >>> template = env.from_string("<p>Hello, {{ you | safe }}</p>")
    >>> template.render(you="<em>World!</em>")
    '<p>Hello, <em>World!</em></p>'