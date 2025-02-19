"""Setup for the myst-nb sphinx extension."""
from __future__ import annotations

import contextlib
import hashlib
from importlib import resources as import_resources
import os
from pathlib import Path
import sys
from types import ModuleType
from typing import Any, Iterator, cast

from myst_parser.sphinx_ext.main import setup_sphinx as setup_myst_parser
from sphinx.application import Sphinx
from sphinx.util import logging as sphinx_logging
from sphinx.util.fileutil import copy_asset_file

from myst_nb import __version__, static
from myst_nb.core.config import NbParserConfig
from myst_nb.core.loggers import DEFAULT_LOG_TYPE
from myst_nb.core.read import UnexpectedCellDirective
from myst_nb.ext.download import NbDownloadRole
from myst_nb.ext.eval import load_eval_sphinx
from myst_nb.ext.glue import load_glue_sphinx
from myst_nb.ext.glue.crossref import ReplacePendingGlueReferences
from myst_nb.sphinx_ import (
    HideCodeCellNode,
    HideInputCells,
    NbMetadataCollector,
    Parser,
    SelectMimeType,
    SphinxEnvType,
)

SPHINX_LOGGER = sphinx_logging.getLogger(__name__)
OUTPUT_FOLDER = "jupyter_execute"

# used for deprecated config values,
# so we can tell if they have been set by a user, and warn them
_UNSET = "--unset--"


def sphinx_setup(app: Sphinx):
    """Initialize Sphinx extension."""
    # note, for core events overview, see:
    # https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx-core-events

    # Add myst-parser configuration and transforms (but does not add the parser)
    setup_myst_parser(app)

    # add myst-nb configuration variables
    for name, default, field in NbParserConfig().as_triple():
        if not field.metadata.get("sphinx_exclude"):
            # TODO add types?
            app.add_config_value(f"nb_{name}", default, "env", Any)  # type: ignore[arg-type]
            if "legacy_name" in field.metadata:
                app.add_config_value(
                    f"{field.metadata['legacy_name']}",
                    _UNSET,
                    "env",
                    Any,  # type: ignore[arg-type]
                )
    # Handle non-standard deprecation
    app.add_config_value("nb_render_priority", _UNSET, "env", Any)  # type: ignore[arg-type]

    # generate notebook configuration from Sphinx configuration
    # this also validates the configuration values
    app.connect("builder-inited", create_mystnb_config)

    # add parser and default associated file suffixes
    app.add_source_parser(Parser)
    app.add_source_suffix(".md", "myst-nb", override=True)
    app.add_source_suffix(".ipynb", "myst-nb")
    # add additional file suffixes for parsing
    app.connect("config-inited", add_nb_custom_formats)
    # ensure notebook checkpoints are excluded from parsing
    app.connect("config-inited", add_exclude_patterns)
    # add collector for myst nb specific data
    app.add_env_collector(NbMetadataCollector)

    # TODO add an event which, if any files have been removed,
    # all jupyter-cache stage records with a non-existent path are removed
    # (just to keep it "tidy", but won't affect run)

    # add directive to ensure all notebook cells are converted
    app.add_directive("code-cell", UnexpectedCellDirective, override=True)
    app.add_directive("raw-cell", UnexpectedCellDirective, override=True)

    # add directive for downloading an executed notebook
    app.add_role("nb-download", NbDownloadRole())

    # add directive for evaluating glue and kernel variables
    load_eval_sphinx(app)
    load_glue_sphinx(app)

    # add post-transform for selecting mime type from a bundle
    app.add_post_transform(SelectMimeType)
    app.add_post_transform(ReplacePendingGlueReferences)

    # setup collapsible content
    app.add_post_transform(HideInputCells)
    HideCodeCellNode.add_to_app(app)

    # add HTML resources
    add_css(app)
    app.connect("build-finished", add_global_html_resources)
    # note, this event is only available in Sphinx >= 3.5
    app.connect("html-page-context", add_per_page_html_resources)

    # Note lexers are registered as `pygments.lexers` entry-points
    # and so do not need to be added here.

    # setup extension for execution statistics tables
    # import here, to avoid circular import
    from myst_nb.ext.execution_tables import setup_exec_table_extension

    setup_exec_table_extension(app)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def add_nb_custom_formats(app: Sphinx, config):
    """Add custom conversion formats."""
    for suffix in config.nb_custom_formats:
        app.add_source_suffix(suffix, "myst-nb", override=True)


