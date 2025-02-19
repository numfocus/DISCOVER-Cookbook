import logging
import os

import click

from jupyter_cache.entry_points import ENTRY_POINT_GROUP_EXEC, list_group_names
from jupyter_cache.readers import list_readers


def callback_autocomplete(ctx, param, value):
    if value and not ctx.resilient_parsing:
        click.echo("Execute this in the terminal for auto-completion:")
        click.echo('eval "$(_JCACHE_COMPLETE=source jcache)"')
        ctx.exit()


AUTOCOMPLETE = click.option(
    "-a",
    "--autocomplete",
    help="Print the autocompletion command and exit.",
    is_flag=True,
    expose_value=True,
    is_eager=True,
    callback=callback_autocomplete,
)


def default_cache_path():
    return os.environ.get("JUPYTERCACHE", os.path.join(os.getcwd(), ".jupyter_cache"))


def callback_print_cache_path(ctx, param, value):
    if value and not ctx.resilient_parsing:
        click.secho("Cache path: ", fg="green", nl=False)
        click.echo(default_cache_path())
        ctx.exit()


PRINT_CACHE_PATH = click.option(
    "-p",
    "--print-path",
    help="Print the current cache path and exit.",
    is_flag=True,
    expose_value=True,
    is_eager=True,
    callback=callback_print_cache_path,
)


CACHE_PATH = click.option(
    "-p",
    "--cache-path",
    help="Path to project cache.",
    default=default_cache_path,
    show_default=".jupyter_cache",
)


NB_PATH = click.option(
    "-nb",
    "--nbpath",
    required=True,
    help="The notebooks path.",
    type=click.Path(dir_okay=False, exists=True, readable=True, resolve_path=True),
)

READER_KEY = click.option(
    "-r",
    "--reader",
    help="The notebook reader to use.",
    default="nbformat",
    type=click.Choice(list_readers()),
    show_default=True,
)


EXECUTOR_KEY = click.option(
    "-e",
    "--executor",
    help="The executor to use.",
    default="local-serial",
    type=click.Choice(list_group_names(ENTRY_POINT_GROUP_EXEC)),
    show_default=True,
)

EXEC_TIMEOUT = click.option(
    "-t",
    "--timeout",
    help="Execution timeout value in seconds.",
    default=30,
    show_default=True,
)


def EXEC_FORCE(default=False):
    return click.option(
        "-f",
        "--force/--no-force",
        help="Execute a notebook even if it is cached.",
        is_flag=True,
        default=default,
        show_default=True,
    )


PATH_LENGTH = click.option(
    "-l", "--path-length", default=3, show_default=True, help="Maximum URI path."
)


VALIDATE_NB = click.option(
    "--validate/--no-validate",
    default=True,
    show_default=True,
    help="Whether to validate that a notebook has been executed.",
)


OVERWRITE_CACHED = click.option(
    "--overwrite/--no-overwrite",
    default=True,
    show_default=True,
    help="Whether to overwrite an existing notebook with the same hash.",
)

FORCE = click.option(
    "-f", "--force", default=False, is_flag=True, help="Do not ask for confirmation."
)


def confirm_remove_all(ctx, param, remove_all):
    if remove_all and not click.confirm("Are you sure you want to remove all?"):
        click.secho("Aborted!", bold=True, fg="red")
        ctx.exit()
    return remove_all


REMOVE_ALL = click.option(
    "-a",
    "--all",
    "remove_all",
    is_flag=True,
    help="Remove all notebooks.",
    callback=confirm_remove_all,
)


def confirm_invalidate_all(ctx, param, remove_all):
    if remove_all and not click.confirm("Are you sure you want to invalidate all?"):
        click.secho("Aborted!", bold=True, fg="red")
        ctx.exit()
    return remove_all


INVALIDATE_ALL = click.option(
    "-a",
    "--all",
    "invalidate_all",
    is_flag=True,
    help="Invalidate all notebooks.",
    callback=confirm_invalidate_all,
)


def set_log_level(logger):
    """Set the log level of the logger."""

    def _callback(ctx, param, value):
        """Set logging level."""
        level = getattr(logging, value.upper(), None)
        if level is None:
            raise click.BadParameter(f"Unknown log level: {value.upper()}")
        logger.setLevel(level)

    return click.option(
        "-v",
        "--verbosity",
        type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
        default="INFO",
        show_default=True,
        expose_value=False,
        callback=_callback,
        help="Set logging verbosity.",
    )
