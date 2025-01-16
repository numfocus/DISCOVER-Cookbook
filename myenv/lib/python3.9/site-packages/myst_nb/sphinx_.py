"""The sphinx parser implementation for myst-nb."""
from __future__ import annotations

from collections import defaultdict
from html import escape
import json
from pathlib import Path
import re
from typing import Any, DefaultDict, cast

from docutils import nodes
from markdown_it.token import Token
from markdown_it.tree import SyntaxTreeNode
from myst_parser.config.main import MdParserConfig, merge_file_level
from myst_parser.mdit_to_docutils.base import token_line
from myst_parser.mdit_to_docutils.sphinx_ import SphinxRenderer
from myst_parser.parsers.mdit import create_md_parser
from myst_parser.parsers.sphinx_ import MystParser
import nbformat
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.environment.collectors import EnvironmentCollector
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import logging as sphinx_logging
from sphinx.util.docutils import SphinxTranslator

from myst_nb._compat import findall
from myst_nb.core.config import NbParserConfig
from myst_nb.core.execute import ExecutionResult, create_client
from myst_nb.core.loggers import DEFAULT_LOG_TYPE, SphinxDocLogger
from myst_nb.core.nb_to_tokens import nb_node_to_dict, notebook_to_tokens
from myst_nb.core.read import create_nb_reader
from myst_nb.core.render import (
    MditRenderMixin,
    MimeData,
    NbElementRenderer,
    create_figure_context,
    get_mime_priority,
    load_renderer,
)
from myst_nb.warnings_ import MystNBWarnings, create_warning

SPHINX_LOGGER = sphinx_logging.getLogger(__name__)


class SphinxEnvType(BuildEnvironment):
    """Sphinx build environment, including attributes set by myst_nb."""

    myst_config: MdParserConfig
    mystnb_config: NbParserConfig
    nb_metadata: DefaultDict[str, dict]
    nb_new_exec_data: bool


