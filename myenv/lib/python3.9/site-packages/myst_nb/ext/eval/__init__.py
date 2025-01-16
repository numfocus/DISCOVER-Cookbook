"""Roles/directives for evaluating variables in the notebook."""
from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any

from docutils import nodes
from docutils.parsers.rst import directives as spec

from myst_nb.core.execute.base import EvalNameError
from myst_nb.core.render import NbElementRenderer
from myst_nb.core.variables import (
    RetrievalError,
    VariableOutput,
    create_warning,
    render_variable_outputs,
)
from myst_nb.ext.utils import DirectiveBase, RoleBase

try:
    from sphinx.domains import Domain
except ImportError:
    # for docutils only use
    Domain = object  # type: ignore

if TYPE_CHECKING:
    from sphinx.application import Sphinx

    from myst_nb.docutils_ import DocutilsApp

eval_warning = partial(create_warning, subtype="eval")


def retrieve_eval_data(document: nodes.document, key: str) -> list[VariableOutput]:
    """Retrieve the glue data from a specific document."""
    if "nb_renderer" not in document:
        raise RetrievalError("This document does not have a running kernel")
    element: NbElementRenderer = document["nb_renderer"]

    # evaluate the variable
    try:
        outputs = element.renderer.nb_client.eval_variable(key)
    except NotImplementedError:
        raise RetrievalError("This document does not have a running kernel")
    except EvalNameError:
        raise RetrievalError(
            f"The expression {key!r} is not valid according to the configured pattern"
        )
    except Exception as exc:
        raise RetrievalError(f"variable evaluation error: {exc}")
    if not outputs:
        raise RetrievalError(f"expression {key!r} does not return any outputs")

    # the returned outputs could be one of the following:
    # https://nbformat.readthedocs.io/en/latest/format_description.html#code-cell-outputs

    for output in outputs:
        if output.get("output_type") == "error":
            msg = f"{output.get('ename', '')}: {output.get('evalue', '')}"
            raise RetrievalError(msg)

    return [
        VariableOutput(
            data=output.get("data", {}),
            metadata=output.get("metadata", {}),
            nb_renderer=element,
            vtype="eval",
            index=i,
        )
        for i, output in enumerate(outputs)
    ]


class EvalRoleAny(RoleBase):
    """A role for evaluating value outputs from the kernel,
    using render priority to decide the output mime type.
    """

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        try:
            data = retrieve_eval_data(self.document, self.text)
        except RetrievalError as exc:
            return [], [eval_warning(str(exc), self.document, self.line)]

        # for text/plain, we want to strip quotes from strings
        for output in data:
            output.metadata["strip_text_quotes"] = True

        _nodes = render_variable_outputs(
            data,
            self.document,
            self.line,
            self.source,
            inline=True,
        )

        return _nodes, []


class EvalDirectiveAny(DirectiveBase):
    """A directive for evaluating value outputs from the kernel,
    using render priority to decide the output mime type.
    """

    required_arguments = 1  # the key
    final_argument_whitespace = False
    has_content = False

    def run(self) -> list[nodes.Node]:
        """Run the directive."""
        try:
            data = retrieve_eval_data(self.document, self.arguments[0])
        except RetrievalError as exc:
            return [eval_warning(str(exc), self.document, self.line)]
        return render_variable_outputs(
            data,
            self.document,
            self.line,
            self.source,
            inline=False,
        )


class EvalFigureDirective(DirectiveBase):
    """A directive for pasting code outputs from notebooks, wrapped in a figure.

    Mirrors:
    https://github.com/docutils-mirror/docutils/blob/9649abee47b4ce4db51be1d90fcb1fb500fa78b3/docutils/parsers/rst/directives/images.py#95
    """

    required_arguments = 1  # the key
    final_argument_whitespace = False
    has_content = True

    def align(argument):
        return spec.choice(argument, ("left", "center", "right"))

    def figwidth_value(argument):
        return spec.length_or_percentage_or_unitless(argument, "px")

    option_spec = {
        # note we don't add converters for image options,
        # since this is handled in `NbElementRenderer.render_image`
        "alt": spec.unchanged,
        "height": spec.unchanged,
        "width": spec.unchanged,
        "scale": spec.unchanged,
        "class": spec.unchanged,
        "figwidth": figwidth_value,
        "figclass": spec.class_option,
        "align": align,
        "name": spec.unchanged,
    }

    def run(self):
        try:
            data = retrieve_eval_data(self.document, self.arguments[0])
        except RetrievalError as exc:
            return [eval_warning(str(exc), self.document, self.line)]

        render: dict[str, Any] = {}
        for key in ("alt", "height", "width", "scale", "class"):
            if key in self.options:
                render.setdefault("image", {})[
                    key.replace("classes", "class")
                ] = self.options[key]

        mime_nodes = render_variable_outputs(
            data, self.document, self.line, self.source, render=render
        )

        # note: most of this is copied directly from sphinx.Figure

        # create figure node
        figure_node = nodes.figure("", *mime_nodes)
        self.set_source_info(figure_node)

        # add attributes
        figwidth = self.options.pop("figwidth", None)
        figclasses = self.options.pop("figclass", None)
        align = self.options.pop("align", None)
        if figwidth is not None:
            figure_node["width"] = figwidth
        if figclasses:
            figure_node["classes"] += figclasses
        if align:
            figure_node["align"] = align

        # add target
        self.add_name(figure_node)

        # create the caption and legend
        if self.content:
            node = nodes.Element()  # anonymous container for parsing
            self.state.nested_parse(self.content, self.content_offset, node)
            first_node = node[0]
            if isinstance(first_node, nodes.paragraph):
                caption = nodes.caption(first_node.rawsource, "", *first_node.children)
                caption.source = first_node.source
                caption.line = first_node.line
                figure_node += caption
            elif not (isinstance(first_node, nodes.comment) and len(first_node) == 0):
                error = eval_warning(
                    "Figure caption must be a paragraph or empty comment.",
                    self.document,
                    self.lineno,
                )
                return [figure_node, error]
            if len(node) > 1:
                figure_node += nodes.legend("", *node[1:])

        return [figure_node]


class NbEvalDomain(Domain):
    """A sphinx domain for defining eval roles and directives.

    Note, the only reason we use this,
    is that sphinx will not allow for `:` in a directive/role name,
    if it is part of a domain.
    """

    name = "eval"
    label = "NotebookEval"

    # data version, bump this when the format of self.data changes
    data_version = 1

    directives = {"figure": EvalFigureDirective}
    roles: dict = {}

    def merge_domaindata(self, *args, **kwargs):
        pass

    def resolve_any_xref(self, *args, **kwargs):
        return []


def load_eval_sphinx(app: Sphinx) -> None:
    """Load the eval domain."""
    app.add_role("eval", EvalRoleAny(), override=True)
    app.add_directive("eval", EvalDirectiveAny, override=True)
    app.add_domain(NbEvalDomain)


def load_eval_docutils(app: DocutilsApp) -> None:
    app.roles["eval"] = EvalRoleAny()
    app.directives["eval"] = EvalDirectiveAny
    app.directives["eval:figure"] = EvalFigureDirective
