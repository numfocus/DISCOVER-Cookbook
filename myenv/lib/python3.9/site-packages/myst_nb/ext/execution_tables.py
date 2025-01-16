"""Sphinx elements to create tables of statistics on executed notebooks.

The `nb-exec-table` directive adds a placeholder node to the document,
which is then replaced by a table of statistics in a post-transformation
(once all the documents have been executed and these statistics are available).
"""
from __future__ import annotations

from datetime import datetime
import posixpath
from typing import Any, Callable, DefaultDict

from docutils import nodes
from sphinx.addnodes import pending_xref
from sphinx.application import Sphinx
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

from myst_nb._compat import findall
from myst_nb.sphinx_ import NbMetadataCollector, SphinxEnvType

SPHINX_LOGGER = logging.getLogger(__name__)

METADATA_KEY = "has_exec_table"


def setup_exec_table_extension(app: Sphinx) -> None:
    """Add the Sphinx extension to the Sphinx application."""
    app.add_node(ExecutionStatsNode)
    app.add_directive("nb-exec-table", ExecutionStatsTable)
    app.connect("env-updated", update_exec_tables)
    app.add_post_transform(ExecutionStatsPostTransform)


class ExecutionStatsNode(nodes.General, nodes.Element):
    """A placeholder node, for adding a notebook execution statistics table."""


class ExecutionStatsTable(SphinxDirective):
    """Add a notebook execution statistics table."""

    has_content = True
    final_argument_whitespace = True

    def run(self):
        """Add a placeholder node to the document, and mark it as having a table."""
        self.env: SphinxEnvType
        NbMetadataCollector.set_doc_data(self.env, self.env.docname, METADATA_KEY, True)
        return [ExecutionStatsNode()]


def update_exec_tables(app: Sphinx, env: SphinxEnvType):
    """If a document has been re-executed, return all documents containing tables.

    These documents will be updated with the new statistics.
    """
    if not NbMetadataCollector.new_exec_data(env):
        return None
    to_update = [
        docname
        for docname, data in NbMetadataCollector.get_doc_data(env).items()
        if data.get(METADATA_KEY)
    ]
    if to_update:
        SPHINX_LOGGER.info(
            f"Updating {len(to_update)} file(s) with execution table [mystnb]"
        )
    return to_update


class ExecutionStatsPostTransform(SphinxPostTransform):
    """Replace the placeholder node with the final table nodes."""

    default_priority = 8  # before ReferencesResolver (10) and MystReferenceResolver(9)

    def run(self, **kwargs) -> None:
        """Replace the placeholder node with the final table nodes."""
        self.env: SphinxEnvType
        for node in findall(self.document)(ExecutionStatsNode):
            node.replace_self(
                make_stat_table(
                    self.env.docname, NbMetadataCollector.get_doc_data(self.env)
                )
            )


_key2header: dict[str, str] = {
    "mtime": "Modified",
    "method": "Method",
    "runtime": "Run Time (s)",
    "succeeded": "Status",
}

_key2transform: dict[str, Callable[[Any], str]] = {
    "mtime": lambda x: datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M")
    if x
    else "",
    "method": str,
    "runtime": lambda x: "-" if x is None else str(round(x, 2)),
    "succeeded": lambda x: "✅" if x is True else "❌",
}


def make_stat_table(
    parent_docname: str, metadata: DefaultDict[str, dict]
) -> nodes.table:
    """Create a table of statistics on executed notebooks."""

    # top-level element
    table = nodes.table()
    table["classes"] += ["colwidths-auto"]
    # self.set_source_info(table)

    # column settings element
    ncols = len(_key2header) + 1
    tgroup = nodes.tgroup(cols=ncols)
    table += tgroup
    colwidths = [round(100 / ncols, 2)] * ncols
    for colwidth in colwidths:
        colspec = nodes.colspec(colwidth=colwidth)
        tgroup += colspec

    # header
    thead = nodes.thead()
    tgroup += thead
    row = nodes.row()
    thead += row

    for name in ["Document"] + list(_key2header.values()):
        row.append(nodes.entry("", nodes.paragraph(text=name)))

    # body
    tbody = nodes.tbody()
    tgroup += tbody

    for docname in sorted(metadata):
        data = metadata[docname].get("exec_data")
        if not data:
            continue
        row = nodes.row()
        tbody += row

        # document name
        doclink = pending_xref(
            refdoc=parent_docname,
            reftarget=posixpath.relpath(docname, posixpath.dirname(parent_docname)),
            reftype="doc",
            refdomain="std",
            refexplicit=True,
            refwarn=True,
            classes=["xref", "doc"],
        )
        doclink += nodes.inline(text=docname)
        paragraph = nodes.paragraph()
        paragraph += doclink
        row.append(nodes.entry("", paragraph))

        # other rows
        for name in _key2header.keys():
            paragraph = nodes.paragraph()
            if name == "succeeded" and data[name] is False:
                paragraph += nodes.abbreviation(
                    text=_key2transform[name](data[name]),
                    explanation=(data["error"] or ""),
                )
            else:
                paragraph += nodes.Text(_key2transform[name](data[name]))
            row.append(nodes.entry("", paragraph))

    return table
