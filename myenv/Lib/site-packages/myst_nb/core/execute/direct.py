"""Execute a notebook directly."""
from __future__ import annotations

from contextlib import nullcontext
from datetime import datetime
import os
from tempfile import TemporaryDirectory
from typing import ContextManager

from jupyter_cache.executors.utils import single_nb_execution

from .base import ExecutionError, NotebookClientBase


class NotebookClientDirect(NotebookClientBase):
    """A notebook client that executes the notebook directly,
    on entrance of the context.
    """

    def start_client(self):
        # setup the execution current working directory
        cwd_context: ContextManager[str]
        if self.nb_config.execution_in_temp:
            cwd_context = TemporaryDirectory()
        else:
            if self.path is None:
                raise ValueError(
                    "Input source must exist as file, if execution_in_temp=False"
                )
            cwd_context = nullcontext(str(self.path.parent))

        # execute in the context of the current working directory
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

        if result.err is not None:
            if self.nb_config.execution_raise_on_error:
                raise ExecutionError(str(self.path)) from result.err
            msg = f"Executing notebook failed: {result.err.__class__.__name__}"
            if self.nb_config.execution_show_tb:
                msg += f"\n{result.exc_string}"
            self.logger.warning(msg, subtype="exec")
        else:
            self.logger.info(f"Executed notebook in {result.time:.2f} seconds")

        self.exec_metadata = {
            "mtime": datetime.now().timestamp(),
            "runtime": result.time,
            "method": self.nb_config.execution_mode,
            "succeeded": False if result.err else True,
            "error": f"{result.err.__class__.__name__}" if result.err else None,
            "traceback": result.exc_string if result.err else None,
        }
