from pathlib import Path
import shutil
import traceback
from typing import Any, List, Optional, Union

import attr
from nbclient import execute as executenb
from nbclient.client import CellExecutionError, CellTimeoutError
from nbformat import NotebookNode

from jupyter_cache.base import CacheBundleIn, ProjectNb
from jupyter_cache.cache.main import NbArtifacts
from jupyter_cache.utils import Timer, to_relative_paths


@attr.s()
class ExecutionResult:
    nb: NotebookNode = attr.ib()
    cwd: str = attr.ib()
    time: float = attr.ib()
    err: Optional[Union[CellExecutionError, CellTimeoutError]] = attr.ib(default=None)
    exc_string: Optional[str] = attr.ib(default=None)


def single_nb_execution(
    nb: NotebookNode,
    cwd: Optional[str],
    timeout: Optional[int],
    allow_errors: bool,
    meta_override: bool = True,
    record_timing: bool = False,
    **kwargs: Any,
) -> ExecutionResult:
    """Execute notebook in place.

    :param cwd: If supplied, the kernel will run in this directory.
    :param timeout: The time to wait (in seconds) for output from executions.
                If a cell execution takes longer, a ``TimeoutError`` is raised.
    :param allow_errors: If ``False`` when a cell raises an error the
                execution is stopped and a ``CellExecutionError`` is raised.
    :param meta_override: If ``True`` then timeout and allow_errors may be overridden
                by equivalent keys in nb.metadata.execution
    :param kwargs: Additional keyword arguments to pass to the ``NotebookClient``.

    :returns: The execution time in seconds
    """
    if meta_override and "execution" in nb.metadata:
        if "timeout" in nb.metadata.execution:
            timeout = nb.metadata.execution.timeout
        if "allow_errors" in nb.metadata.execution:
            allow_errors = nb.metadata.execution.allow_errors

    error = exc_string = None
    # TODO nbclient with record_timing=True will add execution data to each cell
    timer = Timer()
    with timer:
        try:
            executenb(
                nb,
                cwd=cwd,
                timeout=timeout,
                allow_errors=allow_errors,
                record_timing=record_timing,
                **kwargs,
            )
        except (CellExecutionError, CellTimeoutError) as err:
            error = err
            exc_string = "".join(traceback.format_exc())

    return ExecutionResult(nb, cwd, timer.last_split, error, exc_string)


def copy_assets(uri: str, assets: List[str], folder: str) -> List[Path]:
    """Copy notebook assets to the folder the notebook will be executed in."""
    asset_files = []
    relative_paths = to_relative_paths(assets, Path(uri).parent)
    for path, rel_path in zip(assets, relative_paths):
        temp_file = Path(folder).joinpath(rel_path)
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, temp_file)
        asset_files.append(temp_file)
    return asset_files


def create_cache_bundle(
    project_nb: ProjectNb,
    execdir: Optional[str],
    asset_files: Optional[List[Path]],
    exec_time: float,
    exec_tb: Optional[str],
) -> CacheBundleIn:
    """Create a cache bundle to save."""
    return CacheBundleIn(
        project_nb.nb,
        project_nb.uri,
        # TODO retrieve assets that have changed file mtime?
        artifacts=(
            NbArtifacts(
                [p for p in Path(execdir).glob("**/*") if p not in asset_files],
                execdir,
            )
            if (execdir is not None and asset_files is not None)
            else None
        ),
        data={"execution_seconds": exec_time},
        traceback=exec_tb,
    )
