"""The main `jcache` click group."""

import click

from jupyter_cache.cli import options


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(
    None, "-v", "--version", message="jupyter-cache version %(version)s"
)
@options.PRINT_CACHE_PATH
@options.AUTOCOMPLETE
def jcache(*args, **kwargs):
    """The command line interface of jupyter-cache."""
