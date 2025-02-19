"""Defines the `SiteMap` object, for storing the parsed ToC."""
from collections.abc import MutableMapping
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterator, List, Optional, Set, Union

from ._compat import (
    DC_SLOTS,
    deep_iterable,
    field,
    instance_of,
    matches_re,
    optional,
    validate_fields,
)

#: Pattern used to match URL items.
URL_PATTERN: str = r".+://.*"


class FileItem(str):
    """A document path in a toctree list.

    This should be in POSIX format (folders split by ``/``), relative to the
    source directory, and can be with or without an extension.
    """


class GlobItem(str):
    """A document glob in a toctree list."""


@dataclass(**DC_SLOTS)
class UrlItem:
    """A URL in a toctree."""

    # regex should match sphinx.util.url_re
    url: str = field(validator=[instance_of(str), matches_re(URL_PATTERN)])
    title: Optional[str] = field(default=None, validator=optional(instance_of(str)))

    def __post_init__(self):
        validate_fields(self)


@dataclass(**DC_SLOTS)
class TocTree:
    """An individual toctree within a document."""

    # TODO validate uniqueness of docnames (at least one item)
    items: List[Union[GlobItem, FileItem, UrlItem]] = field(
        validator=deep_iterable(
            instance_of((GlobItem, FileItem, UrlItem)), instance_of(list)
        )
    )
    caption: Optional[str] = field(
        default=None, kw_only=True, validator=optional(instance_of(str))
    )
    hidden: bool = field(default=True, kw_only=True, validator=instance_of(bool))
    maxdepth: int = field(default=-1, kw_only=True, validator=instance_of(int))
    numbered: Union[bool, int] = field(
        default=False, kw_only=True, validator=instance_of((bool, int))
    )
    reversed: bool = field(default=False, kw_only=True, validator=instance_of(bool))
    titlesonly: bool = field(default=False, kw_only=True, validator=instance_of(bool))

    def __post_init__(self):
        validate_fields(self)

    def files(self) -> List[str]:
        """Returns a list of file items included in this ToC tree.

        :return: file items
        """
        return [str(item) for item in self.items if isinstance(item, FileItem)]

    def globs(self) -> List[str]:
        """Returns a list of glob items included in this ToC tree.

        :return: glob items
        """
        return [str(item) for item in self.items if isinstance(item, GlobItem)]


@dataclass(**DC_SLOTS)
class Document:
    """A document in the site map."""

    # TODO validate uniqueness of docnames across all parts (and none should be the docname)
    docname: str = field(validator=instance_of(str))
    subtrees: List[TocTree] = field(
        default_factory=list,
        validator=deep_iterable(instance_of(TocTree), instance_of(list)),
    )
    title: Optional[str] = field(default=None, validator=optional(instance_of(str)))

    def __post_init__(self):
        validate_fields(self)

    def child_files(self) -> List[str]:
        """Return all children files.

        :return: child files
        """
        return [name for tree in self.subtrees for name in tree.files()]

    def child_globs(self) -> List[str]:
        """Return all children globs.

        :return: child globs
        """
        return [name for tree in self.subtrees for name in tree.globs()]


class SiteMap(MutableMapping):
    """A mapping of documents to their toctrees (or None if terminal)."""

    def __init__(
        self,
        root: Document,
        meta: Optional[Dict[str, Any]] = None,
        file_format: Optional[str] = None,
    ) -> None:
        self._docs: Dict[str, Document] = {}
        self[root.docname] = root
        self._root: Document = root
        self._meta: Dict[str, Any] = meta or {}
        self._file_format = file_format

    @property
    def root(self) -> Document:
        """Return the root document of the ToC tree.

        :return: root document
        """
        return self._root

    @property
    def meta(self) -> Dict[str, Any]:
        """Return the site-map metadata.

        :return: metadata dictionary
        """
        return self._meta

    @property
    def file_format(self) -> Optional[str]:
        """Return the format of the file to write to.

        :return: output file format
        """
        return self._file_format

    @file_format.setter
    def file_format(self, value: Optional[str]) -> None:
        """Set the format of the file to write to."""
        self._file_format = value

    def globs(self) -> Set[str]:
        """Return set of all globs present across all toctrees."""
        return {glob for item in self._docs.values() for glob in item.child_globs()}

    def __getitem__(self, docname: str) -> Document:
        """Enable retrieving a document by name using the indexing operator.

        :param docname: document name
        :return: document instance
        """
        return self._docs[docname]

    def __setitem__(self, docname: str, item: Document) -> None:
        """Enable setting a document by name using the indexing operator.

        :param docname: document name
        :param item: document instance
        """
        assert item.docname == docname
        self._docs[docname] = item

    def __delitem__(self, docname: str) -> None:
        """Enable removing a document by name.

        :param docname: document name
        """
        assert docname != self._root.docname, "cannot delete root doc item"
        del self._docs[docname]

    def __iter__(self) -> Iterator[str]:
        """Enable iterating the names of the documents the site map is composed
        of.

        :yield: document name
        """
        for docname in self._docs:
            yield docname

    def __len__(self) -> int:
        """Enable using Python's built-in `len()` function to return the number
        of documents contained in a site map.

        :return: number of documents in this site map
        """
        return len(self._docs)

    def as_json(self) -> Dict[str, Any]:
        """Return JSON serialized site-map representation."""
        doc_dict = {
            k: asdict(self._docs[k]) if self._docs[k] else self._docs[k]
            for k in sorted(self._docs)
        }

        def _replace_items(d: Dict[str, Any]) -> Dict[str, Any]:
            for k, v in d.items():
                if isinstance(v, dict):
                    d[k] = _replace_items(v)
                elif isinstance(v, (list, tuple)):
                    d[k] = [
                        _replace_items(i)
                        if isinstance(i, dict)
                        else (str(i) if isinstance(i, str) else i)
                        for i in v
                    ]
                elif isinstance(v, str):
                    d[k] = str(v)
            return d

        doc_dict = _replace_items(doc_dict)
        data = {
            "root": self.root.docname,
            "documents": doc_dict,
            "meta": self.meta,
        }
        if self.file_format:
            data["file_format"] = self.file_format
        return data

    def get_changed(self, previous: "SiteMap") -> Set[str]:
        """Compare this sitemap to another and return a list of changed documents.

        .. note:: for Sphinx, file extensions should be removed to get docnames.
        """
        changed_docs = set()
        # check if the root document has changed
        if self.root != previous.root:
            changed_docs.add(self.root.docname)
        for name, doc in self._docs.items():
            if name not in previous:
                changed_docs.add(name)
                continue
            prev_doc = previous[name]
            if prev_doc != doc:
                changed_docs.add(name)
        return changed_docs
