Python Liquid Change Log
========================

Version 0.7.0
-------------

- New ``Template`` API. Create templates from strings without an ``Environment``.
- The ``template`` object is no longer included in every render context automatically.
- 

Version 0.6.4
-------------

- Implemented the ``blank`` keyword. Empty string and strings containing only whitespace are equal to ``blank``.
- Implemented the ``null`` keyword. ``null`` is an alias for ``nil``.
- Implemented the ``ifchanged`` tag.

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
  