"""Parse the ToC to a `SiteMap` object."""
from collections.abc import Mapping
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union

import yaml

from ._compat import DC_SLOTS, field
from .api import Document, FileItem, GlobItem, SiteMap, TocTree, UrlItem

DEFAULT_SUBTREES_KEY = "subtrees"
DEFAULT_ITEMS_KEY = "entries"
FILE_FORMAT_KEY = "format"
ROOT_KEY = "root"
FILE_KEY = "file"
GLOB_KEY = "glob"
URL_KEY = "url"
TOCTREE_OPTIONS = (
    "caption",
    "hidden",
    "maxdepth",
    "numbered",
    "reversed",
    "titlesonly",
)


@dataclass(**DC_SLOTS)
class FileFormat:
    """Mapping of keys for subtrees and items, dependant on depth in the ToC."""

    toc_defaults: Dict[str, Any] = field(default_factory=dict)
    subtrees_keys: Sequence[str] = ()
    items_keys: Sequence[str] = ()
    default_subtrees_key: str = DEFAULT_SUBTREES_KEY
    default_items_key: str = DEFAULT_ITEMS_KEY

    def get_subtrees_key(self, depth: int) -> str:
        """Get the subtrees key name for this depth in the ToC.

        :param depth: recursive depth (starts at 0)
        :return: subtrees key name
        """
        try:
            return self.subtrees_keys[depth]
        except IndexError:
            return self.default_subtrees_key

    def get_items_key(self, depth: int) -> str:
        """Get the items key name for this depth in the ToC.

        :param depth: recursive depth (starts at 0)
        :return: items key name
        """
        try:
            return self.items_keys[depth]
        except IndexError:
            return self.default_items_key


FILE_FORMATS: Dict[str, FileFormat] = {
    "default": FileFormat(),
    "jb-book": FileFormat(
        subtrees_keys=("parts",),
        items_keys=("chapters",),
        default_items_key="sections",
        toc_defaults={"titlesonly": True},
    ),
    "jb-article": FileFormat(
        default_items_key="sections",
        toc_defaults={"titlesonly": True},
    ),
}


class MalformedError(Exception):
    """Raised if the `_toc.yml` file is malformed."""


def parse_toc_yaml(path: Union[str, Path], encoding: str = "utf8") -> SiteMap:
    """Parse the ToC file.

    :param path: `_toc.yml` file path
    :param encoding: `_toc.yml` file character encoding
    :return: parsed site map
    """
    with Path(path).open(encoding=encoding) as handle:
        data = yaml.safe_load(handle)
    return parse_toc_data(data)


def parse_toc_data(data: Dict[str, Any]) -> SiteMap:
    """Parse a dictionary of the ToC.

    :param data: ToC data dictionary
    :return: parsed site map
    """
    if not isinstance(data, Mapping):
        raise MalformedError(f"toc is not a mapping: {type(data)}")

    try:
        file_format = FILE_FORMATS[data.get(FILE_FORMAT_KEY, "default")]
    except KeyError:
        raise MalformedError(
            f"'{FILE_FORMAT_KEY}' key value not recognised: "
            f"'{data.get(FILE_FORMAT_KEY, 'default')}'"
        )

    defaults: Dict[str, Any] = {
        **file_format.toc_defaults,
        **data.get("defaults", {}),
    }

    doc_item, docs_list = _parse_doc_item(
        data, defaults, "/", depth=0, is_root=True, file_format=file_format
    )

    site_map = SiteMap(
        root=doc_item,
        meta=data.get("meta"),
        file_format=data.get(FILE_FORMAT_KEY),
    )

    _parse_docs_list(docs_list, site_map, defaults, depth=1, file_format=file_format)

    return site_map


