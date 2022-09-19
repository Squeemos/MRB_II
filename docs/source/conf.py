# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
sys.path.insert(0, os.path.abspath('../../..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'MRB_II'
copyright = '2022, Ben van Oostendorp and Eric Zander'
author = 'Ben van Oostendorp and Eric Zander'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

css_font_family = "Arial, Helvetica, sans-serif"

# Theme options
html_theme_options = {
    "logo": "temp_icon.png",
    # "logo_name": True,
    # "logo_text_align": "center",

    # "github_user": "Squeemos",
    # "github_repo": "MRB_II",
    # "github_button": True,
    # "github_type": "star",

    # "caption_font_size": ,
    # "caption_font_family": ,

    # "code_font_size": ,
    # "code_font_family": ,

    "font_family": css_font_family,

    # "font_size": ,
    "head_font_family": css_font_family,
}