class Parser(MystParser):
    """Sphinx parser for Jupyter Notebook formats, containing MyST Markdown."""

    supported = ("myst-nb",)
    translate_section_name = None

    config_section = "myst-nb parser"
    config_section_dependencies = ("parsers",)

    env: SphinxEnvType

    def parse(self, inputstring: str, document: nodes.document) -> None:
        """Parse source text.

        :param inputstring: The source string to parse
        :param document: The root docutils node to add AST elements to
        """
        assert self.env is not None, "env not set"
        document_path = self.env.doc2path(self.env.docname)

        # get a logger for this document
        logger = SphinxDocLogger(document)

        # get markdown parsing configuration
        md_config: MdParserConfig = self.env.myst_config

        # get notebook rendering configuration
        nb_config: NbParserConfig = self.env.mystnb_config

        # create a reader for the notebook
        nb_reader = create_nb_reader(document_path, md_config, nb_config, inputstring)
        # If the nb_reader is None, then we default to a standard Markdown parser
        if nb_reader is None:
            return super().parse(inputstring, document)
        notebook = nb_reader.read(inputstring)

        # update the global markdown config with the file-level config
        warning = lambda wtype, msg: create_warning(  # noqa: E731
            document, msg, line=1, append_to=document, subtype=wtype
        )
        nb_reader.md_config = merge_file_level(
            nb_reader.md_config, notebook.metadata, warning
        )

        # potentially replace kernel name with alias
        kernel_name = notebook.metadata.get("kernelspec", {}).get("name", None)
        if kernel_name is not None and nb_config.kernel_rgx_aliases:
            for rgx, alias in nb_config.kernel_rgx_aliases.items():
                if re.fullmatch(rgx, kernel_name):
                    logger.debug(
                        f"Replaced kernel name: {kernel_name!r} -> {alias!r}",
                        subtype="kernel",
                    )
                    notebook.metadata["kernelspec"]["name"] = alias
                    break

        # Update mystnb configuration with notebook level metadata
        if nb_config.metadata_key in notebook.metadata:
            overrides = nb_node_to_dict(notebook.metadata[nb_config.metadata_key])
            overrides.pop("output_folder", None)  # this should not be overridden
            try:
                nb_config = nb_config.copy(**overrides)
            except Exception as exc:
                logger.warning(
                    f"Failed to update configuration with notebook metadata: {exc}",
                    subtype="config",
                )
            else:
                logger.debug(
                    "Updated configuration with notebook metadata", subtype="config"
                )

        # Setup the parser
        mdit_parser = create_md_parser(nb_reader.md_config, SphinxNbRenderer)
        mdit_parser.options["document"] = document
        mdit_parser.options["nb_config"] = nb_config
        mdit_renderer: SphinxNbRenderer = mdit_parser.renderer  # type: ignore
        mdit_env: dict[str, Any] = {}

        # load notebook element renderer class from entry-point name
        # this is separate from SphinxNbRenderer, so that users can override it
        renderer_name = nb_config.render_plugin
        nb_renderer: NbElementRenderer = load_renderer(renderer_name)(
            mdit_renderer, logger
        )
        # we temporarily store nb_renderer on the document,
        # so that roles/directives can access it
        document.attributes["nb_renderer"] = nb_renderer
        # we currently do this early, so that the nb_renderer has access to things
        mdit_renderer.setup_render(mdit_parser.options, mdit_env)  # type: ignore

        # parse notebook structure to markdown-it tokens
        # note, this does not assume that the notebook has been executed yet
        mdit_tokens = notebook_to_tokens(notebook, mdit_parser, mdit_env, logger)

        # open the notebook execution client,
        # this may execute the notebook immediately or during the page render
        with create_client(
            notebook, document_path, nb_config, logger, nb_reader.read_fmt
        ) as nb_client:
            mdit_parser.options["nb_client"] = nb_client
            # convert to docutils AST, which is added to the document
            mdit_renderer.render(mdit_tokens, mdit_parser.options, mdit_env)

        # save final execution data
        if nb_client.exec_metadata:
            NbMetadataCollector.set_exec_data(
                self.env, self.env.docname, nb_client.exec_metadata
            )
            if nb_client.exec_metadata["traceback"]:
                # store error traceback in outdir and log its path
                reports_file = Path(self.env.app.outdir).joinpath(
                    "reports", *(self.env.docname + ".err.log").split("/")
                )
                reports_file.parent.mkdir(parents=True, exist_ok=True)
                reports_file.write_text(
                    nb_client.exec_metadata["traceback"], encoding="utf8"
                )
                logger.warning(
                    f"Notebook exception traceback saved in: {reports_file}",
                    subtype="exec",
                )

        # write final (updated) notebook to output folder (utf8 is standard encoding)
        path = self.env.docname.split("/")
        ipynb_path = path[:-1] + [path[-1] + ".ipynb"]
        content = nbformat.writes(notebook).encode("utf-8")
        nb_renderer.write_file(ipynb_path, content, overwrite=True)

        # write glue data to the output folder,
        # and store the keys to environment doc metadata,
        # so that they may be used in any post-transform steps
        if nb_client.glue_data:
            glue_path = path[:-1] + [path[-1] + ".glue.json"]
            nb_renderer.write_file(
                glue_path,
                json.dumps(nb_client.glue_data, cls=BytesEncoder).encode("utf8"),
                overwrite=True,
            )
            NbMetadataCollector.set_doc_data(
                self.env, self.env.docname, "glue", list(nb_client.glue_data.keys())
            )

        # move some document metadata to environment metadata,
        # so that we can later read it from the environment,
        # rather than having to load the whole doctree
        for key, (uri, kwargs) in document.attributes.pop("nb_js_files", {}).items():
            NbMetadataCollector.add_js_file(
                self.env, self.env.docname, key, uri, kwargs
            )

        # remove temporary state
        document.attributes.pop("nb_renderer")


