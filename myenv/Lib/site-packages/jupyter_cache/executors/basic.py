import logging
import multiprocessing as mproc
import os
from pathlib import Path
import tempfile
from typing import NamedTuple, Tuple

from jupyter_cache.base import JupyterCacheAbstract, ProjectNb
from jupyter_cache.cache.db import NbProjectRecord
from jupyter_cache.executors.base import ExecutorRunResult, JupyterExecutorAbstract
from jupyter_cache.executors.utils import (
    ExecutionResult,
    copy_assets,
    create_cache_bundle,
    single_nb_execution,
)

REPORT_LEVEL = logging.INFO + 1
logging.addLevelName(REPORT_LEVEL, "REPORT")


class ProcessData(NamedTuple):
    """Data for the process worker."""

    pk: int
    uri: str
    cache: JupyterCacheAbstract
    timeout: int
    allow_errors: bool


class ExecutionWorkerBase:
    """Base execution worker.

    Note this must be pickleable.
    """

    @property
    def logger(self) -> logging.Logger:
        raise NotImplementedError

    def log_info(self, msg: str):
        self.logger.info(msg)

    def execute(self, project_nb: ProjectNb, data: ProcessData) -> ExecutionResult:
        raise NotImplementedError

    def __call__(self, data: ProcessData) -> Tuple[int, str]:
        try:
            project_nb = data.cache.get_project_notebook(data.pk)
        except Exception:
            self.logger.error(
                "Failed Retrieving: %s" % data.uri,
                exc_info=True,
            )
            return (2, data.uri)

        try:
            self.log_info("Executing: %s" % project_nb.uri)
            result = self.execute(project_nb, data)
        except Exception:
            self.logger.error(
                "Failed Executing: %s" % data.uri,
                exc_info=True,
            )
            return (2, data.uri)

        if result.err:
            self.logger.warning(
                "Execution Excepted: %s\n%s: %s"
                % (project_nb.uri, type(result.err).__name__, str(result.err))
            )
            NbProjectRecord.set_traceback(
                project_nb.uri, result.exc_string, data.cache.db
            )
            return (1, data.uri)

        self.log_info("Execution Successful: %s" % project_nb.uri)
        try:
            # TODO deal with artifact retrieval
            bundle = create_cache_bundle(
                project_nb, result.cwd, None, result.time, result.exc_string
            )
            data.cache.cache_notebook_bundle(
                bundle, check_validity=False, overwrite=True
            )
        except Exception:
            self.logger.error(
                "Failed Caching: %s" % data.uri,
                exc_info=True,
            )
            return (2, data.uri)

        return (0, data.uri)


class ExecutionWorkerLocalSerial(ExecutionWorkerBase):
    """Execution worker, that executes in local folder."""

    def __init__(self, logger: logging.Logger) -> None:
        super().__init__()
        self._logger = logger

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @staticmethod
    def execute(project_nb: ProjectNb, data: ProcessData) -> ExecutionResult:
        cwd = str(Path(project_nb.uri).parent)
        return single_nb_execution(
            project_nb.nb,
            cwd=cwd,
            timeout=data.timeout,
            allow_errors=data.allow_errors,
        )


class ExecutionWorkerTempSerial(ExecutionWorkerBase):
    """Execution worker, that executes in temporary folder."""

    def __init__(self, logger: logging.Logger) -> None:
        super().__init__()
        self._logger = logger

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @staticmethod
    def execute(project_nb: ProjectNb, data: ProcessData) -> ExecutionResult:
        with tempfile.TemporaryDirectory() as cwd:
            copy_assets(project_nb.uri, project_nb.assets, cwd)
            return single_nb_execution(
                project_nb.nb,
                cwd=cwd,
                timeout=data.timeout,
                allow_errors=data.allow_errors,
            )


