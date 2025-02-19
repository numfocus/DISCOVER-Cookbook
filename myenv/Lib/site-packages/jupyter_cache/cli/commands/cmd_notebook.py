import logging
import os

import click
import nbformat

from jupyter_cache.cli import arguments, options, pass_cache, utils
from jupyter_cache.cli.commands.cmd_main import jcache
from jupyter_cache.readers import NbReadError
from jupyter_cache.utils import tabulate_project_records

logger = logging.getLogger(__name__)
utils.setup_logger(logger)


@jcache.group("notebook")
@options.CACHE_PATH
@pass_cache
def cmnd_notebook(cache, cache_path):
    """Work with notebook(s) in a project."""
    cache.set_cache_path(cache_path)


@cmnd_notebook.command("add")
@arguments.NB_PATHS
@options.READER_KEY
@pass_cache
def add_notebooks(cache, nbpaths, reader):
    """Add notebook(s) to the project."""
    db = cache.get_cache()
    for path in nbpaths:
        # TODO deal with errors (print all at end? or option to ignore)
        click.echo(f"Adding: {path}")
        db.add_nb_to_project(path, read_data={"name": reader, "type": "plugin"})
    click.secho("Success!", fg="green")


@cmnd_notebook.command("add-with-assets")
@arguments.ASSET_PATHS
@options.NB_PATH
@options.READER_KEY
@pass_cache
def add_notebook(cache, nbpath, reader, asset_paths):
    """Add notebook(s) to the project, with possible asset files."""
    db = cache.get_cache()
    db.add_nb_to_project(
        nbpath, read_data={"name": reader, "type": "plugin"}, assets=asset_paths
    )
    click.secho("Success!", fg="green")


@cmnd_notebook.command("clear")
@options.FORCE
@pass_cache
def clear_nbs(cache, force):
    """Remove all notebooks from the project."""
    db = cache.get_cache()
    if not force:
        click.confirm(
            "Are you sure you want to permanently clear the project!?", abort=True
        )
    for record in db.list_project_records():
        db.remove_nb_from_project(record.pk)
    click.secho("Project cleared!", fg="green")


@cmnd_notebook.command("remove")
@arguments.PK_OR_PATHS
@pass_cache
def remove_nbs(cache, pk_paths):
    """Remove notebook(s) from the project (by ID/URI)."""
    db = cache.get_cache()
    for pk_path in pk_paths:
        # TODO deal with errors (print all at end? or option to ignore)
        click.echo(f"Removing: {pk_path}")
        db.remove_nb_from_project(
            int(pk_path) if pk_path.isdigit() else os.path.abspath(pk_path)
        )
    click.secho("Success!", fg="green")


@cmnd_notebook.command("invalidate")
@arguments.PK_OR_PATHS
@options.INVALIDATE_ALL
@pass_cache
def invalidate_nbs(cache, pk_paths, invalidate_all):
    """Remove any matching cache of the notebook(s) (by ID/URI)."""
    db = cache.get_cache()
    if invalidate_all:
        pk_paths = [str(record.pk) for record in db.list_project_records()]
    for pk_path in pk_paths:
        # TODO deal with errors (print all at end? or option to ignore)
        click.echo(f"Invalidating: {pk_path}")
        record = db.get_cached_project_nb(
            int(pk_path) if pk_path.isdigit() else os.path.abspath(pk_path)
        )
        if record is not None:
            db.remove_cache(record.pk)
    click.secho("Success!", fg="green")


@cmnd_notebook.command("list")
# @click.option(
#     "--compare/--no-compare",
#     default=True,
#     show_default=True,
#     help="Compare to cached notebooks (to find cache ID).",
# )
@options.PATH_LENGTH
@click.option(
    "--assets",
    is_flag=True,
    help="Show the number of assets associated with each notebook",
)
@pass_cache
def list_nbs_in_project(cache, path_length, assets):
    """List notebooks in the project."""
    db = cache.get_cache()
    records = db.list_project_records()
    if not records:
        click.secho("No notebooks in project", fg="blue")
    click.echo(
        tabulate_project_records(
            records, path_length=path_length, cache=db, assets=assets
        )
    )


@cmnd_notebook.command("info")
@arguments.PK_OR_PATH
@click.option(
    "--tb/--no-tb",
    default=True,
    show_default=True,
    help="Show traceback, if last execution failed.",
)
@pass_cache
def show_project_record(cache, pk_path, tb):
    """Show details of a notebook (by ID)."""
    import yaml

    db = cache.get_cache()
    try:
        record = db.get_project_record(
            int(pk_path) if pk_path.isdigit() else os.path.abspath(pk_path)
        )
    except KeyError:
        click.secho(f"ID {pk_path} does not exist, Aborting!", fg="red")
        raise click.Abort()
    cache_record = None
    try:
        cache_record = db.get_cached_project_nb(record.uri)
    except NbReadError as exc:
        click.secho(f"File could not be read: {exc}", fg="red")
    data = record.format_dict(
        cache_record=cache_record, path_length=None, assets=False, read_name=False
    )
    click.echo(yaml.safe_dump(data, sort_keys=False, allow_unicode=True).rstrip())
    if record.assets:
        click.echo("Assets:")
        for path in record.assets:
            click.echo(f"- {path}")
    if record.traceback:
        click.secho("Failed Last Execution!", fg="red")
        if tb:
            click.echo(record.traceback)


@cmnd_notebook.command("merge")
@arguments.PK_OR_PATH
@arguments.OUTPUT_PATH
@pass_cache
def merge_executed(cache, pk_path, outpath):
    """Create notebook merged with cached outputs (by ID/URI)."""
    db = cache.get_cache()
    nb = db.get_project_notebook(
        int(pk_path) if pk_path.isdigit() else os.path.abspath(pk_path)
    ).nb
    cached_pk, nb = db.merge_match_into_notebook(nb)
    nbformat.write(nb, outpath)
    click.echo(f"Merged with cache PK {cached_pk}")
    click.secho("Success!", fg="green")


@cmnd_notebook.command("execute")
@arguments.PK_OR_PATHS
@options.EXECUTOR_KEY
@options.EXEC_TIMEOUT
@options.EXEC_FORCE(default=True)
@options.set_log_level(logger)
@pass_cache
def execute_nbs(cache, pk_paths, executor, timeout, force):
    """Execute specific notebooks in the project."""
    import yaml

    from jupyter_cache.executors import load_executor

    uris = [os.path.abspath(p) for p in pk_paths if not p.isdigit()] or None
    pks = [int(p) for p in pk_paths if p.isdigit()] or None

    db = cache.get_cache()

    try:
        executor = load_executor(executor, db, logger=logger)
    except ImportError as error:
        logger.error(str(error))
        return 1
    result = executor.run_and_cache(
        filter_pks=pks, filter_uris=uris, timeout=timeout, force=force
    )
    click.secho(
        "Finished! Successfully executed notebooks have been cached.", fg="green"
    )
    click.echo(yaml.safe_dump(result.as_json(), sort_keys=False))