class SphinxNbRenderer(SphinxRenderer, MditRenderMixin):
    """A sphinx renderer for Jupyter Notebooks."""

    def render_nb_initialise(self, token: SyntaxTreeNode) -> None:
        env = cast(BuildEnvironment, self.sphinx_env)
        metadata = self.nb_client.nb_metadata
        special_keys = ["kernelspec", "language_info", "source_map"]
        for key in special_keys:
            if key in metadata:
                # save these special keys on the metadata, rather than as docinfo
                # note, sphinx_book_theme checks kernelspec is in the metadata
                env.metadata[env.docname][key] = metadata.get(key)

        # forward the remaining metadata to the front_matter renderer
        special_keys.append("widgets")
        top_matter = {k: v for k, v in metadata.items() if k not in special_keys}
        self.render_front_matter(
            Token(  # type: ignore
                "front_matter",
                "",
                0,
                map=[0, 0],
                content=top_matter,  # type: ignore[arg-type]
            ),
        )

    def _render_nb_cell_code_outputs(
        self, token: SyntaxTreeNode, outputs: list[nbformat.NotebookNode]
    ) -> None:
        """Render a notebook code cell's outputs."""
        line = token_line(token, 0)
        cell_index = token.meta["index"]
        metadata = token.meta["metadata"]
        # render the outputs
        for output_index, output in enumerate(outputs):
            if output.output_type == "stream":
                if output.name == "stdout":
                    _nodes = self.nb_renderer.render_stdout(
                        output, metadata, cell_index, line
                    )
                    self.add_line_and_source_path_r(_nodes, token)
                    self.current_node.extend(_nodes)
                elif output.name == "stderr":
                    _nodes = self.nb_renderer.render_stderr(
                        output, metadata, cell_index, line
                    )
                    self.add_line_and_source_path_r(_nodes, token)
                    self.current_node.extend(_nodes)
                else:
                    pass  # TODO warning
            elif output.output_type == "error":
                _nodes = self.nb_renderer.render_error(
                    output, metadata, cell_index, line
                )
                self.add_line_and_source_path_r(_nodes, token)
                self.current_node.extend(_nodes)
            elif output.output_type in ("display_data", "execute_result"):
                # Note, this is different to the docutils implementation,
                # where we directly select a single output, based on the mime_priority.
                # Here, we do not know the mime priority until we know the output format
                # so we output all the outputs during this parsing phase
                # (this is what sphinx caches as "output format agnostic" AST),
                # and replace the mime_bundle with the format specific output
                # in a post-transform (run per output format on the cached AST)

                figure_options = (
                    self.get_cell_level_config(
                        "render_figure_options", metadata, line=line
                    )
                    or None
                )

                with create_figure_context(self, figure_options, line):
                    mime_bundle = nodes.container(nb_element="mime_bundle")
                    with self.current_node_context(mime_bundle):
                        for mime_type, data in output["data"].items():
                            mime_container = nodes.container(mime_type=mime_type)
                            with self.current_node_context(mime_container):
                                _nodes = self.nb_renderer.render_mime_type(
                                    MimeData(
                                        mime_type,
                                        data,
                                        cell_metadata=metadata,
                                        output_metadata=output.get("metadata", {}),
                                        cell_index=cell_index,
                                        output_index=output_index,
                                        line=line,
                                    )
                                )
                                self.current_node.extend(_nodes)
                            if mime_container.children:
                                self.current_node.append(mime_container)
                    if mime_bundle.children:
                        self.add_line_and_source_path_r([mime_bundle], token)
                        self.current_node.append(mime_bundle)
            else:
                create_warning(
                    self.document,
                    f"Unsupported output type: {output.output_type}",
                    line=line,
                    append_to=self.current_node,
                    # wtype=DEFAULT_LOG_TYPE,
                    subtype=MystNBWarnings.OUTPUT_TYPE,
                )


