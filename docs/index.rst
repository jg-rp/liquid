.. Liquid documentation master file, created by
   sphinx-quickstart on Sun Mar 21 07:16:31 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _Liquid: https://shopify.github.io/liquid/

Python Liquid
=============

Release v\ |version|

A Python implementation of `Liquid`_. A non evaling templating language suitable for
end users.

Also see documentation at https://jg-rp.github.io/liquid/.

Installation
------------

Install and update using `pip <https://pip.pypa.io/en/stable/quickstart/>`_:

.. code-block:: text

    $ python -m pip install -U python-liquid

Quick Start
-----------

Render a template string by creating a ``Template`` and calling its ``render`` method.

    >>> from liquid import Template
    >>> template = Template("Hello, {{ you }}!")
    >>> template.render(you="World")
    'Hello, World!'
    >>> template.render(you="Dave")         
    'Hello, Dave!'

Keyword arguments passed to ``render`` are made available as variables for templates
to use in Liquid expressions.

If you want to use the built-in ``include`` or ``render`` tags, you'll need to create an 
``Environment``, with a template ``Loader``, then load and render templates from that
environment.

This example assumes a folder called ``templates`` exists in the current working
directory, and that the template file ``index.html`` exists within it.

    >>> from liquid import Environment, FileSystemLoader
    >>> env = Environment(loader=FileSystemLoader("templates/"))
    >>> template = env.get_template("index.html")
    >>> template.render(some="variable", other="thing")

You can create templates from strings using an ``Environment`` too. This is often more
efficient than using ``Template`` directly.

    >>> from liquid import Environment
    >>> env = Environment()
    >>> template = env.from_string(""" 
    ...     <html>    
    ...     {% for i in (1..3) -%}
    ...     <p>hello {{ some }} {{ i }}</p>
    ...     {% endfor -%}
    ...     </html>
    ... """)
    >>> print(template.render(some="thing"))
    <html>
    <p>hello thing 1</p>
    <p>hello thing 2</p>
    <p>hello thing 3</p>
    </html>


User's Guide
------------

See documentation at https://jg-rp.github.io/liquid/.

API Reference
-------------

.. toctree::
   :maxdepth: 2

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
