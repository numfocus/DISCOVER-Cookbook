"""Module for rendering notebook components to docutils nodes.

Note, this module purposely does not import any Sphinx modules at the top-level,
in order for docutils-only use.
"""
from __future__ import annotations

from binascii import a2b_base64
from contextlib import contextmanager
import dataclasses as dc
from functools import lru_cache
import hashlib
import json
from mimetypes import guess_extension
import os
from pathlib import Path
import re
from typing import TYPE_CHECKING, Any, ClassVar, Iterator, Sequence, Union

from docutils import nodes
from docutils.parsers.rst import directives as options_spec
from importlib_metadata import entry_points
from myst_parser.config.main import MdParserConfig
from myst_parser.mdit_to_docutils.base import token_line
from myst_parser.parsers.mdit import create_md_parser
from nbformat import NotebookNode
from typing_extensions import Protocol

from myst_nb.core.config import NbParserConfig
from myst_nb.core.execute import NotebookClientBase
from myst_nb.core.loggers import LoggerType  # DEFAULT_LOG_TYPE,
from myst_nb.core.utils import coalesce_streams
from myst_nb.warnings_ import MystNBWarnings, create_warning

if TYPE_CHECKING:
    from markdown_it.tree import SyntaxTreeNode

    from myst_nb.docutils_ import DocutilsNbRenderer, DocutilsRenderer
    from myst_nb.sphinx_ import SphinxNbRenderer, SphinxRenderer

    SelfType = Union["MditRenderMixin", DocutilsRenderer, SphinxRenderer]


WIDGET_STATE_MIMETYPE = "application/vnd.jupyter.widget-state+json"
WIDGET_VIEW_MIMETYPE = "application/vnd.jupyter.widget-view+json"
RENDER_ENTRY_GROUP = "myst_nb.renderers"
MIME_RENDER_ENTRY_GROUP = "myst_nb.mime_renderers"
_ANSI_RE = re.compile("\x1b\\[(.*?)([@-~])")
_QUOTED_RE = re.compile(r"^([\"']).*\1$")