class SelectMimeType(SphinxPostTransform):
    """Select the mime type to render from mime bundles,
    based on the builder and its associated priority list.
    """

    default_priority = 4  # TODO set correct priority

    def run(self, **kwargs: Any) -> None:
        """Run the transform."""
        # get priority list for this builder
        # TODO allow for per-notebook/cell priority dicts?
        bname = self.app.builder.name
        priority_list = get_mime_priority(
            bname, self.config["nb_mime_priority_overrides"]
        )

        def condition(node):
            return (
                isinstance(node, nodes.container)
                and node.attributes.get("nb_element", "") == "mime_bundle"
            )

        # remove/replace_self will not work with an iterator
        for node in list(findall(self.document)(condition)):
            # get available mime types
            mime_types = [node["mime_type"] for node in node.children]
            if not mime_types:
                node.parent.remove(node)
                continue
            # select top priority
            index = None
            for mime_type in priority_list:
                try:
                    index = mime_types.index(mime_type)
                except ValueError:
                    continue
                else:
                    break
            if index is None:
                mime_string = ",".join(repr(m) for m in mime_types)
                SPHINX_LOGGER.warning(
                    f"No mime type available in priority list for builder {bname!r} "
                    f"({mime_string}) [{DEFAULT_LOG_TYPE}.mime_priority]",
                    type=DEFAULT_LOG_TYPE,
                    subtype="mime_priority",
                    location=node,
                )
                node.parent.remove(node)
            elif not node.children[index].children:
                node.parent.remove(node)
            else:
                node.replace_self(node.children[index].children)


class NbMetadataCollector(EnvironmentCollector):
    """Collect myst-nb specific metadata, and handle merging of parallel builds."""

    @staticmethod
    def set_doc_data(env: SphinxEnvType, docname: str, key: str, value: Any) -> None:
        """Add nb metadata for a docname to the environment."""
        if not hasattr(env, "nb_metadata"):
            env.nb_metadata = defaultdict(dict)
        env.nb_metadata.setdefault(docname, {})[key] = value

    @staticmethod
    def get_doc_data(env: SphinxEnvType) -> DefaultDict[str, dict]:
        """Get myst-nb docname -> metadata dict."""
        if not hasattr(env, "nb_metadata"):
            env.nb_metadata = defaultdict(dict)
        return env.nb_metadata

    @classmethod
    def set_exec_data(
        cls, env: SphinxEnvType, docname: str, value: ExecutionResult
    ) -> None:
        """Add nb metadata for a docname to the environment."""
        cls.set_doc_data(env, docname, "exec_data", value)
        # TODO this does not take account of cache data
        cls.note_exec_update(env)

    @classmethod
    def get_exec_data(cls, env: SphinxEnvType, docname: str) -> ExecutionResult | None:
        """Get myst-nb docname -> execution data."""
        return cls.get_doc_data(env)[docname].get("exec_data")

    def get_outdated_docs(  # type: ignore[override]
        self,
        app: Sphinx,
        env: SphinxEnvType,
        added: set[str],
        changed: set[str],
        removed: set[str],
    ) -> list[str]:
        # called before any docs are read
        env.nb_new_exec_data = False
        return []

    @staticmethod
    def note_exec_update(env: SphinxEnvType) -> None:
        """Note that a notebook has been executed."""
        env.nb_new_exec_data = True

    @staticmethod
    def new_exec_data(env: SphinxEnvType) -> bool:
        """Return whether any notebooks have updated execution data."""
        return getattr(env, "nb_new_exec_data", False)

    @classmethod
    def add_js_file(
        cls,
        env: SphinxEnvType,
        docname: str,
        key: str,
        uri: str | None,
        kwargs: dict[str, str],
    ):
        """Register a JavaScript file to include in the HTML output."""
        if not hasattr(env, "nb_metadata"):
            env.nb_metadata = defaultdict(dict)
        js_files = env.nb_metadata.setdefault(docname, {}).setdefault("js_files", {})
        # TODO handle whether overrides are allowed
        js_files[key] = (uri, kwargs)

    @classmethod
    def get_js_files(
        cls, env: SphinxEnvType, docname: str
    ) -> dict[str, tuple[str | None, dict[str, str]]]:
        """Get myst-nb docname -> execution data."""
        return cls.get_doc_data(env)[docname].get("js_files", {})

    def clear_doc(  # type: ignore[override]
        self,
        app: Sphinx,
        env: SphinxEnvType,
        docname: str,
    ) -> None:
        if not hasattr(env, "nb_metadata"):
            env.nb_metadata = defaultdict(dict)
        env.nb_metadata.pop(docname, None)

    def process_doc(self, app: Sphinx, doctree: nodes.document) -> None:
        pass

    def merge_other(  # type: ignore[override]
        self,
        app: Sphinx,
        env: SphinxEnvType,
        docnames: set[str],
        other: SphinxEnvType,
    ) -> None:
        if not hasattr(env, "nb_metadata"):
            env.nb_metadata = defaultdict(dict)
        other_metadata = getattr(other, "nb_metadata", defaultdict(dict))
        for docname in docnames:
            env.nb_metadata[docname] = other_metadata[docname]
        if other.nb_new_exec_data:
            env.nb_new_exec_data = True


