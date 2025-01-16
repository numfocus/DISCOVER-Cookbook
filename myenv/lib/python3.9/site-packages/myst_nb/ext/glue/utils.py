"""Utilities for working with docutils and sphinx.

We intentionally do no import sphinx in this module,
in order to allow docutils-only use without sphinx installed.
"""
from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any

from docutils import nodes

from myst_nb.core.render import NbElementRenderer
from myst_nb.core.variables import (
    RetrievalError,
    VariableOutput,
    create_warning,
    is_sphinx,
)

if TYPE_CHECKING:
    from sphinx.environment import BuildEnvironment

glue_warning = partial(create_warning, subtype="glue")


class PendingGlueReference(nodes.Element):
    """A glue reference to another document."""

    @property
    def refdoc(self) -> str:
        return self.attributes["refdoc"]

    @property
    def key(self) -> str:
        return self.attributes["key"]

    @property
    def inline(self) -> bool:
        return self.attributes.get("inline", False)

    @property
    def gtype(self) -> str | None:
        return self.attributes.get("gtype", None)


class PendingGlueReferenceError(Exception):
    """An error occurred while resolving a pending glue reference."""


def create_pending_glue_ref(
    document: nodes.document,
    source: str,
    line: int,
    rel_doc: str,
    key: str,
    inline: bool = False,
    gtype: str | None = None,
    **kwargs: Any,
) -> PendingGlueReference:
    """Create a pending glue reference."""
    if not is_sphinx(document):
        raise PendingGlueReferenceError(
            "Pending glue references are only supported in sphinx."
        )
    env: BuildEnvironment = document.settings.env
    _, filepath = env.relfn2path(rel_doc, env.docname)
    refdoc = env.path2doc(filepath)
    if refdoc is None:
        raise PendingGlueReferenceError(
            f"Pending glue reference document not found: {filepath!r}."
        )
    ref = PendingGlueReference(
        refdoc=refdoc, key=key, inline=inline, gtype=gtype, **kwargs
    )
    ref.source = source
    ref.line = line
    return ref


def retrieve_glue_data(document: nodes.document, key: str) -> VariableOutput:
    """Retrieve the glue data from a specific document."""
    msg = f"No key {key!r} found in glue data for this document."
    if "nb_renderer" not in document:
        raise RetrievalError(msg)
    element: NbElementRenderer = document["nb_renderer"]
    glue_data = element.renderer.nb_client.glue_data

    if key not in glue_data:
        raise RetrievalError(msg)

    return VariableOutput(
        data=glue_data[key]["data"],
        metadata=glue_data[key].get("metadata", {}),
        nb_renderer=element,
        vtype="glue",
    )
