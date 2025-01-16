"""Execute a notebook from the cache."""
from __future__ import annotations

from contextlib import nullcontext, suppress
from datetime import datetime
import os
from tempfile import TemporaryDirectory
from typing import ContextManager

from jupyter_cache import get_cache
from jupyter_cache.base import CacheBundleIn
from jupyter_cache.cache.db import NbProjectRecord
from jupyter_cache.executors.utils import single_nb_execution

from .base import ExecutionError, NotebookClientBase


class NotebookClientCache(NotebookClientBase):
    """A notebook client that retrieves notebook outputs from the cache,
    or executes the notebook and adds them to the cache, on entrance of the context.
    """

    def start_client(self):
        # setup the cache
        cache = get_cache(self.nb_config.execution_cache_path or ".jupyter_cache")
        # TODO config on what notebook/cell metadata to hash/merge

        # attempt to match the notebook to one in the cache
        cache_record = None
        with suppress(KeyError):
            cache_record = cache.match_cache_notebook(self.notebook)

        # use the cached notebook if it exists
        if cache_record is not None:
            self.logger.info(f"Using cached notebook: ID={cache_record.pk}")
            _, self._notebook = cache.merge_match_into_notebook(self.notebook)
            self.exec_metadata = {
                "mtime": cache_record.created.timestamp(),
                "runtime": cache_record.data.get("execution_seconds", None),
                "method": self.nb_config.execution_mode,
                "succeeded": True,
                "error": None,
                "traceback": None,
            }
            return

        if self.path is None:
            raise ValueError(
                "Input source must exist as file, if execution_mode is 'cache'"
            )

        # attempt to execute the notebook
        read_fmt = self._kwargs.get("read_fmt", None)
        if read_fmt is not None:
            stage_record = cache.add_nb_to_project(str(self.path), read_data=read_fmt)
        else:
            stage_record = cache.add_nb_to_project(str(self.path))
        # TODO do in try/except, in case of db write errors
        NbProjectRecord.remove_tracebacks([stage_record.pk], cache.db)
        cwd_context: ContextManager[str] = (
            TemporaryDirectory()  # type: ignore
            if self.nb_config.execution_in_temp
            else nullcontext(str(self.path.parent))
        )
        with cwd_context as cwd:
            cwd = os.path.abspath(cwd)
            self.logger.info(
                "Executing notebook using "
                + ("temporary" if self.nb_config.execution_in_temp else "local")
                + " CWD"
            )
            result = single_nb_execution(
                self.notebook,
                cwd=cwd,
                allow_errors=self.nb_config.execution_allow_errors,
                timeout=self.nb_config.execution_timeout,
                meta_override=True,  # TODO still support this?
            )

        # handle success / failure cases
        # TODO do in try/except to be careful (in case of database write errors?
        if result.err is not None:
            msg = f"Executing notebook failed: {result.err.__class__.__name__}"
            if self.nb_config.execution_show_tb:
                msg += f"\n{result.exc_string}"
            self.logger.warning(msg, subtype="exec")
            if self.nb_config.execution_raise_on_error:
                raise ExecutionError(str(self.path)) from result.err
            NbProjectRecord.set_traceback(stage_record.uri, result.exc_string, cache.db)
        else:
            self.logger.info(f"Executed notebook in {result.time:.2f} seconds")
            cache_record = cache.cache_notebook_bundle(
                CacheBundleIn(
                    self.notebook,
                    stage_record.uri,
                    data={"execution_seconds": result.time},
                ),
                check_validity=False,
                overwrite=True,
            )
            self.logger.info(f"Cached executed notebook: ID={cache_record.pk}")

        self.exec_metadata = {
            "mtime": datetime.now().timestamp(),
            "runtime": result.time,
            "method": self.nb_config.execution_mode,
            "succeeded": False if result.err else True,
            "error": f"{result.err.__class__.__name__}" if result.err else None,
            "traceback": result.exc_string if result.err else None,
        }
