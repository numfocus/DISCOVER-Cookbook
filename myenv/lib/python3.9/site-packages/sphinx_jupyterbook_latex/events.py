import sys
from typing import cast

from sphinx.application import Sphinx
from sphinx.builders.latex import LaTeXBuilder
from sphinx.config import Config
from sphinx.util import logging
from sphinx.util.fileutil import copy_asset_file

from . import __version__, theme
from .transforms import (
    LatexRootDocPostTransforms,
    MystNbPostTransform,
    _check_mystnb_dependency,
)

if sys.version_info < (3, 9):
    import importlib_resources as resources
else:
    import importlib.resources as resources

logger = logging.getLogger(__name__)


def override_latex_config(app: Sphinx, config: Config) -> None:
    """This ``config-inited`` event overrides aspects of the sphinx latex config.

    - ``latex_engine`` -> ``xelatex``
    - ``latex_theme`` -> ``jupyterBook``
    - appends necessary LaTeX commands to the preamble

    """
    # only allow latex builder to access rest of the features
    config["latex_engine"] = "xelatex"
    config["latex_theme"] = "jupyterBook"
    config["numfig"] = True

    latex_elements = cast(dict, config["latex_elements"])

    # preamble to overwrite things from sphinx latex writer
    config_preamble = (
        latex_elements["preamble"] if "preamble" in config["latex_elements"] else ""
    )

    latex_elements["preamble"] = (
        config_preamble
        + r"""
        % Start of preamble defined in sphinx-jupyterbook-latex %
         \usepackage[Latin,Greek]{ucharclasses}
        \usepackage{unicode-math}
        % fixing title of the toc
        \addto\captionsenglish{\renewcommand{\contentsname}{Contents}}
        \hypersetup{
            pdfencoding=auto,
            psdextra
        }
        % End of preamble defined in sphinx-jupyterbook-latex %
        """
    )

    # at the moment, True means list for this config
    if isinstance(config["jblatex_show_tocs"], bool) and config["jblatex_show_tocs"]:  # noqa: E501
        config["jblatex_show_tocs"] = "list"


def setup_latex_transforms(app: Sphinx) -> None:
    """This ``builder-inited`` event sets up aspects of the extension,
    reserved only for when a LaTeX builder is specified.
    """

    if not isinstance(app.builder, LaTeXBuilder):
        return

    # note: bold is a dynamically created function
    from sphinx.util.console import bold

    # decide whether we will convert top-level toctree captions to parts
    app.env.jblatex_captions_to_parts = False
    app.env.img_converter_ext = False

    if app.config["jblatex_captions_to_parts"] is True:
        app.config["latex_toplevel_sectioning"] = "part"
        app.config["numfig_secnum_depth"] = 2  # equation number with chapter numbers
        app.env.jblatex_captions_to_parts = True
    elif app.config["jblatex_captions_to_parts"] is None:
        # if using the sphinx-external-toc, we can look if parts are being specified
        # TODO this should probably be made more robust
        sitemap = getattr(app.config, "external_site_map", None)
        if sitemap is not None:
            if sitemap.file_format == "jb-book" and len(sitemap.root.subtrees) > 1:
                app.config["latex_toplevel_sectioning"] = "part"
                app.config[
                    "numfig_secnum_depth"
                ] = 2  # equation number with chapter numbers
                app.env.jblatex_captions_to_parts = True
            elif sitemap.file_format == "jb-book":
                app.config["latex_toplevel_sectioning"] = "chapter"
            elif sitemap.file_format == "jb-article":
                app.config["latex_toplevel_sectioning"] = "section"

    # Copy the class theme to the output directory.
    # note: importlib.resources is the formal method to access files within packages
    with resources.as_file(resources.files(theme).joinpath("jupyterBook.cls")) as path:
        copy_asset_file(str(path), app.outdir)

    # only load when myst-nb is present
    if _check_mystnb_dependency():
        app.add_post_transform(MystNbPostTransform)

    if app.config["jblatex_load_imgconverter"]:
        app.setup_extension("sphinx.ext.imgconverter")
        app.env.img_converter_ext = "sphinx.ext.imgconverter"

    logger.info(
        bold("sphinx-jupyterbook-latex v%s:")
        + "engine='%s', toplevel_section='%s', imgconverter='%s', show_tocs='%s'",
        __version__,
        app.config["latex_engine"],
        app.config["latex_toplevel_sectioning"],
        app.env.img_converter_ext,
        app.config["jblatex_show_tocs"],
    )

    app.add_post_transform(LatexRootDocPostTransforms)
