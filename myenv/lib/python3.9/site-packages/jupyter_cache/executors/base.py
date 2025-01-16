from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional, Set

import attr

from jupyter_cache.base import JupyterCacheAbstract
from jupyter_cache.cache.db import NbProjectRecord
from jupyter_cache.entry_points import (
    ENTRY_POINT_GROUP_EXEC,
    get_entry_point,
    list_group_names,
)

base_logger = logging.getLogger(__name__)


class ExecutionError(Exception):
    pass


@attr.s(slots=True)
class ExecutorRunResult:
    """A container for the execution result."""

    # URIs of notebooks which where successfully executed
    succeeded: List[str] = attr.ib(factory=list)
    # URIs of notebooks which excepted during execution
    excepted: List[str] = attr.ib(factory=list)
    # URIs of notebooks which errored before execution
    errored: List[str] = attr.ib(factory=list)

    def all(self) -> List[str]:
        """Return all notebooks."""
        return self.succeeded + self.excepted + self.errored

    def as_json(self) -> Dict[str, Any]:
        """Return the result as a JSON serializable dict."""
        return {
            "succeeded": self.succeeded,
            "excepted": self.excepted,
            "errored": self.errored,
        }


class JupyterExecutorAbstract(ABC):
    """An abstract class for executing notebooks in a cache."""

    def __init__(self, cache: JupyterCacheAbstract, logger=None):
        self._cache = cache
        self._logger = logger or logging.getLogger(__name__)

    def __repr__(self):
        return f"{self.__class__.__name__}(cache={self._cache})"

    @property
    def cache(self):
        return self._cache

    @property
    def logger(self):
        return self._logger

    def get_records(
        self,
        filter_uris: Optional[List[str]] = None,
        filter_pks: Optional[List[int]] = None,
        clear_tracebacks: bool = True,
        force: bool = False,
    ) -> List[NbProjectRecord]:
        """Return records to execute.

        :param clear_tracebacks: Remove any tracebacks from previous executions
        """
        if force:
            execute_records = self.cache.list_project_records(filter_uris, filter_pks)
        else:
            execute_records = self.cache.list_unexecuted(filter_uris, filter_pks)
        if clear_tracebacks:
            NbProjectRecord.remove_tracebacks(
                [r.pk for r in execute_records], self.cache.db
            )
        return execute_records

    @abstractmethod
    def run_and_cache(
        self,
        *,
        filter_uris: Optional[List[str]] = None,
        filter_pks: Optional[List[int]] = None,
        timeout: Optional[int] = 30,
        allow_errors: bool = False,
        force: bool = False,
        **kwargs: Any,
    ) -> ExecutorRunResult:
        """Run execution, cache successfully executed notebooks and return their URIs

        :param filter_uris: Filter the notebooks in the project to execute by these URIs
        :param filter_pks: Filter the notebooks in the project to execute by these PKs
        :param timeout: Maximum time in seconds to wait for a single cell to run for
        :param allow_errors: Whether to halt execution on the first cell exception
            (provided the cell is not tagged as an expected exception)
        :param force: Whether to force execution of all notebooks, even if they are cached
        :param kwargs: Additional keyword arguments to pass to the executor
        """


def list_executors() -> Set[str]:
    return list_group_names(ENTRY_POINT_GROUP_EXEC)


def load_executor(
    entry_point: str, cache: JupyterCacheAbstract, logger=None
) -> JupyterExecutorAbstract:
    """Retrieve an initialised JupyterExecutor from an entry point."""
    ep = get_entry_point(ENTRY_POINT_GROUP_EXEC, entry_point)
    if ep is None:
        raise ImportError(
            f"Entry point not found: {ENTRY_POINT_GROUP_EXEC}:{entry_point}"
        )
    execute_cls = ep.load()
    return execute_cls(cache=cache, logger=logger)
