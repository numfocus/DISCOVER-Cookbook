import click

from jupyter_cache.cli import arguments, options, pass_cache
from jupyter_cache.cli.commands.cmd_main import jcache
from jupyter_cache.utils import tabulate_cache_records


@jcache.group("cache")
@options.CACHE_PATH
@pass_cache
def cmnd_cache(cache, cache_path):
    """Work with cached execution(s) in a project."""
    cache.set_cache_path(cache_path)


@cmnd_cache.command("list")
@click.option(
    "-l",
    "--latest-only",
    is_flag=True,
    help="Show only the most recent record per origin URI.",
)
@click.option("-h", "--hashkeys", is_flag=True, help="Show the hashkey of notebook.")
@options.PATH_LENGTH
@pass_cache
def list_caches(cache, latest_only, hashkeys, path_length):
    """List cached notebook records."""
    db = cache.get_cache()
    records = db.list_cache_records()
    if not records:
        click.secho("No Cached Notebooks", fg="blue")
    # TODO optionally list number of artifacts
    if latest_only:
        latest_records = {}
        for record in records:
            if record.uri not in latest_records:
                latest_records[record.uri] = record
                continue
            if latest_records[record.uri].created < record.created:
                latest_records[record.uri] = record
        records = list(latest_records.values())
    click.echo(
        tabulate_cache_records(records, hashkeys=hashkeys, path_length=path_length)
    )


@cmnd_cache.command("info")
@arguments.PK
@pass_cache
def cached_info(cache, pk):
    """Show details of a cached notebook."""
    import yaml

    db = cache.get_cache()
    try:
        record = db.get_cache_record(pk)
    except KeyError:
        click.secho(f"ID {pk} does not exist, Aborting!", fg="red")
        raise click.Abort()
    data = record.format_dict(hashkey=True, path_length=None)
    click.echo(yaml.safe_dump(data, sort_keys=False), nl=False)
    with db.cache_artefacts_temppath(pk) as folder:
        paths = [str(p.relative_to(folder)) for p in folder.glob("**/*") if p.is_file()]
    if not paths:
        click.echo("")
        return
    if paths:
        click.echo("Artifacts:")
        for path in paths:
            click.echo(f"- {path}")


@cmnd_cache.command("cat-artefact")
@arguments.PK
@arguments.ARTIFACT_RPATH
@pass_cache
def cat_artifact(cache, pk, artifact_rpath):
    """Print the contents of a cached artefact."""
    db = cache.get_cache()
    with db.cache_artefacts_temppath(pk) as path:
        artifact_path = path.joinpath(artifact_rpath)
        if not artifact_path.exists():
            click.secho("Artifact does not exist", fg="red")
            raise click.Abort()
        if not artifact_path.is_file():
            click.secho("Artifact is not a file", fg="red")
            raise click.Abort()
        text = artifact_path.read_text(encoding="utf8")
    click.echo(text)


def cache_file(db, nbpath, validate, overwrite, artifact_paths=()):
    from jupyter_cache.base import NbValidityError

    click.echo(f"Caching: {nbpath}")
    try:
        db.cache_notebook_file(
            nbpath,
            artifacts=artifact_paths,
            check_validity=validate,
            overwrite=overwrite,
        )
    except NbValidityError as error:
        click.secho("Validity Error: ", fg="red", nl=False)
        click.echo(str(error))
        if click.confirm("The notebook may not have been executed, continue caching?"):
            try:
                db.cache_notebook_file(
                    nbpath,
                    artifacts=artifact_paths,
                    check_validity=False,
                    overwrite=overwrite,
                )
            except OSError as error:
                click.secho("Artifact Error: ", fg="red", nl=False)
                click.echo(str(error))
                return False
    except OSError as error:
        click.secho("Artifact Error: ", fg="red", nl=False)
        click.echo(str(error))
        return False
    return True


@cmnd_cache.command("add-with-artefacts")
@arguments.ARTIFACT_PATHS
@options.NB_PATH
@options.VALIDATE_NB
@options.OVERWRITE_CACHED
@pass_cache
def cache_nb(cache, artifact_paths, nbpath, validate, overwrite):
    """Cache a notebook, with possible artefact files."""
    db = cache.get_cache()
    success = cache_file(db, nbpath, validate, overwrite, artifact_paths)
    if success:
        click.secho("Success!", fg="green")


@cmnd_cache.command("add")
@arguments.NB_PATHS
@options.VALIDATE_NB
@options.OVERWRITE_CACHED
@pass_cache
def cache_nbs(cache, nbpaths, validate, overwrite):
    """Cache notebook(s) that have already been executed."""
    db = cache.get_cache()
    success = True
    for nbpath in nbpaths:
        # TODO deal with errors (print all at end? or option to ignore)
        if not cache_file(db, nbpath, validate, overwrite):
            success = False
    if success:
        click.secho("Success!", fg="green")


@cmnd_cache.command("clear")
@options.FORCE
@pass_cache
def clear_cache_cmd(cache, force):
    """Remove all executed notebooks from the cache."""
    db = cache.get_cache()
    if not force:
        click.confirm(
            "Are you sure you want to permanently clear the cache!?", abort=True
        )
    for record in db.list_cache_records():
        db.remove_cache(record.pk)
    click.secho("Cache cleared!", fg="green")


@cmnd_cache.command("remove")
@arguments.PKS
@options.REMOVE_ALL
@pass_cache
def remove_caches(cache, pks, remove_all):
    """Remove notebooks stored in the cache."""
    from jupyter_cache.base import CachingError

    db = cache.get_cache()
    if remove_all:
        pks = [r.pk for r in db.list_cache_records()]
    for pk in pks:
        # TODO deal with errors (print all at end? or option to ignore)
        click.echo(f"Removing Cache ID = {pk}")
        try:
            db.remove_cache(pk)
        except KeyError:
            click.secho("Does not exist", fg="red")
        except CachingError as err:
            click.secho("Error: ", fg="red")
            click.echo(str(err))
    click.secho("Success!", fg="green")


@cmnd_cache.command("diff")
@arguments.PK
@arguments.NB_PATH
@pass_cache
def diff_nb(cache, pk, nbpath):
    """Print a diff of a notebook to one stored in the cache."""
    db = cache.get_cache()
    click.echo(db.diff_nbfile_with_cache(pk, nbpath, as_str=True))
    click.secho("Success!", fg="green")
