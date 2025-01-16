""" """


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sphinx.application import Sphinx

__version__ = "1.0.0"
"""sphinx-jupyterbook-latex version"""


def setup(app: "Sphinx") -> None:
    """The sphinx entry-point for the extension."""

    from .events import override_latex_config, setup_latex_transforms
    from .nodes import CellInput, CellOutput, HiddenCellNode, RootHeader
    from .transforms import (
        CodeBlockTransforms,
        LatexRootDocTransforms,
        LatexToctreeNodeInterpret,
        ListTableOfContents,
        _check_mystnb_dependency,
    )

    # autoload the sphinx.ext.imgconverter extension
    app.add_config_value("jblatex_load_imgconverter", True, "env")
    app.add_config_value("jblatex_show_tocs", True, "env", (str, bool))
    # turn root level toctree captions into top-level `part` headings
    # If None, auto-infer whether to do this, or specifically specify
    app.add_config_value("jblatex_captions_to_parts", None, "env", (type(None), bool))

    HiddenCellNode.add_node(app)
    RootHeader.add_node(app)
    CellOutput.add_node(app)
    CellInput.add_node(app)

    app.add_transform(LatexRootDocTransforms)
    app.add_transform(LatexToctreeNodeInterpret)

    if _check_mystnb_dependency():
        app.add_post_transform(CodeBlockTransforms)

    app.add_post_transform(ListTableOfContents)

    app.connect("config-inited", override_latex_config)
    app.connect("builder-inited", setup_latex_transforms)
