"""This module defines the abstract interface of the cache.

API access to the cache should use this interface,
with no assumptions about the backend storage/retrieval mechanisms.
"""

from abc import ABC, abstractmethod
import io
from pathlib import Path
from typing import Iterable, List, Mapping, Optional, Tuple, Union

import attr
from attr.validators import instance_of, optional
import nbformat as nbf

# TODO make these abstract
from jupyter_cache.cache.db import NbCacheRecord, NbProjectRecord
from jupyter_cache.readers import DEFAULT_READ_DATA

NB_VERSION = 4


class CachingError(Exception):
    """An error to raise when adding to the cache fails."""


class RetrievalError(Exception):
    """An error to raise when retrieving from the cache fails."""


class NbValidityError(Exception):
    """Signals a notebook may not be valid to cache.

    For example, because it has not yet been executed.
    """

    def __init__(self, message, nb_bundle, *args, **kwargs):
        self.uri = nb_bundle.uri
        super().__init__(message, *args, **kwargs)


@attr.s(frozen=True, slots=True)
class ProjectNb:
    """A notebook read from a project"""

    pk: int = attr.ib(
        validator=instance_of(int),
        metadata={"help": "the ID of the notebook"},
    )
    uri: str = attr.ib(
        converter=str,
        validator=instance_of(str),
        metadata={"help": "the URI of the notebook"},
    )
    nb: nbf.NotebookNode = attr.ib(
        validator=instance_of(nbf.NotebookNode),
        repr=lambda nb: f"Notebook(cells={len(nb.cells)})",
        metadata={"help": "the notebook"},
    )
    assets: List[Path] = attr.ib(
        factory=list,
        metadata={"help": "File paths required to run the notebook"},
    )


class NbArtifactsAbstract(ABC):
    """Container for artefacts of a notebook execution."""

    @property
    @abstractmethod
    def relative_paths(self) -> List[Path]:
        """Return the list of paths (relative to the notebook folder)."""

    @abstractmethod
    def __iter__(self) -> Iterable[Tuple[Path, io.BufferedReader]]:
        """Yield the relative path and open files (in bytes mode)"""

    def __repr__(self):
        return f"{self.__class__.__name__}(paths={len(self.relative_paths)})"


@attr.s(frozen=True, slots=True)
class CacheBundleIn:
    """A container for notebooks and their associated data to cache."""

    nb: nbf.NotebookNode = attr.ib(
        validator=instance_of(nbf.NotebookNode),
        repr=lambda nb: f"Notebook(cells={len(nb.cells)})",
        metadata={"help": "the notebook"},
    )
    uri: str = attr.ib(
        converter=str,
        validator=instance_of(str),
        metadata={"help": "the origin URI of the notebook"},
    )
    artifacts: Optional[NbArtifactsAbstract] = attr.ib(
        kw_only=True,
        default=None,
        metadata={"help": "artifacts created during the notebook execution"},
    )
    data: dict = attr.ib(
        kw_only=True,
        factory=dict,
        validator=instance_of(dict),
        metadata={"help": "additional data related to the execution"},
    )
    traceback: Optional[str] = attr.ib(
        kw_only=True,
        default=None,
        validator=optional(instance_of(str)),
        metadata={"help": "the traceback, if the execution excepted"},
    )


@attr.s(frozen=True, slots=True)
class CacheBundleOut:
    """A container for notebooks and their associated data that have been cached."""

    nb: nbf.NotebookNode = attr.ib(
        validator=instance_of(nbf.NotebookNode),
        repr=lambda nb: f"Notebook(cells={len(nb.cells)})",
        metadata={"help": "the notebook"},
    )
    record: NbCacheRecord = attr.ib(metadata={"help": "the cache record"})
    artifacts: Optional[NbArtifactsAbstract] = attr.ib(
        default=None,
        metadata={"help": "artifacts created during the notebook execution"},
    )