def _parse_doc_item(
    data: Dict[str, Any],
    defaults: Dict[str, Any],
    path: str,
    *,
    depth: int,
    file_format: FileFormat,
    is_root: bool = False,
) -> Tuple[Document, Sequence[Tuple[str, Dict[str, Any]]]]:
    """Parse a single doc item.

    :param data: doc item dictionary
    :param defaults: doc item defaults dictionary
    :param path: doc item file path
    :param depth: recursive depth (starts at 0)
    :param file_format: doc item file format
    :param is_root: whether this is the root item, defaults to False
    :raises MalformedError: invalid doc item
    :return: parsed doc item
    """
    file_key = ROOT_KEY if is_root else FILE_KEY
    if file_key not in data:
        raise MalformedError(f"'{file_key}' key not found @ '{path}'")

    subtrees_key = file_format.get_subtrees_key(depth)
    items_key = file_format.get_items_key(depth)

    # check no unknown keys present
    allowed_keys = {
        file_key,
        "title",
        "options",
        subtrees_key,
        items_key,
        # top-level only
        FILE_FORMAT_KEY,
        "defaults",
        "meta",
    }
    if not allowed_keys.issuperset(data.keys()):
        unknown_keys = set(data.keys()).difference(allowed_keys)
        raise MalformedError(
            f"Unknown keys found: {unknown_keys!r}, allowed: {allowed_keys!r} @ '{path}'"
        )

    shorthand_used = False
    if items_key in data:
        # this is a shorthand for defining a single subtree
        if subtrees_key in data:
            raise MalformedError(
                f"Both '{subtrees_key}' and '{items_key}' found @ '{path}'"
            )
        subtrees_data = [{items_key: data[items_key], **data.get("options", {})}]
        shorthand_used = True
    elif subtrees_key in data:
        subtrees_data = data[subtrees_key]
        if not (isinstance(subtrees_data, Sequence) and subtrees_data):
            raise MalformedError(f"'{subtrees_key}' not a non-empty list @ '{path}'")
        path = f"{path}{subtrees_key}/"
    else:
        subtrees_data = []

    _known_link_keys = {FILE_KEY, GLOB_KEY, URL_KEY}

    toctrees = []
    for toc_idx, toc_data in enumerate(subtrees_data):
        toc_path = path if shorthand_used else f"{path}{toc_idx}/"

        if not (isinstance(toc_data, Mapping) and items_key in toc_data):
            raise MalformedError(
                f"entry not a mapping containing '{items_key}' key @ '{toc_path}'"
            )

        items_data = toc_data[items_key]

        if not (isinstance(items_data, Sequence) and items_data):
            raise MalformedError(f"'{items_key}' not a non-empty list @ '{toc_path}'")

        # generate items list
        items: List[Union[GlobItem, FileItem, UrlItem]] = []
        for item_idx, item_data in enumerate(items_data):
            if not isinstance(item_data, Mapping):
                raise MalformedError(
                    f"entry not a mapping type @ '{toc_path}{items_key}/{item_idx}'"
                )

            link_keys = _known_link_keys.intersection(item_data)

            # validation checks
            if not link_keys:
                raise MalformedError(
                    f"entry does not contain one of "
                    f"{_known_link_keys!r} @ '{toc_path}{items_key}/{item_idx}'"
                )
            if not len(link_keys) == 1:
                raise MalformedError(
                    f"entry contains incompatible keys "
                    f"{link_keys!r} @ '{toc_path}{items_key}/{item_idx}'"
                )
            for item_key in (GLOB_KEY, URL_KEY):
                for other_key in (subtrees_key, items_key):
                    if link_keys == {item_key} and other_key in item_data:
                        raise MalformedError(
                            f"entry contains incompatible keys "
                            f"'{item_key}' and '{other_key}' @ '{toc_path}{items_key}/{item_idx}'"
                        )

            try:
                if link_keys == {FILE_KEY}:
                    items.append(FileItem(item_data[FILE_KEY]))
                elif link_keys == {GLOB_KEY}:
                    items.append(GlobItem(item_data[GLOB_KEY]))
                elif link_keys == {URL_KEY}:
                    items.append(UrlItem(item_data[URL_KEY], item_data.get("title")))
            except (ValueError, TypeError) as exc:
                exc_arg = exc.args[0] if exc.args else ""
                raise MalformedError(
                    f"entry validation @ '{toc_path}{items_key}/{item_idx}': {exc_arg}"
                ) from exc

        # generate toc key-word arguments
        keywords = {k: toc_data[k] for k in TOCTREE_OPTIONS if k in toc_data}
        for key in defaults:
            if key not in keywords:
                keywords[key] = defaults[key]

        try:
            toc_item = TocTree(items=items, **keywords)
        except (ValueError, TypeError) as exc:
            exc_arg = exc.args[0] if exc.args else ""
            raise MalformedError(
                f"toctree validation @ '{toc_path}': {exc_arg}"
            ) from exc
        toctrees.append(toc_item)

    try:
        doc_item = Document(
            docname=data[file_key], title=data.get("title"), subtrees=toctrees
        )
    except (ValueError, TypeError) as exc:
        exc_arg = exc.args[0] if exc.args else ""
        raise MalformedError(f"doc validation @ '{path}': {exc_arg}") from exc

    # list of docs that need to be parsed recursively (and path)
    docs_to_be_parsed_list = [
        (
            f"{path}/{items_key}/{ii}/"
            if shorthand_used
            else f"{path}{ti}/{items_key}/{ii}/",
            item_data,
        )
        for ti, toc_data in enumerate(subtrees_data)
        for ii, item_data in enumerate(toc_data[items_key])
        if FILE_KEY in item_data
    ]

    return (
        doc_item,
        docs_to_be_parsed_list,
    )