class MditRenderMixin:
    """Mixin for rendering markdown-it tokens to docutils nodes.

    This has shared methods for both the `DocutilsRenderer` and `SphinxRenderer`
    """

    # required by mypy
    md_options: dict[str, Any]
    document: nodes.document
    render_children: Any
    add_line_and_source_path: Any
    add_line_and_source_path_r: Any
    current_node: Any
    current_node_context: Any
    create_highlighted_code_block: Any

    @property
    def nb_config(self: SelfType) -> NbParserConfig:
        """Get the notebook element renderer."""
        return self.md_options["nb_config"]

    @property
    def nb_client(self: SelfType) -> NotebookClientBase:
        """Get the notebook element renderer."""
        return self.md_options["nb_client"]

    @property
    def nb_renderer(self: SelfType) -> NbElementRenderer:
        """Get the notebook element renderer."""
        return self.document["nb_renderer"]

    def get_cell_level_config(
        self: SelfType,
        field: str,
        cell_metadata: dict[str, Any],
        line: int | None = None,
    ) -> Any:
        """Get a configuration value at the cell level.

        Takes the highest priority configuration from:
        `cell > document > global > default`

        :param field: the field name from ``NbParserConfig`` to get the value for
        :param cell_metadata: the metadata for the cell
        """

        def _callback(msg: str, subtype: MystNBWarnings):
            create_warning(self.document, msg, line=line, subtype=subtype)

        return self.nb_config.get_cell_level_config(field, cell_metadata, _callback)

    def render_nb_initialise(self, token: SyntaxTreeNode) -> None:
        """Run rendering at the start of the notebook."""

    def render_nb_finalise(self, token: SyntaxTreeNode) -> None:
        """Run rendering at the end of the notebook."""
        self.nb_client.finalise_client()
        self.nb_renderer.render_nb_finalise(self.nb_client.nb_metadata)

    def render_nb_cell_markdown(self: SelfType, token: SyntaxTreeNode) -> None:
        """Render a notebook markdown cell."""
        # TODO this is currently just a "pass-through", but we could utilise the metadata
        # it would be nice to "wrap" this in a container that included the metadata,
        # but unfortunately this would break the heading structure of docutils/sphinx.
        # perhaps we add an "invisible" (non-rendered) marker node to the document tree,
        self.render_children(token)

    def render_nb_cell_raw(self: SelfType, token: SyntaxTreeNode) -> None:
        """Render a notebook raw cell."""
        line = token_line(token, 0)
        _nodes = self.nb_renderer.render_raw_cell(
            token.content, token.meta["metadata"], token.meta["index"], line
        )
        self.add_line_and_source_path_r(_nodes, token)
        self.current_node.extend(_nodes)

    def render_nb_cell_code(self: SelfType, token: SyntaxTreeNode) -> None:
        """Render a notebook code cell."""
        cell_index = token.meta["index"]
        cell_line = token_line(token, 0) or None
        tags = token.meta["metadata"].get("tags", [])

        exec_count, outputs = self._get_nb_code_cell_outputs(token)

        classes = ["cell"]
        for tag in tags:
            classes.append(f"tag_{tag.replace(' ', '_')}")

        # TODO do we need this -/_ duplication of tag names, or can we deprecate one?
        hide_cell = "hide-cell" in tags
        remove_input = (
            self.get_cell_level_config(
                "remove_code_source", token.meta["metadata"], line=cell_line
            )
            or ("remove_input" in tags)
            or ("remove-input" in tags)
        )
        hide_input = "hide-input" in tags
        remove_output = (
            self.get_cell_level_config(
                "remove_code_outputs", token.meta["metadata"], line=cell_line
            )
            or ("remove_output" in tags)
            or ("remove-output" in tags)
        )
        hide_output = "hide-output" in tags

        # if we are remove both the input and output, we can skip the cell
        if remove_input and remove_output:
            return

        hide_mode = None
        if hide_cell:
            hide_mode = "all"
        elif hide_input and hide_output:
            hide_mode = "input+output"
        elif hide_input:
            hide_mode = "input"
        elif hide_output:
            hide_mode = "output"

        # create a container for all the input/output
        cell_container = nodes.container(
            nb_element="cell_code",
            cell_index=cell_index,
            # TODO some way to use this to allow repr of count in outputs like HTML?
            exec_count=exec_count,
            cell_metadata=token.meta["metadata"],
            classes=classes,
        )
        if hide_mode:
            cell_container["hide_mode"] = hide_mode
            code_prompt_show = self.get_cell_level_config(
                "code_prompt_show", token.meta["metadata"], line=cell_line
            )
            code_prompt_hide = self.get_cell_level_config(
                "code_prompt_hide", token.meta["metadata"], line=cell_line
            )
            cell_container["prompt_show"] = code_prompt_show
            cell_container["prompt_hide"] = code_prompt_hide

        self.add_line_and_source_path(cell_container, token)
        with self.current_node_context(cell_container, append=True):
            # render the code source code
            if not remove_input:
                cell_input = nodes.container(
                    nb_element="cell_code_source", classes=["cell_input"]
                )
                self.add_line_and_source_path(cell_input, token)
                with self.current_node_context(cell_input, append=True):
                    self._render_nb_cell_code_source(token)

            # render the execution output, if any
            if outputs and (not remove_output):
                cell_output = nodes.container(
                    nb_element="cell_code_output", classes=["cell_output"]
                )
                self.add_line_and_source_path(cell_output, token)
                with self.current_node_context(cell_output, append=True):
                    self._render_nb_cell_code_outputs(token, outputs)

    def _get_nb_source_code_lexer(
        self: SelfType,
        cell_index: int,
        warn_missing: bool = True,
        line: int | None = None,
    ) -> str | None:
        """Get the lexer name for code cell source."""
        lexer = self.nb_client.nb_source_code_lexer()
        if lexer is None and warn_missing:
            # TODO this will create a warning for every cell, but perhaps
            # it should only be a single warning for the notebook (as previously)
            # TODO allow user to set default lexer?
            create_warning(
                self.document,
                f"No source code lexer found for notebook cell {cell_index + 1}",
                # wtype=DEFAULT_LOG_TYPE,
                subtype=MystNBWarnings.LEXER,
                line=line,
                append_to=self.current_node,
            )
        return lexer

    def _render_nb_cell_code_source(self: SelfType, token: SyntaxTreeNode) -> None:
        """Render a notebook code cell's source."""
        cell_index = token.meta["index"]
        line = token_line(token, 0) or None
        node = self.create_highlighted_code_block(
            token.content,
            self._get_nb_source_code_lexer(cell_index, line=line),
            number_lines=self.get_cell_level_config(
                "number_source_lines",
                token.meta["metadata"],
                line=line,
            ),
            source=self.document["source"],
            line=token_line(token),
        )
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def _get_nb_code_cell_outputs(
        self, token: SyntaxTreeNode
    ) -> tuple[int | None, list[NotebookNode]]:
        """Get the outputs for a code cell and its execution count."""
        cell_index = token.meta["index"]
        line = token_line(token, 0) or None

        exec_count, outputs = self.nb_client.code_cell_outputs(cell_index)

        if self.get_cell_level_config("merge_streams", token.meta["metadata"], line):
            # TODO should this be saved on the output notebook
            outputs = coalesce_streams(outputs)

        return exec_count, outputs

    def _render_nb_cell_code_outputs(
        self, token: SyntaxTreeNode, outputs: list[NotebookNode]
    ) -> None:
        """Render a notebook code cell's outputs."""
        # for display_data/execute_result this is different in the
        # docutils/sphinx implementation,
        # since sphinx delays MIME type selection until a post-transform
        # (when the output format is known)

        # TODO how to output MyST Markdown?
        # currently text/markdown is set to be rendered as CommonMark only,
        # with headings disallowed,
        # to avoid "side effects" if the mime is discarded but contained
        # targets, etc, and because we can't parse headings within containers.
        # perhaps we could have a config option to allow this?
        # - for non-commonmark, the text/markdown would always be considered
        #   the top priority, and all other mime types would be ignored.
        # - for headings, we would also need to parsing the markdown
        #   at the "top-level", i.e. not nested in container(s)

        raise NotImplementedError


