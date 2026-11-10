Babel
=====

This page covers i18n and l10n filter and tag configuration, and how we support
translations and translation message catalogs. See :doc:`extra_filters` for usage
examples.

Currency
--------

The :ref:`currency-filter` filter returns the input number formatted as currency for
the current locale.

.. autoclass:: liquid.filters.Currency
   :no-index:

``currency`` defaults to looking for a locale in a render context variable called
``locale``, and a currency code in a render context variable called ``currency_code``. It
outputs in the locale's standard format and falls back to ``en_US`` and ``USD`` if those
context variables don't exist.

.. code-block:: python

   from liquid import parse

   template = parse("{{ 100457.99 | currency }}")

   print(template.render())
   print(template.render(currency_code="GBP"))
   print(template.render(locale="de", currency_code="CAD"))

.. code-block:: text

   $100,457.99
   £100,457.99
   100.457,99 CA$

To configure ``currency``, register a new instance of ``liquid.filters.Currency`` with an
:class:`liquid.Environment`, then render your templates from that. 

.. code-block:: python

   from liquid.filters import Currency
   from liquid import Environment

   env = Environment()
   env.filters["currency"] = Currency(default_locale="de")

Money
^^^^^

For convenience, some :ref:`money-filter` filters are defined that mimic Shopify's money
filter behavior. These are instances of `Currency`_ with specific default formats. All
other currency options are set to their defaults.

.. code-block:: python

   from liquid import parse

   template = parse("""\
   {% assign amount = 10 %}
   {{ amount | money }}
   {{ amount | money_with_currency }}
   {{ amount | money_without_currency }}
   {{ amount | money_without_trailing_zeros }}""")

   print(template.render(currency_code="CAD", locale="en_CA"))

.. code-block:: text

   $10.00
   $10.00 CAD
   10.00
   $10

DateTime
--------

The :ref:`datetime-filter` filter returns the input :class:`datetime.datetime` formatted
for the current locale.

.. autoclass:: liquid.filters.DateTime
   :no-index:

``datetime`` defaults to looking for a timezone in a render context variable called
``timezone``, a locale in a render context variable called ``locale`` and a datetime
format in a render context variable called ``datetime_format``.

.. code-block:: python

   from liquid import parse

   template = parse("{{ 'Apr 1, 2007, 3:30:00 PM' | datetime }}")

   print(template.render())
   print(template.render(locale="de", datetime_format="long"))
   print(template.render(locale="de", timezone="CET", datetime_format="short"))

.. code-block:: text

   Apr 1, 2007, 3:30:00 PM
   1. April 2007 um 15:30:00 UTC
   01.04.07, 17:30

To configure ``datetime``, register a new instance of ``liquid.filters.DateTime`` with an
instance of :class:`liquid.Environment`, then render your templates from that.

.. code-block:: python

   from liquid.filters import DateTime
   from liquid import Environment

   env = Environment()
   env.filters["datetime"] = DateTime(timezone_var="tz")

Decimal
-------

The :ref:`decimal-filter` filter returns the input number formatted as a decimal for the
current locale.

.. autoclass:: liquid.filters.Number
   :no-index:

``decimal`` defaults to looking for a locale in a render context variable called
``locale``. It uses the locale's standard format and falls back to ``en_US`` if that
variable does not exist.

.. code-block:: python

   from liquid import parse

   # Parse a number from a string in the default (en_US) input locale.
   template = parse("""\
   {{ '10,000.23' | decimal }}
   {{ '10,000.23' | decimal: group_separator: false }}
   """)

   print(template.render(locale="de"))
   print(template.render(locale="en_GB"))

.. code-block:: text

   10.000,23
   10000,23

   10,000.23
   10000.23

To configure ``decimal``, register a new instance of ``liquid.filters.Number`` with an
instance of :class:`liquid.Environment`, then render your templates from that.

