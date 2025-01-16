"""Roles which can be used by both docutils and sphinx.

We intentionally do no import sphinx in this module,
in order to allow docutils-only use without sphinx installed.
"""
from __future__ import annotations

from docutils import nodes

from myst_nb.core.render import MimeData
from myst_nb.core.variables import (
    RetrievalError,
    format_plain_text,
    render_variable_outputs,
)
from myst_nb.ext.utils import RoleBase

from .utils import (
    PendingGlueReferenceError,
    create_pending_glue_ref,
    glue_warning,
    retrieve_glue_data,
)


class PasteRoleAny(RoleBase):
    """A role for pasting inline code outputs from notebooks,
    using render priority to decide the output mime type.
    """

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        # check if this is a pending reference
        doc_key = self.text.split("::", 1)
        if len(doc_key) == 2:
            doc, key = doc_key
            try:
                ref = create_pending_glue_ref(
                    self.document, self.source, self.line, doc, key, inline=True
                )
            except PendingGlueReferenceError as exc:
                return [], [
                    glue_warning(
                        str(exc),
                        self.document,
                        self.line,
                    )
                ]
            return [ref], []

        try:
            data = retrieve_glue_data(self.document, self.text)
        except RetrievalError as exc:
            return [], [glue_warning(str(exc), self.document, self.line)]
        paste_nodes = render_variable_outputs(
            [data],
            self.document,
            self.line,
            self.source,
            inline=True,
        )
        return paste_nodes, []


class PasteTextRole(RoleBase):
    """A role for pasting text/plain outputs from notebooks.

    The role content should follow the format: ``<docpath>::<key>:<format_spec>``, where:

    - ``<docpath>`` (optional) is the relative path to another notebook, defaults to local.
    - ``<key>`` is the key
    - ``<format_spec>`` (optional) is a format specifier,
      defined in: https://docs.python.org/3/library/string.html#format-specification-mini-language,
      it must end in the type character.
    """

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        # check if we have both key:format in the key
        key_format = self.text.rsplit(":", 1)
        if len(key_format) == 2:
            key, fmt_spec = key_format
        else:
            key = key_format[0]
            fmt_spec = "s"

        # check if this is a pending reference
        doc_key = key.split("::", 1)
        if len(doc_key) == 2:
            doc, key = doc_key
            try:
                ref = create_pending_glue_ref(
                    self.document,
                    self.source,
                    self.line,
                    doc,
                    key,
                    inline=True,
                    gtype="text",
                    fmt_spec=fmt_spec,
                )
            except PendingGlueReferenceError as exc:
                return [], [
                    glue_warning(
                        str(exc),
                        self.document,
                        self.line,
                    )
                ]
            return [ref], []

        # now retrieve the data

        try:
            result = retrieve_glue_data(self.document, key)
        except RetrievalError as exc:
            return [], [
                glue_warning(
                    f"{exc} (use `path::key`, to glue from another document)",
                    self.document,
                    self.line,
                )
            ]
        if "text/plain" not in result.data:
            return [], [
                glue_warning(
                    f"No text/plain found in {key!r} data", self.document, self.line
                )
            ]

        try:
            text = format_plain_text(result.data["text/plain"], fmt_spec)
        except Exception as exc:
            return [], [
                glue_warning(
                    f"Failed to format text/plain data: {exc}", self.document, self.line
                )
            ]
        node = nodes.inline(text, text, classes=["pasted-text"])
        self.set_source_info(node)
        return [node], []


class PasteMarkdownRole(RoleBase):
    """A role for pasting markdown outputs from notebooks as inline MyST Markdown."""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        # check if we have both key:format in the key
        parts = self.text.rsplit(":", 1)
        if len(parts) == 2:
            key, fmt = parts
        else:
            key = parts[0]
            fmt = "commonmark"
        # TODO - check fmt is valid
        # retrieve the data

        try:
            result = retrieve_glue_data(self.document, key)
        except RetrievalError as exc:
            return [], [glue_warning(str(exc), self.document, self.line)]
        if "text/markdown" not in result.data:
            return [], [
                glue_warning(
                    f"No text/markdown found in {key!r} data",
                    self.document,
                    self.line,
                )
            ]

        # TODO this feels a bit hacky
        cell_key = result.nb_renderer.renderer.nb_config.cell_metadata_key
        mime = MimeData(
            "text/markdown",
            result.data["text/markdown"],
            cell_metadata={
                cell_key: {"markdown_format": fmt},
            },
            output_metadata=result.metadata,
            line=self.line,
        )
        _nodes = result.nb_renderer.render_markdown_inline(mime)
        for node in _nodes:
            self.set_source_info(node)
        return _nodes, []
