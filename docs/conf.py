# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "liquid"
copyright = "2026, James Prior"
author = "James Prior"
release = "3.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx.ext.githubpages",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

GITHUB_LOGO = """
<svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
  <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
</svg>
""".strip()

html_theme = "furo"
html_static_path = ["_static"]

_link_color_light = "#024bb0"
_link_color_dark = "#5192d2"

html_theme_options = {  # type: ignore
    # "light_logo": "logo_light.png",
    # "dark_logo": "logo_dark.png",
    "light_css_variables": {
        "color-brand-primary": "black",
        "color-brand-content": _link_color_light,
        "color-foreground-muted": "#808080",
        "color-highlight-on-target": "inherit",
        "color-highlighted-background": "#ffffcc",
        "color-sidebar-link-text": "black",
        "color-sidebar-link-text--top-level": "black",
        "color-link": _link_color_light,
        "color-link--hover": _link_color_light,
        "color-link-underline": "transparent",
        "color-link-underline--hover": _link_color_light,
    },
    "dark_css_variables": {
        "color-brand-primary": "#ffffff",
        "color-brand-content": _link_color_dark,
        "color-highlight-on-target": "inherit",
        "color-highlighted-background": "#333300",
        "color-sidebar-link-text": "#ffffffcc",
        "color-sidebar-link-text--top-level": "#ffffffcc",
        "color-link": _link_color_dark,
        "color-link--hover": _link_color_dark,
        "color-link-underline": "transparent",
        "color-link-underline--hover": _link_color_dark,
    },
    "sidebar_hide_name": True,
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/jg-rp/liquid",
            "html": GITHUB_LOGO,
            "class": "",
        },
    ],
}

# -- Options for intersphinx extension ---------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

autodoc_typehints = "signature"
napoleon_numpy_docstring = True
napoleon_google_docstring = False
napoleon_use_rtype = False
