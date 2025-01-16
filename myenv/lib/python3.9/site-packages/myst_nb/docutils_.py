"""The docutils parser implementation for myst-nb."""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache, partial
from importlib import resources as import_resources
import os
from typing import Any

from docutils import nodes
from docutils.core import default_description, publish_cmdline
from docutils.parsers.rst.directives import _directives
from docutils.parsers.rst.roles import _roles
from markdown_it.token import Token
from markdown_it.tree import SyntaxTreeNode
from myst_parser.config.main import MdParserConfig, merge_file_level
from myst_parser.mdit_to_docutils.base import DocutilsRenderer, token_line
from myst_parser.parsers.docutils_ import Parser as MystParser
from myst_parser.parsers.docutils_ import create_myst_config, create_myst_settings_spec
from myst_parser.parsers.mdit import create_md_parser
import nbformat
from nbformat import NotebookNode
from pygments.formatters import get_formatter_by_name

from myst_nb import static
from myst_nb.core.config import NbParserConfig
from myst_nb.core.execute import create_client
from myst_nb.core.loggers import DocutilsDocLogger  # DEFAULT_LOG_TYPE,
from myst_nb.core.nb_to_tokens import nb_node_to_dict, notebook_to_tokens
from myst_nb.core.read import (
    NbReader,
    UnexpectedCellDirective,
    read_myst_markdown_notebook,
    standard_nb_read,
)
from myst_nb.core.render import (
    MditRenderMixin,
    MimeData,
    NbElementRenderer,
    create_figure_context,
    get_mime_priority,
    load_renderer,
)
from myst_nb.ext.eval import load_eval_docutils
from myst_nb.ext.glue import load_glue_docutils
from myst_nb.warnings_ import MystNBWarnings, create_warning

DOCUTILS_EXCLUDED_ARGS = list(
    {f.name for f in NbParserConfig.get_fields() if f.metadata.get("docutils_exclude")}
)


@dataclass
class DocutilsApp:
    roles: dict[str, Any] = field(default_factory=dict)
    directives: dict[str, Any] = field(default_factory=dict)


@lru_cache(maxsize=1)
def get_nb_roles_directives() -> DocutilsApp:
    app = DocutilsApp()
    app.directives["code-cell"] = UnexpectedCellDirective
    app.directives["raw-cell"] = UnexpectedCellDirective
    load_eval_docutils(app)
    load_glue_docutils(app)
    return app


class Parser(MystParser):
    """Docutils parser for Jupyter Notebooks, containing MyST Markdown."""

    supported: tuple[str, ...] = ("mystnb", "ipynb")
    """Aliases this parser supports."""

    settings_spec = (
        "MyST-NB options",
        None,
        create_myst_settings_spec(NbParserConfig, "nb_"),
        *MystParser.settings_spec,
    )
    """Runtime settings specification."""

    config_section = "myst-nb parser"

    def parse(self, inputstring: str, document: nodes.document) -> None:
        # register/unregister special directives and roles
        app = get_nb_roles_directives()
        for name, directive in app.directives.items():
            _directives[name] = directive
        for name, role in app.roles.items():
            _roles[name] = role
        try:
            return self._parse(inputstring, document)
        finally:
            for name in app.directives:
                _directives.pop(name, None)
            for name in app.roles:
                _roles.pop(name, None)

    def _parse(self, inputstring: str, document: nodes.document) -> None:
        """Parse source text.

        :param inputstring: The source string to parse
        :param document: The root docutils node to add AST elements to
        """
        document_source = document["source"]

        # get a logger for this document
        logger = DocutilsDocLogger(document)

        # get markdown parsing configuration
        try:
            md_config = create_myst_config(document.settings)
        except (TypeError, ValueError) as error:
            logger.error(f"myst configuration invalid: {error.args[0]}")
            md_config = MdParserConfig()

        # get notebook rendering configuration
        try:
            nb_config = create_myst_config(document.settings, NbParserConfig, "nb_")
        except (TypeError, ValueError) as error:
            logger.error(f"myst-nb configuration invalid: {error.args[0]}")
            nb_config = NbParserConfig()

        # convert inputstring to notebook
        # note docutils does not support the full custom format mechanism
        if nb_config.read_as_md:
            nb_reader = NbReader(
                partial(
                    read_myst_markdown_notebook,
                    config=md_config,
                    add_source_map=True,
                ),
                md_config,
                {"type": "plugin", "name": "myst_nb_md"},
            )
        else:
            nb_reader = NbReader(standard_nb_read, md_config)
        notebook = nb_reader.read(inputstring)

        # update the global markdown config with the file-level config
        warning = lambda wtype, msg: create_warning(  # noqa: E731
            document, msg, line=1, append_to=document, subtype=wtype
        )
        nb_reader.md_config = merge_file_level(
            nb_reader.md_config, notebook.metadata, warning
        )

        # Update mystnb configuration with notebook level metadata
        if nb_config.metadata_key in notebook.metadata:
            overrides = nb_node_to_dict(notebook.metadata[nb_config.metadata_key])
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

        # Setup the markdown parser
        mdit_parser = create_md_parser(nb_reader.md_config, DocutilsNbRenderer)
        mdit_parser.options["document"] = document
        mdit_parser.options["nb_config"] = nb_config
        mdit_renderer: DocutilsNbRenderer = mdit_parser.renderer  # type: ignore
        mdit_env: dict[str, Any] = {}

        # load notebook element renderer class from entry-point name
        # this is separate from DocutilsNbRenderer, so that users can override it
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
        with create_client(notebook, document_source, nb_config, logger) as nb_client:
            mdit_parser.options["nb_client"] = nb_client
            # convert to docutils AST, which is added to the document
            mdit_renderer.render(mdit_tokens, mdit_parser.options, mdit_env)

        # save final execution data
        if nb_client.exec_metadata:
            document["nb_exec_data"] = nb_client.exec_metadata

        if nb_config.output_folder:
            # write final (updated) notebook to output folder (utf8 is standard encoding)
            content = nbformat.writes(notebook).encode("utf-8")
            nb_renderer.write_file(["processed.ipynb"], content, overwrite=True)

            # if we are using an HTML writer, dynamically add the CSS to the output
            if nb_config.append_css and hasattr(document.settings, "stylesheet"):
                css_paths = []

                css_paths.append(
                    nb_renderer.write_file(
                        ["mystnb.css"],
                        (import_resources.files(static) / "mystnb.css").read_bytes(),
                        overwrite=True,
                    )
                )
                fmt = get_formatter_by_name("html", style="default")
                css_paths.append(
                    nb_renderer.write_file(
                        ["pygments.css"],
                        fmt.get_style_defs(".code").encode("utf-8"),
                        overwrite=True,
                    )
                )
                css_paths = [os.path.abspath(path) for path in css_paths]
                # stylesheet and stylesheet_path are mutually exclusive
                if document.settings.stylesheet_path:
                    document.settings.stylesheet_path.extend(css_paths)
                if document.settings.stylesheet:
                    document.settings.stylesheet.extend(css_paths)

            # TODO also handle JavaScript

        # remove temporary state
        document.attributes.pop("nb_renderer")


