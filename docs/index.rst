Python Liquid
=============

Python Liquid is a Python engine for Liquid, the safe, customer-facing template
language. We follow `Shopify/liquid`_ closely and test against `Shopify/liquid-spec`_.

.. note::

   This is the documentation for the Python Liquid version 3 (GitHub_). Archived
   documentation for versions 1 and 2 can be found 
   `here <https://jg-rp.github.io/python-liquid-docs-archive/>`_ and
   `here <https://github.com/jg-rp/liquid/blob/v2.3.6/docs/index.md>`_, respectively.

.. _Shopify/liquid: https://github.com/Shopify/liquid
.. _Shopify/liquid-spec: https://github.com/Shopify/liquid-spec
.. _GitHub: https://github.com/jg-rp/liquid

Install
-------

Install ``python-liquid`` from PyPI_ using your favorite package manager.

.. _PyPI: https://pypi.org/project/python-liquid

**pip**

.. code-block:: shell

   python -m pip install python-liquid

**uv**

.. code-block:: shell

   uv add python-liquid   

**pipenv**

.. code-block:: shell

   pipenv install -u python-liquid

Quick start
-----------

Use the package-level :func:`liquid.render` function to render a template with Liquid's
default configuration.

.. code-block:: python

   import liquid

   print(liquid.render("Hello, {{ you }}!", {"you": "World"}))  # Hello, World!


And :func:`liquid.parse` to get an instance of :class:`liquid.Template`, which can be
rendered multiple times with different data.

.. code-block:: python

   import liquid

   template = liquid.parse("Hello, {{ you }}!")
   print(template.render({"you": "World"})) # Hello, World!
   print(template.render({"you": "Liquid"})) # Hello, Liquid!

You'll need to create an instance of :class:`liquid.Environment` to configure Liquid,
then load and render templates from that.

.. code-block:: python

   from liquid import Environment, CachingFileSystemLoader

   env = Environment(
      autoescape=True,
      loader=CachingFileSystemLoader("./templates")
   )

   template = env.get_template("index.liquid")
   another_template = env.parse("{% render 'greeting' %}, World!")


.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contents

   configure.rst
   api.rst
