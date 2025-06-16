version = '2.0'
language = 'en'

import json
import os

# Load language data from languages.json
language_json_path = os.path.join(os.path.dirname(__file__), '_static', 'languages.json')
language_data = []
if os.path.exists(language_json_path):
    with open(language_json_path, 'r',encoding='utf-8') as f:
        language_data = json.load(f)

language_names = {}
for lang in language_data:
    if "language" in lang and "name" in lang:
        language_names[lang["language"]] = lang["name"]


html_context = {
    "languages": language_data,
    "language_names": language_names,
    "current_language": language,
    "current_version": version
}

author = 'Community'
comments_config = {'hypothesis': False, 'utterances': False}
copyright = '2023'
exclude_patterns = ['**.ipynb_checkpoints', '.DS_Store', 'Thumbs.db', '_build']
extensions = ['sphinx_togglebutton', 'sphinx_copybutton', 'myst_nb', 'jupyter_book', 'sphinx_external_toc', 'sphinx.ext.intersphinx', 'sphinx_design', 'sphinx_book_theme', 'sphinx_tags', 'sphinx_jupyterbook_latex', 'sphinx_multitoc_numbering']
external_toc_exclude_missing = False
external_toc_path = '_toc.yml'
html_baseurl = ''
html_css_files = ['css/mainLogo.css']
html_favicon = ''
html_js_files = ['js/footer.js', 'js/logo-switcher.js']
html_logo = '_static/images/logo-light.png'
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
        "json_url": (
            "_static/versions.json"
            #  "https://discover-cookbook.numfocus.org/DISCOVER/_static/versions.json" 
        ),
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
