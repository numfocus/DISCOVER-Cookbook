"""Module for handling different functions to read "notebook-like" files."""

from typing import Any, Callable, Dict, Set

import nbformat as nbf

from .entry_points import ENTRY_POINT_GROUP_READER, get_entry_point, list_group_names

DEFAULT_READ_DATA = (("name", "nbformat"), ("type", "plugin"))


def nbf_reader(uri: str) -> nbf.NotebookNode:
    """Standard notebook reader."""
    return nbf.read(uri, nbf.NO_CONVERT)


def jupytext_reader(uri: str) -> nbf.NotebookNode:
    """Jupytext notebook reader."""
    try:
        import jupytext
    except ImportError:
        raise ImportError("jupytext must be installed to use this reader")
    return jupytext.read(uri)


def list_readers() -> Set[str]:
    """List all available readers."""
    return list_group_names(ENTRY_POINT_GROUP_READER)


def get_reader(data: Dict[str, Any]) -> Callable[[str], nbf.NotebookNode]:
    """Returns a function to read a file URI and return a notebook."""
    if data.get("type") == "plugin":
        key = data.get("name", "")
        reader = get_entry_point(ENTRY_POINT_GROUP_READER, key)
        if reader is not None:
            return reader.load()
    raise ValueError(f"No reader found for: {data!r}")


class NbReadError(IOError):
    """Error raised when a notebook cannot be read."""
