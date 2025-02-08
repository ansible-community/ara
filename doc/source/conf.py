# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import sys

import pbr.version
import sphinx_rtd_theme

version_info = pbr.version.VersionInfo("ara")

sys.path.insert(0, os.path.abspath("../.."))
# -- General configuration ----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ["sphinxcontrib.programoutput", "sphinx.ext.autodoc", "sphinx.ext.autosectionlabel"]
autosectionlabel_prefix_document = True

# autodoc generation is a bit aggressive and a nuisance when doing heavy
# text edit cycles.
# execute "export SPHINX_DEBUG=1" in your terminal to disable

# The suffix of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "ara"
copyright = "2024, ARA Records Ansible authors"
author = "ARA Records Ansible authors"

# The short X.Y version.
version = version_info.version_string()
# The full version, including alpha/beta/rc tags.
release = version_info.release_string()

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "default"

# -- Options for HTML output --------------------------------------------------

# The theme to use for HTML and HTML Help pages.  Major themes that come with
# Sphinx are currently 'default' and 'sphinxdoc'.
html_theme = "sphinx_rtd_theme"
html_theme_path = []
html_static_path = ["_static"]

# Output file base name for HTML help builder.
htmlhelp_basename = "%sdoc" % project

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto/manual]).
latex_documents = [
    ("index", "%s.tex" % project, "%s Documentation" % project, "ARA Records Ansible authors", "manual"),
]

# Example configuration for intersphinx: refer to the Python standard library.
# intersphinx_mapping = {'http://docs.python.org/': None}