class BytesEncoder(json.JSONEncoder):
    """A JSON encoder that accepts b64 (and other *ascii*) bytestrings."""

    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode("ascii")
        return json.JSONEncoder.default(self, obj)


class HideCodeCellNode(nodes.Element):
    """Node for hiding cell input."""

    @classmethod
    def add_to_app(cls, app: Sphinx):
        app.add_node(cls, html=(visit_HideCellInput, depart_HideCellInput))


def visit_HideCellInput(self: SphinxTranslator, node: HideCodeCellNode):
    classes = " ".join(node["classes"])
    self.body.append(f'<details class="hide {classes}">\n')
    self.body.append('<summary aria-label="Toggle hidden content">\n')
    self.body.append(f'<span class="collapsed">{escape(node["prompt_show"])}</span>\n')
    self.body.append(f'<span class="expanded">{escape(node["prompt_hide"])}</span>\n')
    self.body.append("</summary>\n")


def depart_HideCellInput(self: SphinxTranslator, node: HideCodeCellNode):
    self.body.append("</details>\n")


class HideInputCells(SphinxPostTransform):
    """Hide input cells in the HTML output."""

    default_priority = 199
    formats = ("html",)

    def run(self, **kwargs):
        for node in findall(self.document)(nodes.container):
            if (
                node.get("nb_element") == "cell_code"
                and node.get("hide_mode")
                and node.children
            ):
                hide_mode = node.get("hide_mode")
                has_input = node.children[0].get("nb_element") == "cell_code_source"
                has_output = node.children[-1].get("nb_element") == "cell_code_output"

                if has_input and hide_mode == "all":
                    # wrap everything and place a summary above the input
                    wrap_node = HideCodeCellNode(
                        prompt_show=node["prompt_show"].replace("{type}", "content"),
                        prompt_hide=node["prompt_hide"].replace("{type}", "content"),
                    )
                    wrap_node["classes"].append("above-input")
                    wrap_node.extend(node.children)
                    node.children = [wrap_node]

                if has_input and has_output and hide_mode in ("output", "input+output"):
                    node.children[0]["classes"].append("above-output-prompt")

                if has_input and hide_mode in ("input", "input+output"):
                    # wrap just the input and place a summary above the input
                    wrap_node = HideCodeCellNode(
                        prompt_show=node["prompt_show"].replace("{type}", "source"),
                        prompt_hide=node["prompt_hide"].replace("{type}", "source"),
                    )
                    wrap_node["classes"].append("above-input")
                    code = node.children[0]
                    wrap_node.append(code)
                    node.replace(code, wrap_node)

                if has_input and has_output and hide_mode in ("output", "input+output"):
                    # wrap just the output and place a summary below the input
                    wrap_node = HideCodeCellNode(
                        prompt_show=node["prompt_show"].replace("{type}", "output"),
                        prompt_hide=node["prompt_hide"].replace("{type}", "output"),
                    )
                    wrap_node["classes"].append("below-input")
                    output = node.children[-1]
                    wrap_node.append(output)
                    node.replace(output, wrap_node)

                if (
                    (not has_input)
                    and has_output
                    and hide_mode in ("all", "input+output", "output")
                ):
                    # wrap just the output and place a summary above the output
                    wrap_node = HideCodeCellNode(
                        prompt_show=node["prompt_show"].replace("{type}", "outputs"),
                        prompt_hide=node["prompt_hide"].replace("{type}", "outputs"),
                    )
                    wrap_node["classes"].append("above-output")
                    output = node.children[-1]
                    wrap_node.append(output)
                    node.replace(output, wrap_node)
