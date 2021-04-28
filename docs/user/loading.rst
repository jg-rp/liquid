.. _loading:

Template Loaders
================

If you want to use the built-in ``include`` or ``render`` tags, you'll need to create an 
``Environment``, with a template ``Loader``, then load and render templates from that
environment.

This example assumes a folder called ``templates`` exists in the current working
directory, and that the template file ``index.html`` exists within it.

.. code-block:: python

    from liquid import Environment
    from liquid import FileSystemLoader

    env = Environment(loader=FileSystemLoader("templates/"))

    template = env.get_template("index.html")
    print(template.render(some="variable", other="thing"))

You can create templates from strings using an ``Environment`` too. This is often more
efficient than using ``Template`` directly.

.. code-block:: python

    from liquid import Environment
    env = Environment()

    template = env.from_string("""
        <html>
        {% for i in (1..3) %}
          <p>hello {{ some }} {{ i }}</p>
        {% endfor %}
        </html>
    """)

    print(template.render(some="thing"))


Custom Loaders
--------------

Write a custom loader class by inheriting from ``liquid.loaders.BaseLoader`` and
implementing its ``get_source`` method. Here we implement ``DictLoader``, a loader that
uses a dictionary of strings instead of the file system for loading templates.

.. code-block:: python

    from liquid.loaders import BaseLoader
    from liquid.loaders import TemplateSource
    from liquid.exceptions import TemplateNotFound

    class DictLoader(BaseLoader):
        def __init__(self, templates: Mapping[str, str]):
            self.templates = templates

        def get_source(self, _: Env, template_name: str) -> TemplateSource:
            try:
                source = self.templates[template_name]
            except KeyError as err:
                raise TemplateNotFound(template_name) from err

            return TemplateSource(source, template_name, None)

``TemplateSource`` is a named tuple containing the template source as a string, its name
and an optional ``uptodate`` callable. If ``uptodate`` is not ``None`` it should be a
callable that returns ``False`` if the template needs to be loaded again, or ``True``
otherwise.

You could then use ``DictLoader`` like this.

.. code-block:: Python

    from liquid import Environment
    from liquid.loaders import DictLoader

    snippets = {
        "greeting": "Hello {{ user.name }}",
        "row": """
            <div class="row"'
              <div class="col">
                {{ row_content }}
              </div>
            </div>
            """,
    }

    env = Environment(loader=DictLoader(snippets))
    
    template = env.from_string("""
        <html>
          {% include 'greeting' %}
          {% for i in (1..3) %}
            {% include 'row' with i as row_content %}
          {% endfor %}
        </html>
    """)

    print(template.render(user={"name": "Brian"}))