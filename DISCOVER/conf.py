import json
import os

version = os.environ.get("WEBSITE_VERSION", "dev")
language = os.environ.get("WEBSITE_LANGUAGE", "en")

baseurl = 'https://discover-cookbook.numfocus.org'

# Load language data from languages.json
language_json_path = os.path.join(os.path.dirname(__file__), '_static', 'languages.json')
language_data = []
current_language_name = None
if os.path.exists(language_json_path):
    with open(language_json_path, 'r', encoding='utf-8') as f:
        all_languages = json.load(f)

# Get the current language name 
current_language_name = next((lang['name_local'] for lang in all_languages if lang['code'] == language), language)

# Filter out hidden languages for the dropdown
language_data = [lang for lang in all_languages if not lang.get('hidden', False)]

html_context = {
    "languages": language_data,
    "current_language_name": current_language_name,
    "current_language": language,
    "current_version": version,
    "baseurl": baseurl
}

html_baseurl = baseurl

author = 'Community'
comments_config = {'hypothesis': False, 'utterances': False}
copyright = '2023'
exclude_patterns = ['**.ipynb_checkpoints', '.DS_Store', 'Thumbs.db', '_build']
extensions = ['sphinx_togglebutton', 'sphinx_copybutton', 'myst_nb', 'jupyter_book', 'sphinx_external_toc', 'sphinx.ext.intersphinx', 'sphinx_design', 'sphinx_book_theme', 'sphinx_tags', 'sphinx_jupyterbook_latex', 'sphinx_multitoc_numbering']
external_toc_exclude_missing = False
external_toc_path = '_toc.yml'
html_baseurl = ''
html_favicon = ''
html_logo = 'logo.png'
html_sourcelink_suffix = ''
html_static_path = ['_static']
html_theme = 'sphinx_book_theme'
templates_path = ["_templates"]
html_theme_options = {
    'search_bar_text': 'Search this book...', 
    'launch_buttons': {'notebook_interface': 'classic', 'binderhub_url': '', 'jupyterhub_url': '', 'thebe': False, 'colab_url': '', 'deepnote_url': ''}, 
    'path_to_docs': 'DISCOVER', 
    'repository_url': 'https://github.com/numfocus/DISCOVER-Cookbook/', 
    'repository_branch': 'main', 
    'extra_footer': '', 
    'home_page_in_toc': True, 
    'announcement': '', 
    'analytics': {'google_analytics_id': '', 'plausible_analytics_domain': '', 'plausible_analytics_url': 'https://plausible.io/js/script.js'}, 
    'use_repository_button': True, 
    'use_edit_page_button': False, 
    'use_issues_button': True,
    "article_header_start": ["toggle-primary-sidebar","version-switcher","language-switcher"],
    "navigation_with_keys": False,
    "show_version_warning_banner": True,
    "switcher": {
        "json_url": "https://discover-cookbook.numfocus.org/versions.json", 
        "version_match": version,
    },
}

html_title = 'DISCOVER'
latex_engine = 'pdflatex'
myst_enable_extensions = ['colon_fence', 'dollarmath', 'linkify', 'substitution', 'tasklist']
myst_url_schemes = ['mailto', 'http', 'https']
nb_execution_allow_errors = False
nb_execution_cache_path = ''
nb_execution_excludepatterns = []
nb_execution_in_temp = False
nb_execution_mode = 'force'
nb_execution_timeout = 30
nb_output_stderr = 'show'
numfig = True
pygments_style = 'sphinx'
suppress_warnings = ['etoc.toctree']
tags_create_tags = True
tags_extension = ['md']
use_jupyterbook_latex = True
use_multitoc_numbering = True