def create_mystnb_config(app):
    """Generate notebook configuration from Sphinx configuration"""

    # Ignore type checkers because the attribute is dynamically assigned
    from sphinx.util.console import bold

    values = {}
    for name, _, field in NbParserConfig().as_triple():
        if not field.metadata.get("sphinx_exclude"):
            values[name] = app.config[f"nb_{name}"]
            if "legacy_name" in field.metadata:
                legacy_value = app.config[field.metadata["legacy_name"]]
                if legacy_value != _UNSET:
                    legacy_name = field.metadata["legacy_name"]
                    SPHINX_LOGGER.warning(
                        f"{legacy_name!r} is deprecated for 'nb_{name}' "
                        f"[{DEFAULT_LOG_TYPE}.config]",
                        type=DEFAULT_LOG_TYPE,
                        subtype="config",
                    )
                    values[name] = legacy_value
    if app.config["nb_render_priority"] != _UNSET:
        SPHINX_LOGGER.warning(
            "'nb_render_priority' is deprecated for 'nb_mime_priority_overrides'"
            f"{DEFAULT_LOG_TYPE}.config",
            type=DEFAULT_LOG_TYPE,
            subtype="config",
        )

    try:
        app.env.mystnb_config = NbParserConfig(**values)
        SPHINX_LOGGER.info(
            bold("myst-nb v%s:") + " %s", __version__, app.env.mystnb_config
        )
    except (TypeError, ValueError) as error:
        SPHINX_LOGGER.critical("myst-nb configuration invalid: %s", error.args[0])
        raise

    # update the output_folder (for writing external files like images),
    # and the execution_cache_path (for caching notebook outputs)
    # to a set path within the sphinx build folder
    output_folder = Path(app.outdir).parent.joinpath(OUTPUT_FOLDER).resolve()
    exec_cache_path: None | str | Path = app.env.mystnb_config.execution_cache_path
    if not exec_cache_path:
        exec_cache_path = Path(app.outdir).parent.joinpath(".jupyter_cache").resolve()
    app.env.mystnb_config = app.env.mystnb_config.copy(
        output_folder=str(output_folder), execution_cache_path=str(exec_cache_path)
    )
    SPHINX_LOGGER.info(f"Using jupyter-cache at: {exec_cache_path}")


def add_exclude_patterns(app: Sphinx, config):
    """Add default exclude patterns (if not already present)."""
    if "**.ipynb_checkpoints" not in config.exclude_patterns:
        config.exclude_patterns.append("**.ipynb_checkpoints")


def _get_file_hash(path: Path):
    """Get the hash of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


@contextlib.contextmanager
def _import_resources_path(package: ModuleType, resource: str) -> Iterator[Path]:
    if sys.version_info < (3, 9):
        with import_resources.path(package, resource) as path:
            yield path
    else:
        with import_resources.as_file(
            import_resources.files(package).joinpath(resource)
        ) as path:
            yield path


def add_css(app: Sphinx):
    """Add CSS for myst-nb."""
    with _import_resources_path(static, "mystnb.css") as source_path:
        hash = _get_file_hash(source_path)
    app.add_css_file(f"mystnb.{hash}.css")


def add_global_html_resources(app: Sphinx, exception):
    """Add HTML resources that apply to all pages."""
    # see https://github.com/sphinx-doc/sphinx/issues/1379
    if app.builder is not None and app.builder.format == "html" and not exception:
        with _import_resources_path(static, "mystnb.css") as source_path:
            hash = _get_file_hash(source_path)
            destination = os.path.join(
                app.builder.outdir, "_static", f"mystnb.{hash}.css"
            )
            copy_asset_file(str(source_path), destination)


def add_per_page_html_resources(
    app: Sphinx, pagename: str, *args: Any, **kwargs: Any
) -> None:
    """Add JS files for this page, identified from the parsing of the notebook."""
    if app.env is None or app.builder is None or app.builder.format != "html":
        return
    js_files = NbMetadataCollector.get_js_files(cast(SphinxEnvType, app.env), pagename)
    for path, kwargs in js_files.values():
        app.add_js_file(path, **kwargs)  # type: ignore[arg-type]
