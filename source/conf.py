# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


project = 'DISCOVER'
author = 'Community'
copyright = '2025, Community'
release = '1.0'

# -- General Configuration ---------------------------------------------------

extensions = []
templates_path = ['_templates']
exclude_patterns = []

# -- Execution Settings ------------------------------------------------------

# Equivalent to execute_notebooks: force in Jupyter Book
jupyter_execute_notebooks = "force"

# -- Repository Settings -----------------------------------------------------

# Mapping repository info from _config.yml to conf.py
repository_url = "https://github.com/numfocus/DISCOVER-Cookbook/"
repository_branch = "main"
repository_path = "handbook"  # If applicable

# -- HTML Output Configuration ------------------------------------------------

html_theme = "alabaster"
html_static_path = ['_static']
html_logo = "logo.png"  # Equivalent to logo in _config.yml

# GitHub button settings from _config.yml
html_context = {
    "display_github": True,
    "github_user": "numfocus",
    "github_repo": "DISCOVER-Cookbook",
    "github_version": "main",
    "conf_py_path": "/handbook/"
}
