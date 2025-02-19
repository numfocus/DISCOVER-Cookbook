import logging

import click

from jupyter_cache.cli import options, pass_cache, utils
from jupyter_cache.cli.commands.cmd_main import jcache

logger = logging.getLogger(__name__)
utils.setup_logger(logger)


@jcache.group("project")
@options.CACHE_PATH
@pass_cache
def cmnd_project(cache, cache_path):
    """Work with a project."""
    cache.set_cache_path(cache_path)


@cmnd_project.command("version")
@pass_cache
def version(cache):
    """Print the version of the cache."""
    if not cache.cache_path.exists():
        click.secho("No cache found.", fg="red")
        raise click.Abort()
    version = cache.get_cache().get_version()
    if version is None:
        click.secho("Cache version not found", fg="red")
        raise click.Abort()
    click.echo(version)


@cmnd_project.command("clear")
@options.FORCE
@pass_cache
def clear_cache(cache, force):
    """Clear the project cache completely."""
    if not cache.cache_path.exists():
        click.secho("Cache does not exist", fg="green")
        raise click.Abort()
    if not force:
        click.echo(f"Cache path: {cache.cache_path}")
        click.confirm(
            "Are you sure you want to permanently clear the cache!?",
            abort=True,
        )
    cache.get_cache().clear_cache()
    click.secho("Cache cleared!", fg="green")


@cmnd_project.command("cache-limit")
@click.argument("limit", metavar="CACHE_LIMIT", type=int, required=False)
@pass_cache
def change_cache_limit(cache, limit):
    """Get/set maximum number of notebooks stored in the cache."""
    db = cache.get_cache()
    if limit is None:
        limit = db.get_cache_limit()
        click.echo(f"Current cache limit: {limit}")
    else:
        db.change_cache_limit(limit)
        click.secho("Cache limit changed!", fg="green")


@cmnd_project.command("execute")
@options.EXECUTOR_KEY
@options.EXEC_TIMEOUT
@options.EXEC_FORCE(default=False)
@options.set_log_level(logger)
@pass_cache
def execute_nbs(cache, executor, timeout, force):
    """Execute all outdated notebooks in the project."""
    import yaml

    from jupyter_cache.executors import load_executor

    db = cache.get_cache()
    try:
        executor = load_executor(executor, db, logger=logger)
    except ImportError as error:
        logger.error(str(error))
        return 1
    result = executor.run_and_cache(timeout=timeout, force=force)
    click.secho(
        "Finished! Successfully executed notebooks have been cached.", fg="green"
    )
    click.echo(yaml.safe_dump(result.as_json(), sort_keys=False))