class JupyterCacheAbstract(ABC):
    """An abstract cache for storing pre/post executed notebooks.

    Note: class instances should be pickleable.
    """

    @abstractmethod
    def get_version(self) -> Optional[str]:
        """Return the version of the cache."""

    @abstractmethod
    def clear_cache(self) -> None:
        """Clear the cache completely."""

    @abstractmethod
    def cache_notebook_bundle(
        self,
        bundle: CacheBundleIn,
        check_validity: bool = True,
        overwrite: bool = False,
    ) -> NbCacheRecord:
        """Commit an executed notebook, returning its cache record.

        Note: non-code source text (e.g. markdown) is not stored in the cache.

        :param bundle: The notebook bundle
        :param check_validity: check that the notebook has been executed correctly,
            by asserting `execution_count`s are consecutive and start at 1.
        :param overwrite: Allow overwrite of cache with matching hash
        :return: The primary key of the cache
        """

    @abstractmethod
    def cache_notebook_file(
        self,
        path: str,
        uri: Optional[str] = None,
        artifacts: List[str] = (),
        data: Optional[dict] = None,
        check_validity: bool = True,
        overwrite: bool = False,
    ) -> NbCacheRecord:
        """Commit an executed notebook, returning its cache record.

        Note: non-code source text (e.g. markdown) is not stored in the cache.

        :param path: path to the notebook
        :param uri: alternative URI to store in the cache record (defaults to path)
        :param artifacts: list of paths to outputs of the executed notebook.
            Artifacts must be in the same folder as the notebook (or a sub-folder)
        :param data: additional, JSONable, data about the cache
        :param check_validity: check that the notebook has been executed correctly,
            by asserting `execution_count`s are consecutive and start at 1.
        :param overwrite: Allow overwrite of cache with matching hash
        :return: The primary key of the cache
        """

    @abstractmethod
    def list_cache_records(self) -> List[NbCacheRecord]:
        """Return a list of cached notebook records."""

    @abstractmethod
    def get_cache_record(self, pk: int) -> NbCacheRecord:
        """Return the record of a cache, by its primary key"""

    @abstractmethod
    def get_cache_bundle(self, pk: int) -> CacheBundleOut:
        """Return an executed notebook bundle, by its primary key"""

    @abstractmethod
    def cache_artefacts_temppath(self, pk: int) -> Path:
        """Context manager to provide a temporary folder path to the notebook artifacts.

        Note this path is only guaranteed to exist within the scope of the context,
        and should only be used for read/copy operations::

            with cache.cache_artefacts_temppath(1) as path:
                shutil.copytree(path, destination)
        """

    @abstractmethod
    def match_cache_notebook(self, nb: nbf.NotebookNode) -> NbCacheRecord:
        """Match to an executed notebook, returning its primary key.

        :raises KeyError: if no match is found
        """

    def match_cache_file(self, path: str) -> NbCacheRecord:
        """Match to an executed notebook, returning its primary key.

        :raises KeyError: if no match is found
        """
        notebook = nbf.read(path, nbf.NO_CONVERT)
        return self.match_cache_notebook(notebook)

    @abstractmethod
    def merge_match_into_notebook(
        self,
        nb: nbf.NotebookNode,
        nb_meta=("kernelspec", "language_info", "widgets"),
        cell_meta=None,
    ) -> Tuple[int, nbf.NotebookNode]:
        """Match to an executed notebook and return a merged version

        :param nb: The input notebook
        :param nb_meta: metadata keys to merge from the cache (all if None)
        :param cell_meta: cell metadata keys to merge from the cache (all if None)
        :raises KeyError: if no match is found
        :return: pk, input notebook with cached code cells and metadata merged.
        """

    def merge_match_into_file(
        self,
        path: str,
        nb_meta=("kernelspec", "language_info", "widgets"),
        cell_meta=None,
    ) -> Tuple[int, nbf.NotebookNode]:
        """Match to an executed notebook and return a merged version

        :param path: The input notebook path
        :param nb_meta: metadata keys to merge from the cache (all if None)
        :param cell_meta: cell metadata keys to merge from the cache (all if None)
        :raises KeyError: if no match is found
        :return: pk, input notebook with cached code cells and metadata merged.
        """
        nb = nbf.read(str(path), nbf.NO_CONVERT)
        return self.merge_match_into_notebook(nb, nb_meta, cell_meta)

    @abstractmethod
    def diff_nbnode_with_cache(
        self, pk: int, nb: nbf.NotebookNode, uri: str = "", as_str=False, **kwargs
    ) -> Union[str, dict]:
        """Return a diff of a notebook to a cached one.

        Note: this will not diff markdown content, since it is not stored in the cache.
        """

    def diff_nbfile_with_cache(
        self, pk: int, path: str, as_str=False, **kwargs
    ) -> Union[str, dict]:
        """Return a diff of a notebook to a cached one.

        Note: this will not diff markdown content, since it is not stored in the cache.
        """
        nb = nbf.read(path, nbf.NO_CONVERT)
        return self.diff_nbnode_with_cache(pk, nb, uri=path, as_str=as_str, **kwargs)

    @abstractmethod
    def add_nb_to_project(
        self,
        uri: str,
        *,
        read_data: Mapping = DEFAULT_READ_DATA,
        assets: List[str] = (),
    ) -> NbProjectRecord:
        """Add a single notebook to the project.

        :param uri: The path to the file
        :param read_data: Data to generate a function, to read the uri and return a NotebookNode
        :param assets: The path of files required by the notebook to run.
        :raises ValueError: assets not within the same folder as the notebook URI.
        """

    @abstractmethod
    def remove_nb_from_project(self, uri_or_pk: Union[int, str]):
        """Remove a notebook from the project."""

    @abstractmethod
    def list_project_records(
        self,
        filter_uris: Optional[List[str]] = None,
        filter_pks: Optional[List[int]] = None,
    ) -> List[NbProjectRecord]:
        """Return a list of all notebook records in the project."""

    @abstractmethod
    def get_project_record(self, uri_or_pk: Union[int, str]) -> NbProjectRecord:
        """Return the record of a notebook in the project, by its primary key or URI."""

    @abstractmethod
    def get_project_notebook(self, uri_or_pk: Union[int, str]) -> ProjectNb:
        """Return a single notebook in the project, by its primary key or URI.

        :raises NbReadError: if the notebook cannot be read
        """

    @abstractmethod
    def get_cached_project_nb(
        self, uri_or_pk: Union[int, str]
    ) -> Optional[NbCacheRecord]:
        """Get cache record for a notebook in the project.

        :param uri_or_pk: The URI of pk of the file in the project
        """

    @abstractmethod
    def list_unexecuted(
        self,
        filter_uris: Optional[List[str]] = None,
        filter_pks: Optional[List[int]] = None,
    ) -> List[NbProjectRecord]:
        """List notebooks in the project, whose hash is not present in the cache."""
