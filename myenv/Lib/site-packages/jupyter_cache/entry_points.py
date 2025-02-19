"""Module for dealing with entry points."""

from typing import Optional, Set

# TODO importlib.metadata was introduced into the standard library in python 3.8
# so we can change this when we drop support for 3.7
# also, from importlib_metadata changed its API in v4.0, to use the python 3.10 API
# however, because of https://github.com/python/importlib_metadata/issues/308
# we do not assume that we have this API, and instead use try/except for the new/old APIs
from importlib_metadata import EntryPoint
from importlib_metadata import entry_points as eps

ENTRY_POINT_GROUP_READER = "jcache.readers"
ENTRY_POINT_GROUP_EXEC = "jcache.executors"


def list_group_names(group: str) -> Set[str]:
    """Return the entry points within a group."""
    all_eps = eps()
    try:
        # importlib_metadata v4 / python 3.10
        return all_eps.select(group=group).names
    except (AttributeError, TypeError):
        return {ep.name for ep in all_eps.get(group, [])}


def get_entry_point(group: str, name: str) -> Optional[EntryPoint]:
    """Return the entry point with the given name in the given group."""
    all_eps = eps()
    try:
        # importlib_metadata v4 / python 3.10
        found = all_eps.select(group=group, name=name)
        ep = found[name] if name in found.names else None
    except (AttributeError, TypeError):
        found = {ep.name: ep for ep in all_eps.get(group, [])}
        ep = found[name] if name in found else None
    return ep
