Template loaders
================

A template loader is responsible for finding template source code given a name or
identifier. Every time you call :meth:`liquid.Environment.get_template` or when Python
Liquid renders a ``{% render %}``, ``{% include %}`` or ``{% extends %}`` tag, the
configured template loader is called upon.

Configure a template loader by passing an instance of :class:`liquid.Loader` to the
`loader` argument of the :class:`liquid.Environment` constructor.

Built-in template loaders include :class:`liquid.DictLoader`, :class:`liquid.FileSystemLoader`,
:class:`liquid.PackageLoader` and :class:`liquid.ChoiceLoader`, and some caching variants
:class:`liquid.CachingDictLoader` and :class:`liquid.CachingFileSystemLoader`.

You are encouraged to implement your own template loader to read templates from a database
or process front matter, for example.

Dictionary loader
-----------------

:class:`liquid.DictLoader` and :class:`liquid.CachingDictLoader` are template loaders that
store template source text in memory using a dictionary.

Pass a dictionary mapping template names to template source text to the ``DictLoader``
constructor.

.. code-block:: python

    from liquid import DictLoader, Environment

    env = Environment(
        loader=DictLoader(
            {
                "index": "{% render 'header' %}\nbody\n{% render 'footer' %}",
                "header": "some header",
                "footer": "a footer",
            }
        )
    )

    template = env.get_template("index")

    print(template.render())
    # some header
    # body
    # a footer

File system loader
------------------

:class:`liquid.FileSystemLoader` and :class:`liquid.CachingFileSystemLoader` are template
loaders that read source text from files on a file system. Both accept a `search_path`,
which can be a string, :class:`~pathlib.Path` or a list of strings and :class:`~pathlib.Path`.

.. code-block:: python

    from liquid import Environment, FileSystemLoader

    env = Environment(
        loader=FileSystemLoader(
            "path/to/templates/",
            ext=".liquid",
            reject_symlinks=True,
        )
    )

    # Look for `path/to/templates/index.liquid`
    template = env.get_template("index")

Package loader
--------------

:class:`liquid.PackageLoader` is a template loader that reads template source text from
Python packages installed in your Python environment. You should pass the name of the
package and, optionally, one or more paths to directories containing template source text
within the package. The default `package_path` is ``templates``.

.. code-block:: python

    from liquid import Environment, PackageLoader

    loader = PackageLoader(
        "awesome_templates",
        package_path="path/to/templates",
        ext=".liquid",
    )

    env = Environment(loader=loader)

Choice loader
-------------

:class:`liquid.ChoiceLoader` and :class:`liquid.CachingChoiceLoader` are template loaders
that delegate to a list of other template loaders. Each one is tried in turn until a
template is found or a :class:`liquid.TemplateNotFound` exception is raised.

When using ``CachingChoiceLoader``, you should probably avoid delegating to other caching
loaders.

.. code-block:: python

    from liquid import ChoiceLoader, DictLoader, Environment, FileSystemLoader

    base_loader = DictLoader({"foo": "some template source text"})
    overlay_loader = FileSystemLoader("templates/")
    loader = ChoiceLoader([overlay_loader, base_loader])

    env = Environment(loader=loader)

Custom loaders
--------------

Implement your own template loader by extending :class:`liquid.Loader` and overriding
:meth:`liquid.Loader.get_source`.

This example implements a front matter loader that reads YAML formatted data.

.. code-block:: python

    import re

    import yaml

    from liquid import CachingFileSystemLoader, Environment, RenderContext, TemplateSource

    RE_FRONT_MATTER = re.compile(r"\s*---\s*(.*?)\s*---\s*", re.MULTILINE | re.DOTALL)


    class FrontMatterLoader(CachingFileSystemLoader):
        def get_source(
            self,
            env: Environment,
            name: str,
            context: RenderContext | None = None,
            **kwargs: object,
        ) -> TemplateSource:
            source = super().get_source(env, name)
            match = RE_FRONT_MATTER.search(source.text)

            if match:
                # TODO: add some yaml error handling here.
                source.matter = yaml.load(match.group(1), Loader=yaml.SafeLoader)
                source.text = source.text[match.end() :]

            return source


Load context
^^^^^^^^^^^^

Sometimes a template loader will need more than a name or identifier to find the correct
source text and meta data. For these situations :meth:`liquid.Loader.get_source` accepts
the active :class:`liquid.RenderContext`, if one is available, and arbitrary keyword
arguments that the loader can use to narrow the search space.

By convention, built-in tags ``{% render %}``, ``{% include %}`` and ``{% extends %}``
pass ``tag="render"``, ``tag="include"`` and ``tag="extends"`` to :meth:`liquid.Loader.get_source`,
respectively. We can use this convention to mimic Shopify's "snippets" behavior, where
``{% render %}`` and ``{% include %}`` automatically load templates from a `snippets` subfolder.

.. code-block:: python

    from pathlib import Path

    from liquid import CachingFileSystemLoader, Environment, RenderContext, TemplateSource


    class SnippetsFileSystemLoader(CachingFileSystemLoader):
        def get_source(
            self,
            env: Environment,
            name: str,
            context: RenderContext | None = None,
            **kwargs: object,
        ) -> TemplateSource:
            if kwargs.get("tag") in ("include", "render"):
                snippet = Path("snippets").joinpath(name)
                return super().get_source(env, name=str(snippet), context=context, **kwargs)
            return super().get_source(env, name=name, context=context, **kwargs)


