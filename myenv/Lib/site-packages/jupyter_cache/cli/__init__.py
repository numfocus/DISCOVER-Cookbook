import os
from pathlib import Path
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from jupyter_cache.base import JupyterCacheAbstract


class CacheContext:
    """Context for retrieving the cache."""

    def __init__(self, cache_path=None) -> None:
        if cache_path is None:
            self._cache_path = os.environ.get(
                "JUPYTERCACHE", os.path.join(os.getcwd(), ".jupyter_cache")
            )
        else:
            self._cache_path = cache_path

    @property
    def cache_path(self) -> Path:
        return Path(self._cache_path)

    def get_cache(self, ask_on_missing=True) -> "JupyterCacheAbstract":
        """Get the cache."""
        from jupyter_cache import get_cache

        if (not self.cache_path.exists()) and ask_on_missing:
            click.secho("Cache path: ", fg="green", nl=False)
            click.echo(str(self.cache_path))
            if not click.confirm(
                "The cache does not yet exist, do you want to create it?"
            ):
                raise click.Abort()

        # gets created lazily
        return get_cache(self.cache_path)

    def set_cache_path(self, cache_path: str) -> None:
        self._cache_path = cache_path


pass_cache = click.make_pass_decorator(CacheContext, ensure=True)
