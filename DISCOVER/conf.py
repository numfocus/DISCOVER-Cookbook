import json
import os

# -------------------------------------------------
# Basic project info
# -------------------------------------------------

version = os.environ.get("WEBSITE_VERSION", "dev")
release = version
language = os.environ.get("WEBSITE_LANGUAGE", "en")

author = "Community"
copyright = "2023"

baseurl = "https://discover-cookbook.numfocus.org"
html_baseurl = baseurl

# -------------------------------------------------
# Paths & exclusions
# -------------------------------------------------

exclude_patterns = [
    "**.ipynb_checkpoints",
    ".DS_Store",
    "Thumbs.db",
    "_build",
]

locale_dirs = ["../locales"]
gettext_uuid = True
gettext_compact = False

# -------------------------------------------------
# Language switcher context
# -------------------------------------------------

language_json_path = os.path.join(
    os.path.dirname(__file__), "_static", "languages.json"
)

language_data = []
current_language_name = language

if os.path.exists(language_json_path):
    with open(language_json_path, "r", encoding="utf-8") as f:
        all_languages = json.load(f)

    current_language_name = next(
        (lang["name_local"] for lang in all_languages if lang["code"] == language),
        language,
    )

    language_data = [
        lang for lang in all_languages if not lang.get("hidden", False)
    ]

html_context = {
    "languages": language_data,
    "current_language_name": current_language_name,
    "current_language": language,
    "current_version": version,
    "baseurl": baseurl,
}

# -------------------------------------------------
# Extensions
# -------------------------------------------------

extensions = [
    "sphinx_togglebutton",
    "sphinx_copybutton",
    "myst_parser",
    "jupyter_book",
    "sphinx_external_toc",
    "sphinx.ext.intersphinx",
    "sphinx_design",
    "sphinx_book_theme",
    "sphinx_tags",
    "sphinx_jupyterbook_latex",
    "sphinx_multitoc_numbering",
]

# -------------------------------------------------
# External TOC
# -------------------------------------------------

external_toc_path = "_toc.yml"
external_toc_exclude_missing = False

# -------------------------------------------------
# Static files
# -------------------------------------------------

html_static_path = ["_static"]

html_css_files = [
    "css/mainLogo.css",
    "css/Switchers.css",
]

html_js_files = [
    "js/footer.js",
    "js/logo-switcher.js",
]

html_logo = "_static/images/logo-light.png"
html_favicon = ""

# -------------------------------------------------
# Templates
# -------------------------------------------------

templates_path = ["_templates"]

# -------------------------------------------------
# Theme
# -------------------------------------------------

html_theme = "sphinx_book_theme"

html_theme_options = {
    "search_bar_text": "Search this book...",
    "path_to_docs": "DISCOVER",
    "repository_url": "https://github.com/numfocus/DISCOVER-Cookbook/",
    "repository_branch": "main",
    "use_repository_button": True,
    "use_edit_page_button": False,
    "use_issues_button": True,

    # Header layout
    "article_header_start": [
        "toggle-primary-sidebar",
        "version-switcher",
        "language-switcher",
    ],

    "navigation_with_keys": False,
    "show_version_warning_banner": True,

    # Version switcher
    "switcher": {
        "json_url": "https://discover-cookbook.numfocus.org/versions.json",
        "version_match": version,
    },

    # IMPORTANT:
    # Footer MUST be empty here
    # It is handled in _templates/footer.html
    "extra_footer": "",
}

# -------------------------------------------------
# Page options
# -------------------------------------------------

html_title = "DISCOVER"
html_sourcelink_suffix = ""

# -------------------------------------------------
# MyST & notebooks
# -------------------------------------------------

myst_enable_extensions = [
    "colon_fence",
    "dollarmath",
    "linkify",
    "substitution",
    "tasklist",
]

myst_url_schemes = ["mailto", "http", "https"]

nb_execution_allow_errors = False
nb_execution_mode = "force"
nb_execution_timeout = 30
nb_output_stderr = "show"

# -------------------------------------------------
# Numbering & tags
# -------------------------------------------------

numfig = True
pygments_style = "sphinx"
suppress_warnings = ["etoc.toctree"]

tags_create_tags = True
tags_extension = ["md"]

use_jupyterbook_latex = True
use_multitoc_numbering = True
latex_engine = "pdflatex"
