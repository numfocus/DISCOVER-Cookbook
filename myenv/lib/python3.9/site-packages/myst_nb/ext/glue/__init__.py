"""Functionality for storing special data in notebook code cells,
which can then be inserted into the document body.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import IPython
from IPython.display import display as ipy_display
from nbformat import NotebookNode

from myst_nb.core.loggers import LoggerType

if TYPE_CHECKING:
    from sphinx.application import Sphinx

    from myst_nb.docutils_ import DocutilsApp

GLUE_PREFIX = "application/papermill.record/"


def load_glue_sphinx(app: Sphinx) -> None:
    """Load the eval domain."""
    from .directives import PasteAnyDirective
    from .domain import NbGlueDomain
    from .roles import PasteRoleAny

    app.add_directive("glue", PasteAnyDirective, override=True)
    app.add_role("glue", PasteRoleAny(), override=True)
    app.add_domain(NbGlueDomain)


def load_glue_docutils(app: DocutilsApp) -> None:
    from .directives import (
        PasteAnyDirective,
        PasteFigureDirective,
        PasteMarkdownDirective,
        PasteMathDirective,
    )
    from .roles import PasteMarkdownRole, PasteRoleAny, PasteTextRole

    for name, role in [
        ("glue", PasteRoleAny()),
        ("glue:", PasteRoleAny()),
        ("glue:any", PasteRoleAny()),
        ("glue:text", PasteTextRole()),
        ("glue:md", PasteMarkdownRole()),
    ]:
        app.roles[name] = role

    for name, directive in [
        ("glue", PasteAnyDirective),
        ("glue:", PasteAnyDirective),
        ("glue:any", PasteAnyDirective),
        ("glue:figure", PasteFigureDirective),
        ("glue:math", PasteMathDirective),
        ("glue:md", PasteMarkdownDirective),
    ]:
        app.directives[name] = directive


def glue(name: str, variable: Any, display: bool = True) -> None:
    """Glue a variable into the notebook's cell metadata.

    Parameters
    ----------
    name: string
        A unique name for the variable. You can use this name to refer to the variable
        later on.
    variable: Python object
        A variable in Python for which you'd like to store its display value. This is
        not quite the same as storing the object itself - the stored information is
        what is *displayed* when you print or show the object in a Jupyter Notebook.
    display: bool
        Display the object you are gluing. This is helpful in sanity-checking the
        state of the object at glue-time.
    """
    mimebundle, metadata = IPython.core.formatters.format_display_data(variable)
    mime_prefix = "" if display else GLUE_PREFIX
    metadata["scrapbook"] = dict(name=name, mime_prefix=mime_prefix)
    ipy_display(
        {mime_prefix + k: v for k, v in mimebundle.items()}, raw=True, metadata=metadata
    )


def extract_glue_data(
    notebook: NotebookNode,
    source_map: list[int],
    logger: LoggerType,
) -> dict[str, NotebookNode]:
    """Extract all the glue data from the notebook."""
    # note this assumes v4 notebook format
    data: dict[str, NotebookNode] = {}
    for index, cell in enumerate(notebook.cells):
        if cell.cell_type != "code":
            continue
        for key, cell_data in extract_glue_data_cell(cell):
            if key in data:
                logger.warning(
                    f"glue key {key!r} duplicate",
                    subtype="glue",
                    line=source_map[index],
                )
            data[key] = cell_data

    return data


def extract_glue_data_cell(cell: NotebookNode) -> list[tuple[str, NotebookNode]]:
    """Extract glue data from a single cell."""
    outputs = []
    data = []
    for output in cell.get("outputs", []):
        meta = output.get("metadata", {})
        if "scrapbook" not in meta:
            outputs.append(output)
            continue
        key = meta["scrapbook"]["name"]
        mime_prefix = len(meta["scrapbook"].get("mime_prefix", ""))
        output["data"] = {k[mime_prefix:]: v for k, v in output["data"].items()}
        data.append((key, output))
        if not mime_prefix:
            # assume that the output is a displayable object
            outputs.append(output)
        cell.outputs = outputs
    return data
