Python Liquid Change Log
========================

Version 0.6.2
-------------

- Refactored the standard expression parser. It's now possible to extend ``ExpressionParser`` for use with custom tags.
- Decoupled boolean expression parsing for easier ``if``, ``unless`` and ``case`` tag subclassing.

Version 0.6.1
-------------

- Added support for Python 3.7 and PyPy3.7.


Version 0.6.0
-------------

- Added support for named filter parameters.
- The ``default`` filter now accepts the named parameter ``allow_false``.
- The ``truncate_words`` filter now forces a minimum number of words to 1.
- The ``newline_to_br`` filter now replaces ``\n`` and ``\r\n`` with ``<br />\n``.
- The ``strip_newlines`` filter strips ``\r\n``.
  