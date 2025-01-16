"""Module for executing notebooks."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from nbformat import NotebookNode
from typing_extensions import TypedDict, final

from myst_nb.core.config import NbParserConfig
from myst_nb.core.loggers import LoggerType
from myst_nb.core.nb_to_tokens import nb_node_to_dict
from myst_nb.ext.glue import extract_glue_data


class ExecutionResult(TypedDict):
    """Result of executing a notebook."""

    mtime: float
    """POSIX timestamp of the execution time"""
    runtime: float | None
    """runtime in seconds"""
    method: str
    """method used to execute the notebook"""
    succeeded: bool
    """True if the notebook executed successfully"""
    error: str | None
    """error type if the notebook failed to execute"""
    traceback: str | None
    """traceback if the notebook failed"""


class ExecutionError(Exception):
    """An exception for failed execution and `execution_raise_on_error` is true."""


class EvalNameError(Exception):
    """An exception for if an evaluation variable name is invalid."""


class NotebookClientBase:
    """A base client for interacting with Jupyter notebooks.

    This class is intended to be used as a context manager,
    and should only be entered once.

    Subclasses should override the `start_client` and `close_client` methods.
    """

    def __init__(
        self,
        notebook: NotebookNode,
        path: Path | None,
        nb_config: NbParserConfig,
        logger: LoggerType,
        **kwargs: Any,
    ):
        """Initialize the client."""
        self._notebook = notebook
        self._path = path
        self._nb_config = nb_config
        self._logger = logger
        self._kwargs = kwargs

        self._glue_data: dict[str, NotebookNode] = {}
        self._exec_metadata: ExecutionResult | None = None

        # get or create source map of cell to source line
        # use 1-based indexing rather than 0, or pseudo base of the cell index
        _source_map: list[int] = notebook.metadata.get("source_map", None)
        self._source_map = [
            (_source_map[i] if _source_map else ((i + 1) * 10000)) + 1
            for i, _ in enumerate(notebook.cells)
        ]

    @final
    def __enter__(self) -> NotebookClientBase:
        """Enter the context manager."""
        self.start_client()
        # extract glue data from the notebook
        self._glue_data = extract_glue_data(
            self.notebook, self._source_map, self.logger
        )
        return self

    @final
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        self.close_client(exc_type, exc_val, exc_tb)

    def start_client(self):
        """Start the client."""

    def finalise_client(self):
        """Finalise the client.

        This is called before final rendering and should be used,
        for example, to finalise the widget state on the metadata.
        """

    def close_client(self, exc_type, exc_val, exc_tb):
        """Close the client."""

    @property
    def notebook(self) -> NotebookNode:
        """Get the notebook."""
        return self._notebook

    @property
    def path(self) -> Path | None:
        """Get the notebook path."""
        return self._path

    @property
    def nb_config(self) -> NbParserConfig:
        """Get the notebook configuration."""
        return self._nb_config

    @property
    def logger(self) -> LoggerType:
        """Get the logger."""
        return self._logger

    @property
    def glue_data(self) -> dict[str, NotebookNode]:
        """Get the glue data."""
        return self._glue_data

    @property
    def exec_metadata(self) -> ExecutionResult | None:
        """Get the execution metadata."""
        return self._exec_metadata

    @exec_metadata.setter
    def exec_metadata(self, value: ExecutionResult):
        """Set the execution metadata."""
        self._exec_metadata = value

    def cell_line(self, cell_index: int) -> int:
        """Get the source line number of a cell."""
        return self._source_map[cell_index]

    @property
    def nb_metadata(self) -> dict[str, Any]:
        """Get the notebook level metadata."""
        return nb_node_to_dict(self.notebook.get("metadata", {}))

    def nb_source_code_lexer(self) -> str | None:
        """Get the lexer for the notebook source code."""
        metadata = self.notebook.get("metadata", {})
        langinfo = metadata.get("language_info") or {}
        lexer = langinfo.get("pygments_lexer") or langinfo.get("name", None)
        if lexer is None:
            lexer = (metadata.get("kernelspec") or {}).get("language", None)
        return lexer

    def code_cell_outputs(
        self, cell_index: int
    ) -> tuple[int | None, list[NotebookNode]]:
        """Get the outputs of a cell.

        :returns: a tuple of the execution_count and the outputs
        :raises IndexError: if the cell index is out of range
        """
        cells = self.notebook.get("cells", [])
        cell = cells[cell_index]
        return cell.get("execution_count", None), cell.get("outputs", [])

    def eval_variable(self, name: str) -> list[NotebookNode]:
        """Retrieve the value of a variable from the kernel.

        :param name: the name of the variable,
            must match the regex `[a-zA-Z][a-zA-Z0-9_]*`

        :returns: code cell outputs
        :raises NotImplementedError: if the execution mode does not support this feature
        :raises EvalNameError: if the variable name is invalid
        """
        raise NotImplementedError
