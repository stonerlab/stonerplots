# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
from pathlib import Path

modpath = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(modpath))

print(sys.path)

project = "StonerPlots"
copyright = "2024, University of Leeds"
author = "Gavin Burnell"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_automodapi.automodapi",
    "sphinx_automodapi.smart_resolver",
]
numpydoc_show_class_members = False

templates_path = ["_templates"]
exclude_patterns = []

intersphinx_mapping = {
    "Python 3 [3.111]": ("https://docs.python.org/3.11/", None),
    "matplotlib [stable]": ("https://matplotlib.org/stable/", None),
    "numpy [stable]": ("https://numpy.org/doc/stable/", None),
    "Sphinx [master]": ("https://www.sphinx-doc.org/en/master/", None),
    "scipy [latest]": ("https://docs.scipy.org/doc/scipy/", None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
html_logo = "figures/StonerLogo2.png"
