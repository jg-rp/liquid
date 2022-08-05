.. _Pipenv: https://pipenv.pypa.io/en/latest/

Python Liquid
=============

A Python implementation of `Liquid <https://shopify.github.io/liquid/>`_, the safe, customer-facing
template language for flexible web apps.

.. image:: https://img.shields.io/pypi/v/python-liquid?style=flat-square
    :target: https://pypi.org/project/python-liquid/
    :alt: Version

.. image:: https://img.shields.io/github/workflow/status/jg-rp/liquid/Tests?style=flat-square
    :target: https://github.com/jg-rp/liquid/tree/main/tests
    :alt: Tests

.. image:: https://img.shields.io/pypi/l/python-liquid.svg?style=flat-square
    :target: https://pypi.org/project/python-liquid/
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/python-liquid.svg?style=flat-square
    :target: https://pypi.org/project/python-liquid/
    :alt: Python versions

.. image:: https://img.shields.io/badge/pypy-3.7%20%7C%203.8-blue?style=flat-square
    :target: https://pypi.org/project/python-liquid/
    :alt: PyPy versions

.. code-block:: python

    from liquid import Template

    template = Template("Hello, {{ you }}!")
    print(template.render(you="World"))  # "Hello, World!"
    print(template.render(you="Liquid"))  # "Hello, Liquid!"


Installing
----------

Install Python Liquid using `Pipenv`_:

.. code-block:: text

    $ pipenv install python-liquid

Or `pip <https://pip.pypa.io/en/stable/getting-started/>`_:

.. code-block:: text

    $ python -m pip install -U python-liquid

Links
-----

- Documentation: https://jg-rp.github.io/liquid/
- Change Log: https://github.com/jg-rp/liquid/blob/main/CHANGES.rst
- PyPi: https://pypi.org/project/python-liquid/
- Source Code: https://github.com/jg-rp/liquid
- Issue Tracker: https://github.com/jg-rp/liquid/issues

Related Projects
----------------

- `liquid-babel <https://github.com/jg-rp/liquid-babel>`_: Internationalization and localization
  for Liquid templates.
- `LiquidScript <https://github.com/jg-rp/liquidscript>`_: A JavaScript and TypeScript engine for
  Liquid with a similar high-level API to Python Liquid.
- `django-liquid <https://github.com/jg-rp/django-liquid>`_: A Django template backend for Liquid.
  Render Liquid templates in your Django apps.
- `Flask-Liquid <https://github.com/jg-rp/Flask-Liquid>`_: A Flask extension for Liquid. Render
  Liquid templates in your Flask applications.
- `python-liquid-extra <https://github.com/jg-rp/liquid-extra>`_: A growing collection of extra tags
  and filters for Python Liquid. Highlights of which are: 

  - an ``if`` tag that supports ``not`` and grouping with parentheses.
  - ``macro`` and ``call`` tags for defining and calling parameterized Liquid snippets.
  - inline ``if``/``else`` expressions. For example ``{{ 'active' if link.active else '' }}`` or
    ``{% assign selected = true if product.selected_variant else false %}``.
  - a JSON encoding filter.

- `golden-liquid <https://github.com/jg-rp/golden-liquid>`_: A test suite for Liquid. See how
  various Liquid template engines compare to the reference implementation.

Compatibility
-------------

We strive to be 100% compatible with the `reference implementation <https://shopify.github.io/liquid/>`_
of Liquid, written in Ruby. That is, given an equivalent render context, a template rendered with
Python Liquid should produce the same output as when rendered with Ruby Liquid.

See the `known issues page <https://jg-rp.github.io/liquid/known_issues>`_ for details of known
incompatibilities between Python Liquid and Ruby Liquid, and please help by raising an issue
if you notice an incompatibility.


Benchmark
---------

You can run the benchmark using ``make benchmark`` (or ``python -O performance.py`` if
you don't have ``make``) from the root of the source tree. On my ropey desktop computer
with a Ryzen 5 1500X, we get the following results.

.. code-block:: text

    Best of 5 rounds with 100 iterations per round and 60 ops per iteration (6000 ops per round).
    
    lex template (not expressions): 1.3s (4727.35 ops/s, 78.79 i/s)
                     lex and parse: 6.4s (942.15 ops/s, 15.70 i/s)
                            render: 1.7s (3443.62 ops/s, 57.39 i/s)
             lex, parse and render: 8.2s (733.30 ops/s, 12.22 i/s)

And PyPy3.7 gives us a decent increase in performance.

.. code-block:: text

    Best of 5 rounds with 100 iterations per round and 60 ops per iteration (6000 ops per round).

    lex template (not expressions): 0.58s (10421.14 ops/s, 173.69 i/s)
                     lex and parse: 2.9s (2036.33 ops/s, 33.94 i/s)
                            render: 1.1s (5644.80 ops/s, 94.08 i/s)
             lex, parse and render: 4.2s (1439.43 ops/s, 23.99 i/s)


On the same machine, running ``rake benchmark:run`` from the root of the reference
implementation source tree gives us these results.

.. code-block:: text

    /usr/bin/ruby ./performance/benchmark.rb lax

    Running benchmark for 10 seconds (with 5 seconds warmup).

    Warming up --------------------------------------
                 parse:     3.000  i/100ms
                render:     8.000  i/100ms
        parse & render:     2.000  i/100ms
    Calculating -------------------------------------
                 parse:     39.072  (± 0.0%) i/s -    393.000  in  10.058789s
                render:     86.995  (± 1.1%) i/s -    872.000  in  10.024951s
        parse & render:     26.139  (± 0.0%) i/s -    262.000  in  10.023365s


I've tried to match the benchmark workload to that of the reference implementation, so that we might
compare results directly. The workload is meant to be representative of Shopify's use case, although
I wouldn't be surprised if their usage has changed subtly since the benchmark fixture was designed.

Contributing
------------

- Install development dependencies with `Pipenv`_

- Python Liquid uses type hints and static type checking. Run ``mypy`` or  
  ``tox -e typing`` to check for typing issues.

- Format code using `black <https://github.com/psf/black>`_.

- Write tests using ``unittest.TestCase``.

- Run tests with ``make test`` or ``python -m unittest`` or ``pytest``.

- Check test coverage with ``make coverage`` and open ``htmlcov/index.html`` in your
  browser.

- Check your changes have not adversely affected performance with ``make benchmark``.

Docs
****

`Documentation <https://jg-rp.github.io/liquid/>`_ is built using `Docusaurus <https://docusaurus.io/>`_.
Find the source in the `docs branch <https://github.com/jg-rp/liquid/tree/docs>`_ of this repository.

The ``docs`` folder in the root of this repository contains older, sphinx-based docs, still hosted
on `Read the Docs <https://liquid.readthedocs.io/en/latest/>`_.

The plan is to generate API Documentation for Docusaurus from Python doc comments. The older docs
will be kept until such time that better Docusaurus/sphinx integration is available or a workaround
is found.