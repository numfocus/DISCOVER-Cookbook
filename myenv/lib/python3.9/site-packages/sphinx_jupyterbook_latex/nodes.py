"""AST nodes to designate notebook components."""
from typing import Any, cast

from docutils import nodes
from sphinx.application import Sphinx

CR = "\n"


def sphinx_encode(string: str) -> str:
    """Replace tilde, hyphen and single quotes with their LaTeX commands."""
    return (
        string.replace("~", "\\textasciitilde{}")
        .replace("-", "\\sphinxhyphen{}")
        .replace("'", "\\textquotesingle{}")
    )


def get_index(body, text):
    index = 0
    indices = [i for i, x in enumerate(body) if x == text]
    for i in indices:
        if body[i - 1] == "\\sphinxstylestrong{":
            index = i
            break
    return index


def skip(self, node: nodes.Element):
    """skip a node in the visitor."""
    raise nodes.SkipNode


class HiddenCellNode(nodes.Element):
    """A node that will not be rendered."""

    def __init__(self, rawsource="", *children, **attributes):
        super().__init__("", **attributes)

    @classmethod
    def add_node(cls, app: Sphinx) -> None:
        add_node = cast(Any, app.add_node)  # has the wrong typing for sphinx<4
        add_node(
            cls,
            override=True,
            html=(visit_HiddenCellNode, None),
            latex=(visit_HiddenCellNode, None),
            textinfo=(visit_HiddenCellNode, None),
            text=(visit_HiddenCellNode, None),
            man=(visit_HiddenCellNode, None),
        )


def visit_HiddenCellNode(self, node):
    raise nodes.SkipNode


class RootHeader(nodes.Element):
    """A node to override the rendering of sub-headers in the index file."""

    def __init__(self, rawsource="", *, level: int = 0, **attributes):
        super().__init__(rawsource, level=level, **attributes)

    @classmethod
    def add_node(cls, app: Sphinx) -> None:
        add_node = cast(Any, app.add_node)  # has the wrong typing for sphinx<4
        add_node(
            cls,
            override=True,
            latex=(visit_RootHeader, depart_RootHeader),
            html=(visit_RootHeader, depart_RootHeader),
            textinfo=(skip, None),
            text=(skip, None),
            man=(skip, None),
        )


def visit_RootHeader(self, node: RootHeader) -> None:
    node["header_text"] = sphinx_encode(node.astext())

    strong = nodes.strong("")
    strong.children = node.children

    line = nodes.line("")
    line.append(strong)

    line_block = nodes.line_block("")
    line_block.append(line)

    node.children = []
    node.append(line_block)


def depart_RootHeader(self, node: RootHeader) -> None:
    index = get_index(self.body, node["header_text"])
    size = "\\Large " if node["level"] <= 2 else "\\large "
    if index:
        self.body[index] = size + node["header_text"]
    # else throw an error


class CellOutput(nodes.Element):
    """A node for code cell outputs designed for latex."""

    def __init__(self, rawsource="", *children, **attributes):
        super().__init__("", **attributes)

    @classmethod
    def add_node(cls, app: Sphinx) -> None:
        add_node = cast(Any, app.add_node)  # has the wrong typing for sphinx<4
        add_node(
            cls,
            override=True,
            latex=(visit_CellOutput, depart_CellOutput),
        )


def visit_CellOutput(self, node) -> None:
    self.body.append("\\begin{sphinxVerbatimOutput}" + CR)


def depart_CellOutput(self, node) -> None:
    self.body.append("\\end{sphinxVerbatimOutput}" + CR)


class CellInput(nodes.Element):
    """A node for code cell inputs designed for latex."""

    def __init__(self, rawsource="", *children, **attributes):
        super().__init__("", **attributes)

    @classmethod
    def add_node(cls, app: Sphinx) -> None:
        add_node = cast(Any, app.add_node)  # has the wrong typing for sphinx<4
        add_node(
            cls,
            override=True,
            latex=(visit_CellInput, depart_CellInput),
        )


def visit_CellInput(self, node) -> None:
    self.body.append("\\begin{sphinxVerbatimInput}" + CR)


def depart_CellInput(self, node) -> None:
    self.body.append("\\end{sphinxVerbatimInput}" + CR)