.. code-block:: python

   from liquid.filters import Number
   from liquid import Environment

   env = Environment()
   env.filters["decimal"] = Number(default_locale="en_GB")

Unit
----

The :ref:`unit-filter` filter returns he input number formatted with the given units
according to the current locale. 

.. autoclass:: liquid.filters.Unit
   :no-index:

``unit`` defaults to looking for a locale in a render context variable called ``locale``,
a length in a render context variable called ``unit_length``, and a decimal format in a
render context variable called ``unit_format``.

.. code-block:: python

   from liquid import parse

   template = parse("""\
   {{ 12 | unit: 'length-meter', format: '#,##0.00' }}
   {{ 150 | unit: 'kilowatt', denominator_unit: 'hour' }}
   """)

   print(template.render(unit_length="long"))
   print(template.render(locale="de", unit_length="long"))

.. code-block:: text

   12.00 meters
   150 kilowatts per hour

   12,00 Meter
   150 Kilowatt pro Stunde

To configure ``unit``, register a new instance of ``liquid.filters.Unit`` with an
instance of :class:`liquid.Environment`, then render your templates from that.

.. code-block:: python

   from liquid.filters import Unit
   from liquid import Environment

   env = Environment()
   env.filters["unit"] = Unit(locale_var="_locale")

Translations
------------

Python Liquid includes :ref:`gettext-filter`, :ref:`ngettext-filter`,
:ref:`pgettext-filter` and :ref:`npgettext-filter` filters equivalent to the functions
found in Python's `gettext`_ module.

.. _gettext: https://docs.python.org/3/library/gettext.html

Additionally there's the :ref:`t-filter` filter which can behave like any of the
\*gettext filters depending on its arguments. Where the \*gettext filters require
positional arguments for ``context``, ``count`` and ``plural``, ``t`` reserves optional
``count`` and ``plural`` keyword arguments.

Liquid Babel also offers a :ref:`translate-tag` tag. This is similar to the
``{% trans %}`` tag found in `Jinja`_ or the ``{% blocktranslate %}`` tag found in
`Django`_'s template language.

.. _Jinja: https://jinja.palletsprojects.com/en/3.1.x/templates/#i18n
.. _Django: https://docs.djangoproject.com/en/4.1/topics/i18n/translation/#blocktranslate-template-tag

Filters
^^^^^^^

:ref:`gettext-filter`, :ref:`ngettext-filter`, :ref:`pgettext-filter` and
:ref:`npgettext-filter` filters all default to looking for :ref:`message-catalogs` in a
render context variable called ``translations``, falling back to an instance of
`NullTranslations`_ if ``translations`` can not be resolved.

.. _NullTranslations: https://docs.python.org/3/library/gettext.html#gettext.NullTranslations

.. code-block:: python

   from liquid import parse

   # You'll need to load an appropriate Translations object.
   # `get_translations()` is defined elsewhere.
   translations = get_translations(locale="de")

   template = parse("{{ 'Hello, World!' | t }}")
   print(template.render(translations=translations))  # Hallo Welt!

.. _message-catalogs:

Message catalogs
^^^^^^^^^^^^^^^^

By default, all translation filters and tags will look for a render context variable
called ``translations``, which must be an object implementing the ``Translations``
protocol. It is the application developer's responsibility to provide a ``Translations``
object, being the interface between Liquid and a message catalog.

The ``Translations`` protocol is defined as follows. It is simply a subset of the
`NullTranslations`_ class found in the `gettext`_ module.

.. code-block:: python

   class Translations(Protocol):
       def gettext(self, message: str) -> str: ...

       def ngettext(self, singular: str, plural: str, n: int) -> str: ...

       def pgettext(self, context: str, message: str) -> str: ...

       def npgettext(self, context: str, singular: str, plural: str, n: int) -> str: ...

It could be a `GNUTranslations`_ instance, a `Babel Translations`_ instance, or any
object implementing ``gettext``, ``ngettext``, ``pgettext`` and ``npgettext`` methods.

