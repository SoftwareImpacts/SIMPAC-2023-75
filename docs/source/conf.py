# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# ----- Agrego la ruta para importar el paquete -------------------------------
import dicomhandler

sys.path.insert(0, os.path.abspath("../.."))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "dicomhandler"
copyright = "2022, Jerónimo Fotinós, Alejandro Rojas, Nicola Maddalozzo"
author = "Jerónimo Fotinós, Alejandro Rojas, Nicola Maddalozzo"
release = dicomhandler.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "nbsphinx",
    "sphinxcontrib.bibtex",
]
# =============================================================================
# BIB TEX
# =============================================================================

bibtex_default_style = "apa"  # pybtex-apa-style

bibtex_bibfiles = ["refs.bib"]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