class ExecutionWorkerLocalMProc(ExecutionWorkerBase):
    """Execution worker, that executes in local folder."""

    @property
    def logger(self) -> logging.Logger:
        return mproc.get_logger()

    def log_info(self, msg: str):
        # multiprocessing logs a lot at info level that we do not want to see
        self.logger.log(REPORT_LEVEL, msg)

    @staticmethod
    def execute(project_nb: ProjectNb, data: ProcessData) -> ExecutionResult:
        cwd = str(Path(project_nb.uri).parent)
        return single_nb_execution(
            project_nb.nb,
            cwd=cwd,
            timeout=data.timeout,
            allow_errors=data.allow_errors,
        )


class ExecutionWorkerTempMProc(ExecutionWorkerBase):
    """Execution worker, that executes in temporary folder."""

    @property
    def logger(self) -> logging.Logger:
        return mproc.get_logger()

    def log_info(self, msg: str):
        # multiprocessing logs a lot at info level that we do not want to see
        self.logger.log(REPORT_LEVEL, msg)

    @staticmethod
    def execute(project_nb: ProjectNb, data: ProcessData) -> ExecutionResult:
        with tempfile.TemporaryDirectory() as cwd:
            copy_assets(project_nb.uri, project_nb.assets, cwd)
            return single_nb_execution(
                project_nb.nb,
                cwd=cwd,
                timeout=data.timeout,
                allow_errors=data.allow_errors,
            )


class JupyterExecutorLocalSerial(JupyterExecutorAbstract):
    """An implementation of an executor; executing locally in serial."""

    _EXECUTION_WORKER = ExecutionWorkerLocalSerial

    def run_and_cache(
        self,
        *,
        filter_uris=None,
        filter_pks=None,
        timeout=30,
        allow_errors=False,
        force=False,
    ) -> ExecutorRunResult:
        # Get the notebook that require re-execution
        execute_records = self.get_records(
            filter_uris, filter_pks, clear_tracebacks=True, force=force
        )

        self.logger.info("Executing %s notebook(s) in serial" % len(execute_records))

        results = [
            self._EXECUTION_WORKER(self.logger)(
                ProcessData(record.pk, record.uri, self.cache, timeout, allow_errors)
            )
            for record in execute_records
        ]

        return ExecutorRunResult(
            succeeded=[p for i, p in results if i == 0],
            excepted=[p for i, p in results if i == 1],
            errored=[p for i, p in results if i == 2],
        )


class JupyterExecutorTempSerial(JupyterExecutorLocalSerial):
    """An implementation of an executor; executing in a temporary folder in serial."""

    _EXECUTION_WORKER = ExecutionWorkerTempSerial


class JupyterExecutorLocalMproc(JupyterExecutorAbstract):
    """An implementation of an executor; executing locally in parallel."""

    _EXECUTION_WORKER = ExecutionWorkerLocalMProc

    def run_and_cache(
        self,
        *,
        filter_uris=None,
        filter_pks=None,
        timeout=30,
        allow_errors=False,
        force=False,
    ) -> ExecutorRunResult:
        # Get the notebook that require re-execution
        execute_records = self.get_records(
            filter_uris, filter_pks, clear_tracebacks=True
        )

        self.logger.info(
            "Executing %s notebook(s) over pool of %s processors"
            % (len(execute_records), os.cpu_count())
        )
        mproc.log_to_stderr(
            REPORT_LEVEL if self.logger.level == logging.INFO else self.logger.level
        )

        with mproc.Pool() as pool:
            results = pool.map(
                self._EXECUTION_WORKER(),
                [
                    ProcessData(
                        record.pk, record.uri, self.cache, timeout, allow_errors
                    )
                    for record in execute_records
                ],
            )
        return ExecutorRunResult(
            succeeded=[p for i, p in results if i == 0],
            excepted=[p for i, p in results if i == 1],
            errored=[p for i, p in results if i == 2],
        )


class JupyterExecutorTempMproc(JupyterExecutorLocalMproc):
    """An implementation of an executor; executing in a temporary directory and in parallel."""

    _EXECUTION_WORKER = ExecutionWorkerTempMProc