class DocutilsNbRenderer(DocutilsRenderer, MditRenderMixin):
    """A docutils-only renderer for Jupyter Notebooks."""

    def render_nb_initialise(self, token: SyntaxTreeNode) -> None:
        metadata = self.nb_client.nb_metadata
        special_keys = ["kernelspec", "language_info", "source_map"]
        for key in special_keys:
            # save these special keys on the document, rather than as docinfo
            if key in metadata:
                self.document[f"nb_{key}"] = metadata.get(key)

        if self.nb_config.metadata_to_fm:
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
        self, token: SyntaxTreeNode, outputs: list[NotebookNode]
    ) -> None:
        """Render a notebook code cell's outputs."""
        cell_index = token.meta["index"]
        metadata = token.meta["metadata"]
        line = token_line(token)
        # render the outputs
        mime_priority = get_mime_priority(
            self.nb_config.builder_name, self.nb_config.mime_priority_overrides
        )
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
                # Note, this is different to the sphinx implementation,
                # here we directly select a single output, based on the mime_priority,
                # as opposed to output all mime types, and select in a post-transform
                # (the mime_priority must then be set for the output format)

                try:
                    mime_type = next(x for x in mime_priority if x in output["data"])
                except StopIteration:
                    if output["data"]:
                        create_warning(
                            self.document,
                            "No output mime type found from render_priority "
                            f"(cell<{cell_index}>.output<{output_index}>",
                            line=line,
                            append_to=self.current_node,
                            # wtype=DEFAULT_LOG_TYPE,
                            subtype=MystNBWarnings.MIME_TYPE,
                        )
                else:
                    figure_options = (
                        self.get_cell_level_config(
                            "render_figure_options", metadata, line=line
                        )
                        or None
                    )

                    with create_figure_context(self, figure_options, line):
                        _nodes = self.nb_renderer.render_mime_type(
                            MimeData(
                                mime_type,
                                output["data"][mime_type],
                                cell_metadata=metadata,
                                output_metadata=output.get("metadata", {}),
                                cell_index=cell_index,
                                output_index=output_index,
                                line=line,
                            ),
                        )
                        self.current_node.extend(_nodes)
                        self.add_line_and_source_path_r(_nodes, token)
            else:
                create_warning(
                    self.document,
                    f"Unsupported output type: {output.output_type}",
                    line=line,
                    append_to=self.current_node,
                    # wtype=DEFAULT_LOG_TYPE,
                    subtype=MystNBWarnings.OUTPUT_TYPE,
                )


def _run_cli(
    writer_name: str, builder_name: str, writer_description: str, argv: list[str] | None
):
    """Run the command line interface for a particular writer."""
    publish_cmdline(
        parser=Parser(),
        writer_name=writer_name,
        description=(
            f"Generates {writer_description} from standalone MyST Notebook sources.\n"
            f"{default_description}\n"
            "External outputs are written to `--nb-output-folder`.\n"
        ),
        # to see notebook execution info by default
        settings_overrides={"report_level": 1, "nb_builder_name": builder_name},
        argv=argv,
    )


def cli_html(argv: list[str] | None = None) -> None:
    """Cmdline entrypoint for converting MyST to HTML."""
    _run_cli("html", "html", "(X)HTML documents", argv)


def cli_html5(argv: list[str] | None = None):
    """Cmdline entrypoint for converting MyST to HTML5."""
    _run_cli("html5", "html", "HTML5 documents", argv)


def cli_latex(argv: list[str] | None = None):
    """Cmdline entrypoint for converting MyST to LaTeX."""
    _run_cli("latex", "latex", "LaTeX documents", argv)


def cli_xml(argv: list[str] | None = None):
    """Cmdline entrypoint for converting MyST to XML."""
    _run_cli("xml", "xml", "Docutils-native XML", argv)


def cli_pseudoxml(argv: list[str] | None = None):
    """Cmdline entrypoint for converting MyST to pseudo-XML."""
    _run_cli("pseudoxml", "html", "pseudo-XML", argv)
