"""Module for parsing notebooks to Markdown-it tokens."""
from __future__ import annotations

from typing import Any

from markdown_it.main import MarkdownIt
from markdown_it.rules_core import StateCore
from markdown_it.token import Token
from nbformat import NotebookNode

from myst_nb.core.loggers import LoggerType


def nb_node_to_dict(node: NotebookNode) -> dict[str, Any]:
    """Recursively convert a notebook node to a dict."""
    return _nb_node_to_dict(node)


def _nb_node_to_dict(item: Any) -> Any:
    """Recursively convert any notebook nodes to dict."""
    if isinstance(item, NotebookNode):
        return {k: _nb_node_to_dict(v) for k, v in item.items()}
    return item


def notebook_to_tokens(
    notebook: NotebookNode,
    mdit_parser: MarkdownIt,
    mdit_env: dict[str, Any],
    logger: LoggerType,
) -> list[Token]:
    # disable front-matter, since this is taken from the notebook
    mdit_parser.disable("front_matter", ignoreInvalid=True)
    # this stores global state, such as reference definitions

    # Parse block tokens only first, leaving inline parsing to a second phase
    # (required to collect all reference definitions, before assessing references).
    block_tokens = [Token("nb_initialise", "", 0, map=[0, 0])]
    for cell_index, nb_cell in enumerate(notebook.cells):
        # skip empty cells
        if len(nb_cell["source"].strip()) == 0:
            continue

        # skip cells tagged for removal
        tags = nb_cell.metadata.get("tags", [])
        if ("remove_cell" in tags) or ("remove-cell" in tags):
            continue

        # generate tokens
        tokens: list[Token]
        if nb_cell["cell_type"] == "markdown":
            # https://nbformat.readthedocs.io/en/5.1.3/format_description.html#markdown-cells
            # TODO if cell has tag output-caption, then use as caption for next/preceding cell?
            tokens = [
                Token(
                    "nb_cell_markdown_open",
                    "",
                    1,
                    hidden=True,
                    meta={
                        "index": cell_index,
                        "metadata": nb_node_to_dict(nb_cell["metadata"]),
                    },
                    map=[0, len(nb_cell["source"].splitlines()) - 1],
                ),
            ]
            with mdit_parser.reset_rules():
                # enable only rules up to block
                rules = mdit_parser.core.ruler.get_active_rules()
                mdit_parser.core.ruler.enableOnly(rules[: rules.index("inline")])
                tokens.extend(mdit_parser.parse(nb_cell["source"], mdit_env))
            tokens.append(
                Token(
                    "nb_cell_markdown_close",
                    "",
                    -1,
                    hidden=True,
                ),
            )
        elif nb_cell["cell_type"] == "raw":
            # https://nbformat.readthedocs.io/en/5.1.3/format_description.html#raw-nbconvert-cells
            tokens = [
                Token(
                    "nb_cell_raw",
                    "code",
                    0,
                    content=nb_cell["source"],
                    meta={
                        "index": cell_index,
                        "metadata": nb_node_to_dict(nb_cell["metadata"]),
                    },
                    map=[0, 0],
                )
            ]
        elif nb_cell["cell_type"] == "code":
            # https://nbformat.readthedocs.io/en/5.1.3/format_description.html#code-cells
            # we don't copy the outputs here, since this would
            # greatly increase the memory consumption,
            # instead they will referenced by the cell index
            tokens = [
                Token(
                    "nb_cell_code",
                    "code",
                    0,
                    content=nb_cell["source"],
                    meta={
                        "index": cell_index,
                        "metadata": nb_node_to_dict(nb_cell["metadata"]),
                    },
                    map=[0, 0],
                )
            ]
        else:
            pass  # TODO create warning

        # update token's source lines, using either a source_map (index -> line),
        # set when converting to a notebook, or a pseudo base of the cell index
        smap = notebook.metadata.get("source_map", None)
        start_line = smap[cell_index] if smap else (cell_index + 1) * 10000
        start_line += 1  # use base 1 rather than 0
        for token in tokens:
            if token.map:
                token.map = [start_line + token.map[0], start_line + token.map[1]]
        # also update the source lines for duplicate references
        for dup_ref in mdit_env.get("duplicate_refs", []):
            if "fixed" not in dup_ref:
                dup_ref["map"] = [
                    start_line + dup_ref["map"][0],
                    start_line + dup_ref["map"][1],
                ]
                dup_ref["fixed"] = True

        # add tokens to list
        block_tokens.extend(tokens)

    block_tokens.append(Token("nb_finalise", "", 0, map=[0, 0]))

    # Now all definitions have been gathered, run the inline parsing phase
    state = StateCore("", mdit_parser, mdit_env, block_tokens)
    with mdit_parser.reset_rules():
        rules = mdit_parser.core.ruler.get_active_rules()
        mdit_parser.core.ruler.enableOnly(rules[rules.index("inline") :])
        mdit_parser.core.process(state)

    return state.tokens
