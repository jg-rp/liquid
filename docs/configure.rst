Configuration
=============

Template parsing and rendering behavior is configured using an instance of
:class:`liquid.Environment`. Once configured, you'd parse templates with
:meth:`liquid.Environment.parse` or :meth:`liquid.Environment.get_template`, both of
which return an instance of :class:`liquid.Template`.