"""Extension utilities for extensions.

We intentionally do no import sphinx in this module,
in order to allow docutils-only use without sphinx installed.
"""
from __future__ import annotations

from typing import Any

from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst.states import Inliner
from docutils.utils import unescape

from myst_nb._compat import findall


def set_source_info(node: nodes.Node, source: str, line: int) -> None:
    """Set the source info for a node and its descendants."""
    for _node in findall(node)(include_self=True):
        _node.source = source
        _node.line = line


class RoleBase:
    """A base class for creating a role."""

    @property
    def document(self) -> nodes.document:
        """Get the document."""
        return self.inliner.document

    def set_source_info(self, node: nodes.Node) -> None:
        """Set the source info for a node and its descendants."""
        set_source_info(node, self.source, self.line)

    def __call__(
        self,
        name: str,
        rawtext: str,
        text: str,
        lineno: int,
        inliner: Inliner,
        options=None,
        content=(),
    ) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        self.text: str = unescape(text)
        self.inliner = inliner
        self.rawtext = rawtext
        source, line = inliner.reporter.get_source_and_line(lineno)
        self.source: str = source
        self.line: int = line
        return self.run()

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        """Run the role."""
        raise NotImplementedError


class DirectiveBase(Directive):
    """A base class for creating a directive."""

    @property
    def document(self) -> nodes.document:
        return self.state.document

    def __init__(self, *args, **kwargs) -> None:
        self.arguments: list[str]
        self.options: dict[str, Any]
        self.content: str
        super().__init__(*args, **kwargs)
        source, line = self.state_machine.get_source_and_line(self.lineno)
        self.source: str = source
        self.line: int = line

    def set_source_info(self, node: nodes.Node) -> None:
        """Set source and line number to the node and its descendants."""
        nodes = node if isinstance(node, (list, tuple)) else [node]
        for _node in nodes:
            set_source_info(_node, self.source, self.line)