def _parse_docs_list(
    docs_list: Sequence[Tuple[str, Dict[str, Any]]],
    site_map: SiteMap,
    defaults: Dict[str, Any],
    *,
    depth: int,
    file_format: FileFormat,
):
    """Parse a list of docs.

    :param docs_list: sequence of doc items
    :param site_map: site map
    :param defaults: default doc item values
    :param depth: recursive depth (starts at 0)
    :param file_format: doc item file format
    :raises MalformedError: doc file used multiple times
    """
    for child_path, doc_data in docs_list:
        docname = doc_data[FILE_KEY]
        if docname in site_map:
            raise MalformedError(f"document file used multiple times: '{docname}'")
        child_item, child_docs_list = _parse_doc_item(
            doc_data,
            defaults,
            child_path,
            depth=depth,
            file_format=file_format,
        )
        site_map[docname] = child_item

        _parse_docs_list(
            child_docs_list,
            site_map,
            defaults,
            depth=depth + 1,
            file_format=file_format,
        )


def create_toc_dict(site_map: SiteMap, *, skip_defaults: bool = True) -> Dict[str, Any]:
    """Create the ToC dictionary from a site-map.

    :param site_map: site map
    :param skip_defaults: do not add key/values for values that are already the default
    :raises KeyError: invalid file format
    :return: ToC dictionary
    """
    try:
        file_format = FILE_FORMATS[site_map.file_format or "default"]
    except KeyError:
        raise KeyError(f"File format not recognised @ '{site_map.file_format}'")
    data = _docitem_to_dict(
        site_map.root,
        site_map,
        depth=0,
        skip_defaults=skip_defaults,
        is_root=True,
        file_format=file_format,
    )
    if site_map.meta:
        data["meta"] = site_map.meta.copy()
    if site_map.file_format and site_map.file_format != "default":
        # ensure it is the first key
        data = {FILE_FORMAT_KEY: site_map.file_format, **data}
    return data


def _docitem_to_dict(
    doc_item: Document,
    site_map: SiteMap,
    *,
    depth: int,
    file_format: FileFormat,
    skip_defaults: bool = True,
    is_root: bool = False,
    parsed_docnames: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """Create ToC dictionary from a `Document` and a `SiteMap`.

    :param doc_item: document instance
    :param site_map: site map
    :param depth: recursive depth (starts at 0)
    :param file_format: doc item file format
    :param skip_defaults: do not add key/values for values that are already the default
    :param is_root: whether this is the root item, defaults to False
    :param parsed_docnames: parsed document names cache used to prevent infinite
        recursion
    :raises RecursionError: site map recursion
    :raises TypeError: invalid ToC item
    :return: parsed ToC dictionary
    """
    file_key = ROOT_KEY if is_root else FILE_KEY
    subtrees_key = file_format.get_subtrees_key(depth)
    items_key = file_format.get_items_key(depth)

    # protect against infinite recursion
    parsed_docnames = parsed_docnames or set()
    if doc_item.docname in parsed_docnames:
        raise RecursionError(f"{doc_item.docname!r} in site-map multiple times")
    parsed_docnames.add(doc_item.docname)

    data: Dict[str, Any] = {}

    data[file_key] = doc_item.docname
    if doc_item.title is not None:
        data["title"] = doc_item.title

    if not doc_item.subtrees:
        return data

    def _parse_item(item):
        if isinstance(item, FileItem):
            if item in site_map:
                return _docitem_to_dict(
                    site_map[item],
                    site_map,
                    depth=depth + 1,
                    file_format=file_format,
                    skip_defaults=skip_defaults,
                    parsed_docnames=parsed_docnames,
                )
            return {FILE_KEY: str(item)}
        if isinstance(item, GlobItem):
            return {GLOB_KEY: str(item)}
        if isinstance(item, UrlItem):
            if item.title is not None:
                return {URL_KEY: item.url, "title": item.title}
            return {URL_KEY: item.url}
        raise TypeError(item)

    data[subtrees_key] = []
    # TODO handle default_factory
    _defaults = {f.name: f.default for f in fields(TocTree)}
    for toctree in doc_item.subtrees:
        # only add these keys if their value is not the default
        toctree_data = {
            key: getattr(toctree, key)
            for key in TOCTREE_OPTIONS
            if (not skip_defaults) or getattr(toctree, key) != _defaults[key]
        }
        toctree_data[items_key] = [_parse_item(s) for s in toctree.items]
        data[subtrees_key].append(toctree_data)

    # apply shorthand if possible (one toctree in subtrees)
    if len(data[subtrees_key]) == 1 and items_key in data[subtrees_key][0]:
        old_toctree_data = data.pop(subtrees_key)[0]
        # move options to options key
        if len(old_toctree_data) > 1:
            data["options"] = {
                k: v for k, v in old_toctree_data.items() if k != items_key
            }
        data[items_key] = old_toctree_data[items_key]

    return data
