.. _Pipenv: https://pipenv.pypa.io/en/latest/

Python Liquid
=============

A Python implementation of `Liquid <https://shopify.github.io/liquid/>`_, the safe, customer-facing
template language for flexible web apps.

.. image:: https://img.shields.io/pypi/v/python-liquid.svg
    :target: https://pypi.org/project/python-liquid/
    :alt: Version

.. image:: https://github.com/jg-rp/liquid/actions/workflows/tests.yaml/badge.svg
    :target: https://github.com/jg-rp/liquid/tree/main/tests
    :alt: Tests

.. image:: https://img.shields.io/pypi/l/python-liquid.svg
    :target: https://pypi.org/project/python-liquid/
    :alt: Licence

.. image:: https://img.shields.io/pypi/pyversions/python-liquid.svg
    :target: https://pypi.org/project/python-liquid/
    :alt: Python versions

.. image:: https://img.shields.io/badge/pypy-3.7%20%7C%203.8-blue
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

Known Issues
************

`Please help by raising an issue if you notice an incompatibility.`

- Error handling. Python Liquid might not handle syntax or type errors in the same
  way as the reference implementation. We might fail earlier or later, and will 
  almost certainly produce a different error message.
  
- The built-in ``date`` filter uses `dateutil <https://dateutil.readthedocs.io/en/stable/>`_ for
  parsing strings to ``datetime``\s, and ``strftime`` for formatting. There are likely to be some
  inconsistencies between this and the reference implementation's equivalent parsing and formatting
  of dates and times.

- In Ruby Liquid, the built-in ``increment`` and ``decrement`` tags can, in some cases,
  mutate "global" context and keep named counters alive between renders. Although not 
  difficult to implement, I can't quite bring myself to do it.

- If a range literal uses a float literal as its start or stop value, the float literal 
  must have something after the decimal point. This is OK ``(1.0..3)``. This is not 
  ``(1...3)``. Ruby Liquid will accept either, resulting in a sequence of ``[1,2,3]``.

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

- Python Liquid uses type hints and static type checking. Run ``mypy`` or  ``tox -e typing`` to
- check for typing issues.

- Format code using `black <https://github.com/psf/black>`_.

- Write tests using ``unittest.TestCase``.

- Run tests with ``make test`` or ``python -m unittest`` or ``pytest``.

- Check test coverage with ``make coverage`` and open ``htmlcov/index.html`` in your
  browser.

- Check your changes have not adversely affected performance with ``make benchmark``.