.. _GNUTranslations: https://docs.python.org/3/library/gettext.html#gettext.GNUTranslations
.. _Babel Translations: https://babel.pocoo.org/en/latest/support.html#extended-translations-class

Message variables
^^^^^^^^^^^^^^^^^

Translatable message text can contain placeholders for variables. When using variables in
strings to be translated by filters, variables are defined using percent-style formatting.
Only the ``s`` modifier is supported and every variable must have a name. In this example
``you`` is the variable name.

.. code-block:: liquid2

   {{ "Hello, %(you)s!" | t }}

Filter keyword arguments are merged with the current render context before being used to
replace variables in message text. All variables are converted to their string
representation before substitution. Dotted property/attribute access is not supported
inside message variables.

.. code-block:: liquid2

   {{ "Hello, %(you)s!" | t: you: user.name }}

The :ref:`translate-tag` block tag recognizes simplified Liquid output statements as
translation message variables. These variables must be valid identifiers without dotted
or bracketed property/attribute access, and no filters.

.. code-block:: liquid2

   {% translate %}
       Hello, {{ you }}!
   {% endtranslate %}

Keyword arguments passed to the :ref:`translate-tag` tag will be merged with the current
render context before being used to replace variables in message text.

.. code-block:: liquid2

   {% translate you: user.name, count: users.size %}
       Hello, {{ you }}!
   {% plural %}
       Hello, {{ you }}s!
   {% endtranslate %}

Message Extraction
^^^^^^^^^^^^^^^^^^

Use the :func:`liquid.extract_from_template` function to build a message `catalog`_ from
one or more templates. You are then free to make use of Babel's `PO file`_ features, or
convert the catalog to a more convenient internal representation.

.. _catalog: https://babel.pocoo.org/en/latest/api/messages/catalog.html#catalogs
.. _PO file: https://babel.pocoo.org/en/latest/api/messages/pofile.html

.. code-block:: python

   import io

   from babel.messages.pofile import write_po

   from liquid import extract_from_templates, parse

   source = """
   {% # Translators: some comment %}
   {{ 'Hello, World!' | t }}
   {% comment %}Translators: other comment{% endcomment %}
   {% translate count: 2 %}
       Hello, {{ you }}!
   {% plural %}
       Hello, all!
   {% endtranslate %}
   """

   template = parse(source, name="something.liquid")
   catalog = extract_from_templates(template)

   buf = io.BytesIO()
   write_po(buf, catalog, omit_header=True)
   print(buf.getvalue().decode("utf-8"))

.. code-block:: text

   #. Translators: some comment
   #: something.liquid:3
   msgid "Hello, World!"
   msgstr ""

   #. Translators: other comment
   #: something.liquid:5
   #, python-format
   msgid "Hello, %(you)s!"
   msgid_plural "Hello, all!"
   msgstr[0] ""
   msgstr[1] ""

Translator Comments
^^^^^^^^^^^^^^^^^^^

When a Liquid comment tag immediately precedes a translatable filter or tag, and the
comment starts with a string in ``comment_tags``, that comment will be included as a
translator comment with the message. Use the ``comment_tags`` argument to
:func:`liquid.extract_liquid`, or :func:`liquid.extract_from_templates` to change
translator comment prefixes. The default is ``["Translators:"]``.

.. code-block:: python

   from liquid import extract_from_templates, parse

   source = """
   {% # Translators: some comment %}
   {{ 'Hello, World!' | t }}
   {% comment %}Translators: other comment{% endcomment %}
   {% translate count: 2 %}
       Hello, {{ you }}!
   {% plural %}
       Hello, all!
   {% endtranslate %}
   """

   template = parse(source, name="something.liquid")
   catalog = extract_from_templates(template, strip_comment_tags=True)

   message = catalog.get("Hello, World!")
   print(message.auto_comments[0])  # some comment


