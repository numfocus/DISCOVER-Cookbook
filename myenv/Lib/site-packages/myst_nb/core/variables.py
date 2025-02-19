"""Utilities for rendering code output variables."""
from __future__ import annotations

from ast import literal_eval
import dataclasses as dc
from typing import Any

from docutils import nodes

from myst_nb._compat import findall
from myst_nb.core.loggers import DocutilsDocLogger, SphinxDocLogger
from myst_nb.core.render import MimeData, NbElementRenderer, get_mime_priority


def is_sphinx(document: nodes.document) -> bool:
    """Return True if we are in sphinx, otherwise docutils."""
    return hasattr(document.settings, "env")


def create_warning(
    message: str, document: nodes.document, line: int, subtype: str
) -> nodes.system_message:
    """Create a warning."""
    logger: DocutilsDocLogger | SphinxDocLogger
    if is_sphinx(document):
        logger = SphinxDocLogger(document)
    else:
        logger = DocutilsDocLogger(document)
    logger.warning(message, line=line, subtype=subtype)
    return nodes.system_message(
        message,
        type="WARNING",
        level=2,
        line=line,
        source=document["source"],
    )


def set_source_info(node: nodes.Node, source: str, line: int) -> None:
    """Set the source info for a node and its descendants."""
    for _node in findall(node)(include_self=True):
        _node.source = source
        _node.line = line


class RetrievalError(Exception):
    """An error occurred while retrieving the variable output."""


@dc.dataclass()
class VariableOutput:
    """A class to store display_data/execute_result output for a variable."""

    data: dict[str, Any]
    """the mime-bundle: mime-type -> data"""
    metadata: dict[str, Any]
    nb_renderer: NbElementRenderer
    vtype: str
    """The variable type (for use in warnings)."""
    index: int = 0
    """The index of the output."""


def render_variable_outputs(
    outputs: list[VariableOutput],
    document: nodes.document,
    line: int,
    source: str,
    *,
    inline: bool = False,
    render: dict[str, Any] | None = None,
) -> list[nodes.Node]:
    """Given output data for a variable,
    return the docutils/sphinx nodes relevant to this data.

    :param outputs: The output data.
    :param document: The current docutils document.
    :param line: The current source line number of the directive or role.
    :param source: The current source path or description.
    :param inline: Whether to render the output as inline (or block).
    :param render: Cell-level render metadata.

    :returns: the docutils/sphinx nodes
    """
    _nodes = []
    for output in outputs:
        _nodes.extend(
            _render_variable_output(
                output,
                document,
                line,
                source,
                inline=inline,
                render=render,
            )
        )
    return _nodes


def _render_variable_output(
    output: VariableOutput,
    document: nodes.document,
    line: int,
    source: str,
    *,
    inline: bool = False,
    render: dict[str, Any] | None = None,
) -> list[nodes.Node]:
    cell_metadata = {}
    if render:
        cell_metadata[output.nb_renderer.config.cell_metadata_key] = render
    if is_sphinx(document):
        _nodes = _render_output_sphinx(
            output,
            cell_metadata,
            source,
            line,
            inline,
        )
    else:
        _nodes = _render_output_docutils(
            output,
            cell_metadata,
            document,
            line,
            inline,
        )
    # TODO rendering should perhaps return if it succeeded explicitly,
    # and whether system_messages or not (required for roles)
    return _nodes


def _render_output_docutils(
    output: VariableOutput,
    cell_metadata: dict[str, Any],
    document: nodes.document,
    line: int,
    inline=False,
) -> list[nodes.Node]:
    """Render the output in docutils (select mime priority directly)."""
    mime_priority = get_mime_priority(
        output.nb_renderer.config.builder_name,
        output.nb_renderer.config.mime_priority_overrides,
    )
    try:
        mime_type = next(x for x in mime_priority if x in output.data)
    except StopIteration:
        if output.data:
            return [
                create_warning(
                    "No output mime type found from render_priority "
                    f"(output<{output.index}>)",
                    document,
                    line,
                    output.vtype,
                )
            ]
        return []
    else:
        mime_data = MimeData(
            mime_type,
            output.data[mime_type],
            cell_metadata=cell_metadata,
            output_metadata=output.metadata,
            line=line,
        )
        if inline:
            return output.nb_renderer.render_mime_type_inline(mime_data)
        return output.nb_renderer.render_mime_type(mime_data)


def _render_output_sphinx(
    output: VariableOutput,
    cell_metadata: dict[str, Any],
    source: str,
    line: int,
    inline=False,
) -> list[nodes.Node]:
    """Render the output in sphinx (defer mime priority selection)."""
    mime_bundle = nodes.container(nb_element="mime_bundle")
    set_source_info(mime_bundle, source, line)
    for mime_type, content in output.data.items():
        mime_container = nodes.container(mime_type=mime_type)
        set_source_info(mime_container, source, line)
        mime_data = MimeData(
            mime_type,
            content,
            cell_metadata=cell_metadata,
            output_metadata=output.metadata,
            line=line,
        )
        if inline:
            _nodes = output.nb_renderer.render_mime_type_inline(mime_data)
        else:
            _nodes = output.nb_renderer.render_mime_type(mime_data)
        if _nodes:
            mime_container.extend(_nodes)
            mime_bundle.append(mime_container)
    return [mime_bundle]


def format_plain_text(text: str, fmt_spec: str) -> str:
    """Format plain text for display in a docutils node."""
    # literal eval, to remove surrounding quotes
    try:
        value = literal_eval(text)
    except (SyntaxError, ValueError):
        value = text
    if fmt_spec == "":
        return str(value)
    type_char = fmt_spec[-1]
    if type_char == "s":
        value = str(value)
    elif type_char in ("b", "c", "d", "o", "x", "X"):
        value = int(value)
    elif type_char in ("e", "E", "f", "F", "g", "G", "n", "%"):
        value = float(value)
    return format(value, fmt_spec)
