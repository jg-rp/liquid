.. Liquid documentation master file, created by
   sphinx-quickstart on Sun Mar 21 07:16:31 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _Liquid: https://shopify.github.io/liquid/

Python Liquid
=============

Release v\ |version|

A Python implementation of `Liquid`_. A safe, customer-facing template language.

.. image:: https://img.shields.io/pypi/pyversions/python-liquid.svg
    :target: https://pypi.org/project/python-liquid/
    :alt: Python versions

.. image:: https://img.shields.io/badge/pypy-3.7-blue
    :target: https://pypi.org/project/python-liquid/
    :alt: PyPy versions

.. image:: https://img.shields.io/pypi/wheel/python-liquid.svg
    :target: https://pypi.org/project/python-liquid/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code style 

-------------------------------

Quick Start
-----------

Render a template string by creating a ``Template`` and calling its ``render`` method.

    >>> from liquid import Template
    >>> template = Template("Hello, {{ you }}!")
    >>> template.render(you="World")
    'Hello, World!'
    >>> template.render(you="Dave")         
    'Hello, Dave!'

When using the built-in ``include`` or ``render`` tags, it's necessary to create an
``Environment``, with a template ``Loader``, then load and render templates from that
environment.

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
    ...     {% for i in (1..3) %}
    ...     <p>hello {{ some }} {{ i }}</p>
    ...     {% endfor %}
    ...     </html>
    ... """)
    >>> template.render(some="thing")


User's Guide
------------



.. toctree::
    :maxdepth: 2
 
    user/description
    user/render
    user/context
    user/loaders
    user/tags
    user/filters


API Reference
-------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api

   


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