@dc.dataclass()
class MimeData:
    """Mime data from an execution output (display_data / execute_result)

    e.g. notebook.cells[0].outputs[0].data['text/plain'] = "Hello, world!"

    see: https://nbformat.readthedocs.io/en/5.1.3/format_description.html#display-data
    """

    mime_type: str
    """Mime type key of the output.data"""
    content: str | bytes
    """Data value of the output.data"""
    cell_metadata: dict[str, Any] = dc.field(default_factory=dict)
    """Cell level metadata of the output"""
    output_metadata: dict[str, Any] = dc.field(default_factory=dict)
    """Output level metadata of the output"""
    cell_index: int | None = None
    """Index of the cell in the notebook"""
    output_index: int | None = None
    """Index of the output in the cell"""
    line: int | None = None
    """Source line of the cell"""

    @property
    def string(self) -> str:
        """Get the content as a string."""
        try:
            return self.content.decode("utf-8")  # type: ignore
        except AttributeError:
            return self.content  # type: ignore


class NbElementRenderer:
    """A class for rendering notebook elements."""

    def __init__(
        self, renderer: DocutilsNbRenderer | SphinxNbRenderer, logger: LoggerType
    ) -> None:
        """Initialize the renderer.

        :params output_folder: the folder path for external outputs (like images)
        """
        self._renderer = renderer
        self._logger = logger

    @property
    def renderer(self) -> DocutilsNbRenderer | SphinxNbRenderer:
        """The renderer this output renderer is associated with."""
        return self._renderer

    @property
    def config(self) -> NbParserConfig:
        """The notebook parser config"""
        return self._renderer.nb_config

    @property
    def logger(self) -> LoggerType:
        """The logger for this renderer.

        In extension to a standard logger,
        this logger also for `line` and `subtype` kwargs to the `log` methods.
        """
        # TODO the only problem with logging here, is that we cannot generate
        # nodes.system_message to append to the document.
        return self._logger

    @property
    def source(self):
        """The source of the notebook."""
        return self.renderer.document["source"]

    def write_file(
        self, path: list[str], content: bytes, overwrite=False, exists_ok=False
    ) -> str:
        """Write a file to the external output folder.

        :param path: the path to write the file to, relative to the output folder
        :param content: the content to write to the file
        :param overwrite: whether to overwrite an existing file
        :param exists_ok: whether to ignore an existing file if overwrite is False

        :returns: URI to use for referencing the file
        """
        output_folder = self.config.output_folder
        filepath = Path(output_folder).joinpath(*path)
        if not output_folder:
            pass  # do not output anything if output_folder is not set (docutils only)
        elif filepath.exists():
            if overwrite:
                filepath.write_bytes(content)
            elif not exists_ok:
                # TODO raise or just report?
                raise FileExistsError(f"File already exists: {filepath}")
        else:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_bytes(content)

        if self.renderer.sphinx_env:
            # sphinx expects paths in POSIX format, relative to the documents path,
            # or relative to the source folder if prepended with '/'
            filepath = filepath.resolve()
            if os.name == "nt":
                # Can't get relative path between drives on Windows
                return filepath.as_posix()
            # Path().relative_to() doesn't work when not a direct subpath
            return "/" + os.path.relpath(filepath, self.renderer.sphinx_env.app.srcdir)
        else:
            return str(filepath)

    def add_js_file(self, key: str, uri: str | None, kwargs: dict[str, str]) -> None:
        """Register a JavaScript file to include in the HTML output of this document.

        :param key: the key to use for referencing the file
        :param uri: the URI to the file, or None and supply the file contents in kwargs['body']
        """
        if "nb_js_files" not in self.renderer.document:
            self.renderer.document["nb_js_files"] = {}
        # TODO handle duplicate keys (whether to override/ignore)
        self.renderer.document["nb_js_files"][key] = (uri, kwargs)

    def render_nb_finalise(self, metadata: dict) -> None:
        """Finalise the render of the notebook metadata."""
        # add ipywidgets state JavaScript,
        # The JSON inside the script tag is identified and parsed by:
        # https://github.com/jupyter-widgets/ipywidgets/blob/32f59acbc63c3ff0acf6afa86399cb563d3a9a86/packages/html-manager/src/libembed.ts#L36
        # see also: https://ipywidgets.readthedocs.io/en/7.6.5/embedding.html
        ipywidgets = metadata.get("widgets", None)
        ipywidgets_mime = (ipywidgets or {}).get(WIDGET_STATE_MIMETYPE, {})
        if ipywidgets_mime.get("state", None):
            self.add_js_file(
                "ipywidgets_state",
                None,
                {
                    "type": "application/vnd.jupyter.widget-state+json",
                    "body": sanitize_script_content(json.dumps(ipywidgets_mime)),
                },
            )
            for i, (path, kwargs) in enumerate(self.config.ipywidgets_js.items()):
                self.add_js_file(f"ipywidgets_{i}", path, kwargs)

    def render_raw_cell(
        self, content: str, metadata: dict, cell_index: int, source_line: int
    ) -> list[nodes.Element]:
        """Render a raw cell.

        https://nbformat.readthedocs.io/en/5.1.3/format_description.html#raw-nbconvert-cells

        :param content: the raw cell content
        :param metadata: the cell level metadata
        :param cell_index: the index of the cell
        :param source_line: the line number of the cell in the source document
        """
        mime_type = metadata.get("format")
        if not mime_type:
            # skip without warning, since e.g. jupytext saves raw cells with no format
            return []
        return self.render_mime_type(
            MimeData(
                mime_type, content, metadata, cell_index=cell_index, line=source_line
            )
        )

    def render_stdout(
        self,
        output: NotebookNode,
        cell_metadata: dict[str, Any],
        cell_index: int,
        source_line: int,
    ) -> list[nodes.Element]:
        """Render a notebook stdout output.

        https://nbformat.readthedocs.io/en/5.1.3/format_description.html#stream-output

        :param output: the output node
        :param metadata: the cell level metadata
        :param cell_index: the index of the cell containing the output
        :param source_line: the line number of the cell in the source document
        """
        if "remove-stdout" in cell_metadata.get("tags", []):
            return []
        lexer = self.renderer.get_cell_level_config(
            "render_text_lexer", cell_metadata, line=source_line
        )
        node = self.renderer.create_highlighted_code_block(
            output["text"], lexer, source=self.source, line=source_line
        )
        node["classes"] += ["output", "stream"]
        return [node]

    def render_stderr(
        self,
        output: NotebookNode,
        cell_metadata: dict[str, Any],
        cell_index: int,
        source_line: int,
    ) -> list[nodes.Element]:
        """Render a notebook stderr output.

        https://nbformat.readthedocs.io/en/5.1.3/format_description.html#stream-output

        :param output: the output node
        :param metadata: the cell level metadata
        :param cell_index: the index of the cell containing the output
        :param source_line: the line number of the cell in the source document
        """
        if "remove-stderr" in cell_metadata.get("tags", []):
            return []
        output_stderr = self.renderer.get_cell_level_config(
            "output_stderr", cell_metadata, line=source_line
        )
        msg = f"stderr was found in the cell outputs of cell {cell_index + 1}"
        outputs = []
        if output_stderr == "remove":
            return []
        elif output_stderr == "remove-warn":
            self.logger.warning(msg, subtype="stderr", line=source_line)
            return []
        elif output_stderr == "warn":
            self.logger.warning(msg, subtype="stderr", line=source_line)
        elif output_stderr == "error":
            self.logger.error(msg, subtype="stderr", line=source_line)
        elif output_stderr == "severe":
            self.logger.critical(msg, subtype="stderr", line=source_line)
        lexer = self.renderer.get_cell_level_config(
            "render_text_lexer", cell_metadata, line=source_line
        )
        node = self.renderer.create_highlighted_code_block(
            output["text"], lexer, source=self.source, line=source_line
        )
        node["classes"] += ["output", "stderr"]
        outputs.append(node)
        return outputs

    def render_error(
        self,
        output: NotebookNode,
        cell_metadata: dict[str, Any],
        cell_index: int,
        source_line: int,
    ) -> list[nodes.Element]:
        """Render a notebook error output.

        https://nbformat.readthedocs.io/en/5.1.3/format_description.html#error

        :param output: the output node
        :param metadata: the cell level metadata
        :param cell_index: the index of the cell containing the output
        :param source_line: the line number of the cell in the source document
        """
        traceback = strip_ansi("\n".join(output["traceback"]))
        lexer = self.renderer.get_cell_level_config(
            "render_error_lexer", cell_metadata, line=source_line
        )
        node = self.renderer.create_highlighted_code_block(
            traceback, lexer, source=self.source, line=source_line
        )
        node["classes"] += ["output", "traceback"]
        return [node]

    def render_mime_type(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook mime output, as a block level element."""
        # try plugin renderers
        for renderer in load_mime_renders():
            nodes = renderer.handle_mime(self, data, False)
            if nodes is not None:
                return nodes

        # try default renderers
        if data.mime_type == "text/plain":
            return self.render_text_plain(data)
        if data.mime_type in {
            "image/png",
            "image/jpeg",
            "application/pdf",
            "image/svg+xml",
            "image/gif",
        }:
            return self.render_image(data)
        if data.mime_type == "text/html":
            return self.render_text_html(data)
        if data.mime_type == "text/latex":
            return self.render_text_latex(data)
        if data.mime_type == "application/javascript":
            return self.render_javascript(data)
        if data.mime_type == WIDGET_VIEW_MIMETYPE:
            return self.render_widget_view(data)
        if data.mime_type == "text/markdown":
            return self.render_markdown(data)

        return self.render_unhandled(data)

    def render_unhandled(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook output of unknown mime type."""
        self.logger.warning(
            f"skipping unknown output mime type: {data.mime_type}",
            subtype="unknown_mime_type",
            line=data.line,
        )
        return []

    def render_markdown(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook text/markdown mime data output."""
        fmt = self.renderer.get_cell_level_config(
            "render_markdown_format", data.cell_metadata, line=data.line
        )
        return self._render_markdown_base(data, fmt=fmt, inline=False)

    def render_text_plain(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook text/plain mime data output."""
        lexer = self.renderer.get_cell_level_config(
            "render_text_lexer", data.cell_metadata, line=data.line
        )
        node = self.renderer.create_highlighted_code_block(
            data.string, lexer, source=self.source, line=data.line
        )
        node["classes"] += ["output", "text_plain"]
        return [node]

    def render_text_html(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook text/html mime data output."""
        return [
            nodes.raw(text=data.string, format="html", classes=["output", "text_html"])
        ]

    def render_text_latex(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook text/latex mime data output."""
        # TODO should we always assume this is math?
        return [
            nodes.math_block(
                text=strip_latex_delimiters(data.string),
                nowrap=False,
                number=None,
                classes=["output", "text_latex"],
            )
        ]

    def render_image(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook image mime data output."""
        # Adapted from:
        # https://github.com/jupyter/nbconvert/blob/45df4b6089b3bbab4b9c504f9e6a892f5b8692e3/nbconvert/preprocessors/extractoutput.py#L43

        # ensure that the data is a bytestring
        if data.mime_type in {
            "image/png",
            "image/jpeg",
            "image/gif",
            "application/pdf",
        }:
            # data is b64-encoded as text
            data_bytes = a2b_base64(data.content)
        elif isinstance(data.content, str):
            # ensure correct line separator
            data_bytes = os.linesep.join(data.content.splitlines()).encode("utf-8")
        # create filename
        extension = (
            guess_extension(data.mime_type) or "." + data.mime_type.rsplit("/")[-1]
        )
        # latex does not recognize the '.jpe' extension
        extension = ".jpeg" if extension == ".jpe" else extension
        # ensure de-duplication of outputs by using hash as filename
        # TODO note this is a change to the current implementation,
        # which names by {notbook_name}-{cell_index}-{output-index}.{extension}
        data_hash = hashlib.sha256(data_bytes).hexdigest()
        filename = f"{data_hash}{extension}"
        # TODO should we be trying to clear old files?
        uri = self.write_file([filename], data_bytes, overwrite=False, exists_ok=True)
        image_node = nodes.image(uri=uri)
        # apply attributes to the image node
        # TODO backwards-compatible re-naming to image_options?
        image_options = self.renderer.get_cell_level_config(
            "render_image_options", data.cell_metadata, line=data.line
        ).copy()
        # Overwrite with metadata stored in output
        image_options.update(
            {
                key: str(value)
                for key, value in data.output_metadata.get(data.mime_type, {}).items()
                if key in {"width", "height"}
            }
        )
        for key, spec in [
            ("classes", options_spec.class_option),
            ("alt", options_spec.unchanged),
            ("height", options_spec.length_or_unitless),
            ("width", options_spec.length_or_percentage_or_unitless),
            ("scale", options_spec.percentage),
            ("align", lambda a: options_spec.choice(a, ("left", "center", "right"))),
        ]:
            if key not in image_options:
                continue
            try:
                image_node[key] = spec(image_options[key])
            except Exception as exc:
                msg = f"Invalid image option ({key!r}; {image_options[key]!r}): {exc}"
                self.logger.warning(msg, subtype="image", line=data.line)
        return [image_node]

    def render_javascript(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook application/javascript mime data output."""
        content = sanitize_script_content(data.string)
        mime_type = "application/javascript"
        return [
            nodes.raw(
                text=f'<script type="{mime_type}">{content}</script>',
                format="html",
            )
        ]

    def render_widget_view(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook application/vnd.jupyter.widget-view+json mime output."""
        # TODO note ipywidgets present?
        content = sanitize_script_content(json.dumps(data.string))
        return [
            nodes.raw(
                text=f'<script type="{WIDGET_VIEW_MIMETYPE}">{content}</script>',
                format="html",
            )
        ]

    def render_mime_type_inline(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook mime output, as an inline level element."""

        # try plugin renderers
        for renderer in load_mime_renders():
            nodes = renderer.handle_mime(self, data, True)
            if nodes is not None:
                return nodes

        # try built-in renderers
        if data.mime_type == "text/plain":
            return self.render_text_plain_inline(data)
        if data.mime_type in {
            "image/png",
            "image/jpeg",
            "application/pdf",
            "image/svg+xml",
            "image/gif",
        }:
            return self.render_image_inline(data)
        if data.mime_type == "text/html":
            return self.render_text_html_inline(data)
        if data.mime_type == "text/latex":
            return self.render_text_latex_inline(data)
        if data.mime_type == "application/javascript":
            return self.render_javascript_inline(data)
        if data.mime_type == WIDGET_VIEW_MIMETYPE:
            return self.render_widget_view_inline(data)
        if data.mime_type == "text/markdown":
            return self.render_markdown_inline(data)

        return self.render_unhandled_inline(data)

    def render_unhandled_inline(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook output of unknown mime type."""
        self.logger.warning(
            f"skipping unknown output mime type: {data.mime_type}",
            subtype="unknown_mime_type",
            line=data.line,
        )
        return []

    def render_markdown_inline(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook text/markdown mime data output."""
        fmt = self.renderer.get_cell_level_config(
            "render_markdown_format", data.cell_metadata, line=data.line
        )
        return self._render_markdown_base(data, fmt=fmt, inline=True)

    def render_text_plain_inline(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook text/plain mime data output."""
        content = data.string
        if data.output_metadata.get("strip_text_quotes", False) and _QUOTED_RE.match(
            content
        ):
            content = content[1:-1]
        node = nodes.inline(data.string, content, classes=["output", "text_plain"])
        return [node]

    def render_text_html_inline(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook text/html mime data output."""
        return self.render_text_html(data)

    def render_text_latex_inline(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook text/latex mime data output."""
        # TODO should we always assume this is math?
        return [
            nodes.math(
                text=strip_latex_delimiters(data.string),
                nowrap=False,
                number=None,
                classes=["output", "text_latex"],
            )
        ]

    def render_image_inline(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook image mime data output."""
        return self.render_image(data)

    def render_javascript_inline(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook application/javascript mime data output."""
        return self.render_javascript(data)

    def render_widget_view_inline(self, data: MimeData) -> list[nodes.Element]:
        """Render a notebook application/vnd.jupyter.widget-view+json mime output."""
        return self.render_widget_view(data)

    def _render_markdown_base(
        self, data: MimeData, *, fmt: str, inline: bool
    ) -> list[nodes.Element]:
        """Base render for a notebook markdown mime output (block or inline)."""
        pseudo_element = nodes.Element()  # element to hold the parsed markdown
        current_parser = self.renderer.md
        current_md_config = self.renderer.md_config
        try:
            # potentially replace the parser temporarily
            if fmt == "myst":
                # use the current configuration to render the markdown
                pass
            elif fmt == "commonmark":
                # use an isolated, CommonMark only, parser
                self.renderer.md_config = MdParserConfig(commonmark_only=True)
                self.renderer.md = create_md_parser(
                    self.renderer.md_config, self.renderer.__class__
                )
            elif fmt == "gfm":
                # use an isolated, GitHub Flavoured Markdown only, parser
                self.renderer.md_config = MdParserConfig(gfm_only=True)
                self.renderer.md = create_md_parser(
                    self.renderer.md_config, self.renderer.__class__
                )
            else:
                self.logger.warning(
                    f"skipping unknown markdown format: {fmt}",
                    subtype="unknown_markdown_format",
                    line=data.line,
                )
                return []

            with self.renderer.current_node_context(pseudo_element):
                self.renderer.nested_render_text(
                    data.string,
                    data.line or 0,
                    inline=inline,
                )
        finally:
            # restore the parser
            self.renderer.md = current_parser
            self.renderer.md_config = current_md_config

        return pseudo_element.children


class EntryPointError(Exception):
    """Exception raised when an entry point cannot be loaded."""


@lru_cache(maxsize=10)
def load_renderer(name: str) -> type[NbElementRenderer]:
    """Load a renderer,
    given a name within the ``RENDER_ENTRY_GROUP`` entry point group
    """
    all_eps = entry_points()
    if hasattr(all_eps, "select"):
        # importlib_metadata >= 3.6 or importlib.metadata in python >=3.10
        eps = all_eps.select(group=RENDER_ENTRY_GROUP, name=name)
        found = name in eps.names
    else:
        eps = {ep.name: ep for ep in all_eps.get(RENDER_ENTRY_GROUP, [])}  # type: ignore
        found = name in eps
    if found:
        klass = eps[name].load()
        if not issubclass(klass, NbElementRenderer):
            raise EntryPointError(
                f"Entry Point for {RENDER_ENTRY_GROUP}:{name} "
                f"is not a subclass of `NbElementRenderer`: {klass}"
            )
        return klass

    raise EntryPointError(f"No Entry Point found for {RENDER_ENTRY_GROUP}:{name}")


class MimeRenderPlugin(Protocol):
    """Protocol for a mime renderer plugin."""

    mime_priority_overrides: ClassVar[Sequence[tuple[str, str, int | None]]] = ()
    """A list of (builder name, mime type, priority)."""

    @staticmethod
    def handle_mime(
        renderer: NbElementRenderer, data: MimeData, inline: bool
    ) -> None | list[nodes.Element]:
        """A function that renders a mime type to docutils nodes, or returns None to reject."""


class ExampleMimeRenderPlugin(MimeRenderPlugin):
    """Example mime renderer for `custommimetype`."""

    mime_priority_overrides = [("*", "custommimetype", 1)]

    @staticmethod
    def handle_mime(
        renderer: NbElementRenderer, data: MimeData, inline: int
    ) -> None | list[nodes.Element]:
        if not inline and data.mime_type == "custommimetype":
            return [
                nodes.paragraph(
                    text=f"This is a custom mime type, with content: {data.content!r}",
                    classes=["output", "text_plain"],
                )
            ]
        return None


@lru_cache
def load_mime_renders() -> list[MimeRenderPlugin]:
    all_eps = entry_points()
    if hasattr(all_eps, "select"):
        # importlib_metadata >= 3.6 or importlib.metadata in python >=3.10
        return [ep.load() for ep in all_eps.select(group=MIME_RENDER_ENTRY_GROUP)]
    return [ep.load() for ep in all_eps.get(MIME_RENDER_ENTRY_GROUP, [])]  # type: ignore


def strip_ansi(text: str) -> str:
    """Strip ANSI escape sequences from a string"""
    return _ANSI_RE.sub("", text)


def sanitize_script_content(content: str) -> str:
    """Sanitize the content of a ``<script>`` tag."""
    # note escaping addresses https://github.com/jupyter/jupyter-sphinx/issues/184
    return content.replace("</script>", r"<\/script>")


def strip_latex_delimiters(source):
    r"""Remove LaTeX math delimiters that would be rendered by the math block.

    These are: ``\(…\)``, ``\[…\]``, ``$…$``, and ``$$…$$``.
    This is necessary because sphinx does not have a dedicated role for
    generic LaTeX, while Jupyter only defines generic LaTeX output, see
    https://github.com/jupyter/jupyter-sphinx/issues/90 for discussion.
    """
    source = source.strip()
    delimiter_pairs = (pair.split() for pair in r"\( \),\[ \],$$ $$,$ $".split(","))
    for start, end in delimiter_pairs:
        if source.startswith(start) and source.endswith(end):
            return source[len(start) : -len(end)]

    return source


@contextmanager
def create_figure_context(
    self: DocutilsNbRenderer | SphinxNbRenderer,
    figure_options: dict[str, Any] | None,
    line: int,
) -> Iterator:
    """Create a context manager, which optionally wraps new nodes in a figure node.

    A caption may also be added before or after the nodes.
    """
    if not isinstance(figure_options, dict):
        yield
        return

    # note: most of this is copied directly from sphinx.Figure

    # create figure node
    figure_node = nodes.figure()
    figure_node.line = line
    figure_node.source = self.document["source"]

    # add attributes to figure node
    if figure_options.get("classes"):  # TODO change to class?
        figure_node["classes"] += str(figure_options["classes"]).split()
    if figure_options.get("align") in ("center", "left", "right"):
        figure_node["align"] = figure_options["align"]

    # add target name
    if figure_options.get("name"):
        name = nodes.fully_normalize_name(str(figure_options.get("name")))
        figure_node["names"].append(name)
        self.document.note_explicit_target(figure_node, figure_node)

    # create caption node
    caption = None
    if figure_options.get("caption", ""):
        node = nodes.Element()  # anonymous container for parsing
        with self.current_node_context(node):
            self.nested_render_text(str(figure_options["caption"]), line)
        first_node = node.children[0]
        legend_nodes = node.children[1:]
        if isinstance(first_node, nodes.paragraph):
            caption = nodes.caption(first_node.rawsource, "", *first_node.children)
            caption.source = self.document["source"]
            caption.line = line
        elif not (isinstance(first_node, nodes.comment) and len(first_node) == 0):
            create_warning(
                self.document,
                "Figure caption must be a paragraph or empty comment.",
                line=line,
                # wtype=DEFAULT_LOG_TYPE,
                subtype=MystNBWarnings.FIG_CAPTION,
            )

    self.current_node.append(figure_node)
    old_current_node = self.current_node
    self.current_node = figure_node

    if caption and figure_options.get("caption_before", False):
        figure_node.append(caption)
        if legend_nodes:
            figure_node += nodes.legend("", *legend_nodes)

    yield

    if caption and not figure_options.get("caption_before", False):
        figure_node.append(caption)
        if legend_nodes:
            figure_node += nodes.legend("", *legend_nodes)

    self.current_node = old_current_node


def base_render_priority() -> dict[str, dict[str, int | None]]:
    """Create a base render priority dict: name -> mime type -> priority (ascending)."""
    # See formats at https://www.sphinx-doc.org/en/master/usage/builders/index.html
    # generated with:
    # [(b.name, b.format, b.supported_image_types) for b in app.registry.builders.values()]
    return {
        "epub": {
            "application/vnd.jupyter.widget-view+json": 10,
            "application/javascript": 20,
            "text/html": 30,
            "image/svg+xml": 40,
            "image/png": 50,
            "image/gif": 60,
            "image/jpeg": 70,
            "text/markdown": 80,
            "text/latex": 90,
            "text/plain": 100,
        },
        "html": {
            "application/vnd.jupyter.widget-view+json": 10,
            "application/javascript": 20,
            "text/html": 30,
            "image/svg+xml": 40,
            "image/png": 50,
            "image/gif": 60,
            "image/jpeg": 70,
            "text/markdown": 80,
            "text/latex": 90,
            "text/plain": 100,
        },
        "dirhtml": {
            "application/vnd.jupyter.widget-view+json": 10,
            "application/javascript": 20,
            "text/html": 30,
            "image/svg+xml": 40,
            "image/png": 50,
            "image/gif": 60,
            "image/jpeg": 70,
            "text/markdown": 80,
            "text/latex": 90,
            "text/plain": 100,
        },
        "singlehtml": {
            "application/vnd.jupyter.widget-view+json": 10,
            "application/javascript": 20,
            "text/html": 30,
            "image/svg+xml": 40,
            "image/png": 50,
            "image/gif": 60,
            "image/jpeg": 70,
            "text/markdown": 80,
            "text/latex": 90,
            "text/plain": 100,
        },
        "applehelp": {
            "application/vnd.jupyter.widget-view+json": 10,
            "application/javascript": 20,
            "text/html": 30,
            "image/png": 40,
            "image/gif": 50,
            "image/jpeg": 60,
            "image/tiff": 70,
            "image/jp2": 80,
            "image/svg+xml": 90,
            "text/markdown": 100,
            "text/latex": 110,
            "text/plain": 120,
        },
        "devhelp": {
            "application/vnd.jupyter.widget-view+json": 10,
            "application/javascript": 20,
            "text/html": 30,
            "image/png": 40,
            "image/gif": 50,
            "image/jpeg": 60,
            "text/markdown": 70,
            "text/latex": 80,
            "text/plain": 90,
        },
        "htmlhelp": {
            "application/vnd.jupyter.widget-view+json": 10,
            "application/javascript": 20,
            "text/html": 30,
            "image/png": 40,
            "image/gif": 50,
            "image/jpeg": 60,
            "text/markdown": 70,
            "text/latex": 80,
            "text/plain": 90,
        },
        "json": {
            "application/vnd.jupyter.widget-view+json": 10,
            "application/javascript": 20,
            "text/html": 30,
            "image/svg+xml": 40,
            "image/png": 50,
            "image/gif": 60,
            "image/jpeg": 70,
            "text/markdown": 80,
            "text/latex": 90,
            "text/plain": 100,
        },
        "pickle": {
            "application/vnd.jupyter.widget-view+json": 10,
            "application/javascript": 20,
            "text/html": 30,
            "image/svg+xml": 40,
            "image/png": 50,
            "image/gif": 60,
            "image/jpeg": 70,
            "text/markdown": 80,
            "text/latex": 90,
            "text/plain": 100,
        },
        "qthelp": {
            "application/vnd.jupyter.widget-view+json": 10,
            "application/javascript": 20,
            "text/html": 30,
            "image/svg+xml": 40,
            "image/png": 50,
            "image/gif": 60,
            "image/jpeg": 70,
            "text/markdown": 80,
            "text/latex": 90,
            "text/plain": 100,
        },
        # deprecated RTD builders
        # https://github.com/readthedocs/readthedocs-sphinx-ext/blob/master/readthedocs_ext/readthedocs.py
        "readthedocs": {
            "application/vnd.jupyter.widget-view+json": 10,
            "application/javascript": 20,
            "text/html": 30,
            "image/svg+xml": 40,
            "image/png": 50,
            "image/gif": 60,
            "image/jpeg": 70,
            "text/markdown": 80,
            "text/latex": 90,
            "text/plain": 100,
        },
        "readthedocsdirhtml": {
            "application/vnd.jupyter.widget-view+json": 10,
            "application/javascript": 20,
            "text/html": 30,
            "image/svg+xml": 40,
            "image/png": 50,
            "image/gif": 60,
            "image/jpeg": 70,
            "text/markdown": 80,
            "text/latex": 90,
            "text/plain": 100,
        },
        "readthedocssinglehtml": {
            "application/vnd.jupyter.widget-view+json": 10,
            "application/javascript": 20,
            "text/html": 30,
            "image/svg+xml": 40,
            "image/png": 50,
            "image/gif": 60,
            "image/jpeg": 70,
            "text/markdown": 80,
            "text/latex": 90,
            "text/plain": 100,
        },
        "readthedocssinglehtmllocalmedia": {
            "application/vnd.jupyter.widget-view+json": 10,
            "application/javascript": 20,
            "text/html": 30,
            "image/svg+xml": 40,
            "image/png": 50,
            "image/gif": 60,
            "image/jpeg": 70,
            "text/markdown": 80,
            "text/latex": 90,
            "text/plain": 100,
        },
        "changes": {"text/latex": 10, "text/markdown": 20, "text/plain": 30},
        "dummy": {"text/latex": 10, "text/markdown": 20, "text/plain": 30},
        "gettext": {"text/latex": 10, "text/markdown": 20, "text/plain": 30},
        "latex": {
            "application/pdf": 10,
            "image/png": 20,
            "image/jpeg": 30,
            "text/latex": 40,
            "text/markdown": 50,
            "text/plain": 60,
        },
        "linkcheck": {"text/latex": 10, "text/markdown": 20, "text/plain": 30},
        "man": {"text/latex": 10, "text/markdown": 20, "text/plain": 30},
        "texinfo": {
            "image/png": 10,
            "image/jpeg": 20,
            "image/gif": 30,
            "text/latex": 40,
            "text/markdown": 50,
            "text/plain": 60,
        },
        "text": {"text/latex": 10, "text/markdown": 20, "text/plain": 30},
        "xml": {"text/latex": 10, "text/markdown": 20, "text/plain": 30},
        "pseudoxml": {"text/latex": 10, "text/markdown": 20, "text/plain": 30},
    }


def get_mime_priority(
    builder: str, overrides: Sequence[tuple[str, str, int | None]]
) -> list[str]:
    """Return the priority list for the builder.

    Takes the base priority list, overrides from the config,
    then sorts by priority in ascending order.
    """
    base = base_render_priority().get(builder, {})
    overrides = list(overrides)
    for plugin in load_mime_renders():
        overrides = list(getattr(plugin, "mime_priority_overrides", [])) + overrides
    for override in overrides:
        if override[0] == "*" or override[0] == builder:
            base[override[1]] = override[2]
    sort = sorted(
        ((k, p) for k, p in base.items() if p is not None), key=lambda x: x[1]
    )
    return [k for k, _ in sort]
