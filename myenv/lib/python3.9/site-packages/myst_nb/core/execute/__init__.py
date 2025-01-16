from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from .base import ExecutionError, ExecutionResult, NotebookClientBase  # noqa: F401
from .cache import NotebookClientCache
from .direct import NotebookClientDirect
from .inline import NotebookClientInline

if TYPE_CHECKING:
    from nbformat import NotebookNode

    from myst_nb.core.config import NbParserConfig
    from myst_nb.core.loggers import LoggerType


def create_client(
    notebook: NotebookNode,
    source: str,
    nb_config: NbParserConfig,
    logger: LoggerType,
    read_fmt: None | dict = None,
) -> NotebookClientBase:
    """Create a notebook execution client, to update its outputs.

    This function may execute the notebook if necessary, to update its outputs,
    or populate from a cache.

    :param notebook: The notebook to update.
    :param source: Path to or description of the input source being processed.
    :param nb_config: The configuration for the notebook parser.
    :param logger: The logger to use.
    :param read_fmt: The format of the input source (to parse to jupyter cache)

    :returns: The updated notebook, and the (optional) execution metadata.
    """
    # path should only be None when using docutils programmatically,
    # e.g. source="<string>"
    try:
        path = Path(source) if Path(source).is_file() else None
    except OSError:
        path = None  # occurs on Windows for `source="<string>"`

    # check if the notebook is excluded from execution by pattern
    if path is not None and nb_config.execution_excludepatterns:
        posix_path = PurePosixPath(path.as_posix())
        for pattern in nb_config.execution_excludepatterns:
            if posix_path.match(pattern):
                logger.info(f"Excluded from execution by pattern: {pattern!r}")
                return NotebookClientBase(notebook, path, nb_config, logger)

    # 'auto' mode only executes the notebook if it is missing at least one output
    missing_outputs = (
        len(cell.outputs) == 0 for cell in notebook.cells if cell["cell_type"] == "code"
    )
    if nb_config.execution_mode == "auto" and not any(missing_outputs):
        logger.info("Skipped execution in 'auto' mode (all outputs present)")
        return NotebookClientBase(notebook, path, nb_config, logger)

    if nb_config.execution_mode in ("auto", "force"):
        return NotebookClientDirect(notebook, path, nb_config, logger)

    if nb_config.execution_mode == "cache":
        return NotebookClientCache(notebook, path, nb_config, logger, read_fmt=read_fmt)

    if nb_config.execution_mode == "inline":
        return NotebookClientInline(notebook, path, nb_config, logger)

    return NotebookClientBase(notebook, path, nb_config, logger)
