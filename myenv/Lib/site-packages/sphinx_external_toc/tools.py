import re
import shutil
from fnmatch import fnmatch
from itertools import chain
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

import yaml

from .api import Document, FileItem, SiteMap, TocTree
from .parsing import (
    DEFAULT_ITEMS_KEY,
    DEFAULT_SUBTREES_KEY,
    MalformedError,
    create_toc_dict,
    parse_toc_data,
    parse_toc_yaml,
)


def create_site_from_toc(
    toc_path: Union[str, Path],
    *,
    root_path: Union[None, str, Path] = None,
    default_ext: str = ".rst",
    encoding: str = "utf8",
    overwrite: bool = False,
    toc_name: Optional[str] = "_toc.yml",
) -> SiteMap:
    """Create the files defined in the external toc file.

    Additional files can also be created by defining them in
    `meta`/`create_files` of the toc. Text can also be appended to files, by
    defining them in `meta`/`create_append` (as a mapping from files to text).

    :param toc_path: path to ToC file
    :param root_path: the root directory, or use ToC file directory
    :param default_ext: default file extension to use
    :param encoding: encoding for writing files
    :param overwrite: overwrite existing files (otherwise raise ``IOError``)
    :param toc_name: copy ToC file to root with this name

    """
    assert default_ext in {".rst", ".md"}
    site_map = parse_toc_yaml(toc_path)

    root_path = Path(toc_path).parent if root_path is None else Path(root_path)
    root_path.mkdir(parents=True, exist_ok=True)

    # retrieve and validate meta variables
    additional_files = site_map.meta.get("create_files", [])
    assert isinstance(additional_files, Sequence), "'create_files' should be a list"
    append_text = site_map.meta.get("create_append", {})
    assert isinstance(append_text, Mapping), "'create_append' should be a mapping"

    # copy toc file to root
    if toc_name and not root_path.joinpath(toc_name).exists():
        shutil.copyfile(toc_path, root_path.joinpath(toc_name))

    # create files
    for docname in chain(site_map, additional_files):
        # create document
        filename = docname
        if not any(docname.endswith(ext) for ext in {".rst", ".md"}):
            filename += default_ext
        docpath = root_path.joinpath(PurePosixPath(filename))
        if docpath.exists() and not overwrite:
            raise IOError(f"Path already exists: {docpath}")
        docpath.parent.mkdir(parents=True, exist_ok=True)

        content = []

        # add heading based on file type
        heading = f"Heading: {filename}"
        if filename.endswith(".rst"):
            content = [heading, "=" * len(heading), ""]
        elif filename.endswith(".md"):
            content = ["# " + heading, ""]

        # append extra text
        extra_lines = append_text.get(docname, "").splitlines()
        if extra_lines:
            content.extend(extra_lines + [""])

        # note \n works when writing for all platforms:
        # https://docs.python.org/3/library/os.html#os.linesep
        docpath.write_text("\n".join(content), encoding=encoding)

    return site_map


def create_site_map_from_path(
    root_path: Union[str, Path],
    *,
    suffixes: Sequence[str] = (".rst", ".md"),
    default_index: str = "index",
    ignore_matches: Sequence[str] = (".*",),
    file_format: Optional[str] = None,
) -> SiteMap:
    """Create the site-map from a folder structure.

    Files and folders are sorted in natural order, see:
    https://en.wikipedia.org/wiki/Natural_sort_order.

    :param suffixes: file suffixes to consider as documents
    :param default_index: file name (without suffix) considered as the index
        file for a folder, if not found then the first file is taken as the
        index
    :param ignore_matches: file/folder names which match one of these will be
        ignored, uses fnmatch Unix shell-style wildcards, defaults to ignoring
        hidden files (starting with a dot)
    """
    root_path = Path(root_path)
    # assess root
    root_index, root_files, root_folders = _assess_folder(
        root_path, suffixes, default_index, ignore_matches
    )
    if not root_index:
        raise IOError(f"path does not contain a root file: {root_path}")

    # create root item and child folders
    root_item, indexed_folders = _doc_item_from_path(
        root_path,
        root_path,
        root_index,
        root_files,
        root_folders,
        suffixes,
        default_index,
        ignore_matches,
    )

    # create base site-map
    site_map = SiteMap(root=root_item, file_format=file_format)
    # we add all files to the site map, even if they don't have descendants
    # so we may later change their title
    for root_file in root_files:
        site_map[root_file] = Document(root_file)

    # while there are subfolders add them to the site-map
    while indexed_folders:
        (
            sub_path,
            child_index,
            child_files,
            child_folders,
        ) = indexed_folders.pop(0)
        for child_file in child_files:
            child_docname = (sub_path / child_file).relative_to(root_path).as_posix()
            assert child_docname not in site_map
            site_map[child_docname] = Document(child_docname)
        doc_item, new_indexed_folders = _doc_item_from_path(
            root_path,
            sub_path,
            child_index,
            child_files,
            child_folders,
            suffixes,
            default_index,
            ignore_matches,
        )
        assert doc_item.docname not in site_map
        site_map[doc_item.docname] = doc_item
        indexed_folders += new_indexed_folders
    return site_map


def _doc_item_from_path(
    root: Path,
    folder: Path,
    index_docname: str,
    other_docnames: Sequence[str],
    folder_names: Sequence[str],
    suffixes: Sequence[str],
    default_index: str,
    ignore_matches: Sequence[str],
):
    """Return the ``Document`` and children folders that contain an index."""
    file_items = [
        FileItem((folder / name).relative_to(root).as_posix())
        for name in other_docnames
    ]

    # get folders with sub-indexes
    indexed_folders = []
    index_items = []
    for folder_name in folder_names:
        sub_folder = folder / folder_name
        child_index, child_files, child_folders = _assess_folder(
            sub_folder, suffixes, default_index, ignore_matches
        )
        if not child_index:
            # TODO handle folders with no files, but files in sub-folders
            continue
        indexed_folders.append((sub_folder, child_index, child_files, child_folders))
        index_items.append(
            FileItem((sub_folder / child_index).relative_to(root).as_posix())
        )

    doc_item = Document(
        docname=(folder / index_docname).relative_to(root).as_posix(),
        subtrees=[TocTree(items=file_items + index_items)]  # type: ignore[arg-type]
        if (file_items or index_items)
        else [],
    )
    return doc_item, indexed_folders


def natural_sort(iterable):
    """Sort an iterable by https://en.wikipedia.org/wiki/Natural_sort_order."""

    def _convert(text):
        return int(text) if text.isdigit() else text.lower()

    def _alphanum_key(key):
        return [_convert(c) for c in re.split("([0-9]+)", key)]

    return sorted(iterable, key=_alphanum_key)


def _assess_folder(
    folder: Path,
    suffixes: Sequence[str],
    default_index: str,
    ignore_matches: Sequence[str],
) -> Tuple[Optional[str], Sequence[str], Sequence[str]]:
    """Assess the folder for ToC items. Strips suffixes from file names and
    sorts file/folder names by natural order.

    :returns: (index file name, other file names, folders)
    """
    if not folder.is_dir():
        raise IOError(f"path must be a directory: {folder}")

    def _strip_suffix(name: str) -> str:
        for suffix in suffixes:
            if name.endswith(suffix):
                return name[: -len(suffix)]
        return name

    # conversion to a set is to remove duplicates, e.g. doc.rst and doc.md
    sub_files = natural_sort(
        list(
            set(
                [
                    _strip_suffix(path.name)
                    for path in folder.iterdir()
                    if path.is_file()
                    and any(path.name.endswith(suffix) for suffix in suffixes)
                    and (not any(fnmatch(path.name, pat) for pat in ignore_matches))
                ]
            )
        )
    )
    sub_folders = natural_sort(
        [
            path.name
            for path in folder.iterdir()
            if path.is_dir()
            if (not any(fnmatch(path.name, pat) for pat in ignore_matches))
        ]
    )

    if not sub_files:
        return (None, sub_files, sub_folders)

    # get the index file for this folder
    try:
        index = sub_files.index(default_index)
    except ValueError:
        index = 0
    index_file = sub_files.pop(index)

    return (index_file, sub_files, sub_folders)


def migrate_jupyter_book(
    toc: Union[Path, Dict[str, Any], list],
) -> Dict[str, Any]:
    """Migrate a jupyter-book v0.10.2 toc."""

    if isinstance(toc, Path):
        with toc.open(encoding="utf8") as handle:
            toc = yaml.safe_load(handle)

    # convert list to dict
    if isinstance(toc, list):
        toc_updated = toc[0]
        if not isinstance(toc_updated, dict):
            raise MalformedError("First list item is not a dict")
        if len(toc) > 1:
            first_items: List[dict] = []
            top_items_key = "sections"  # this is the default top-level key
            # The first set of pages will be called *either* sections or chapters
            if "sections" in toc_updated and "chapters" in toc_updated:
                raise MalformedError(
                    "First list item contains both 'chapters' and 'sections' keys"
                )
            for key in ("sections", "chapters"):
                if key in toc_updated:
                    top_items_key = key
                    items = toc_updated.pop(key)
                    if not isinstance(items, Sequence):
                        raise MalformedError(f"First list item '{key}' is not a list")
                    first_items += items

            # add list items after to same level
            first_items += toc[1:]

            # check for part keys (and also chapter which was deprecated)
            contains_part = any(
                ("part" in item or "chapter" in item) for item in first_items
            )
            contains_file = any("file" in item for item in first_items)
            if contains_part and contains_file:
                raise MalformedError("top-level contains mixed 'part' and 'file' keys")

            toc_updated["parts" if contains_part else top_items_key] = first_items

        toc = toc_updated
    elif not isinstance(toc, dict):
        raise MalformedError("ToC is not a list or dict")

    # convert first `file` to `root`
    if "file" not in toc:
        raise MalformedError("no top-level 'file' key found")
    toc["root"] = toc.pop("file")

    # setting `titlesonly` True is now part of the file format
    # toc["defaults"] = {"titlesonly": True}

    # we should now have a dict with either a 'parts', 'chapters', or 'sections' key
    top_level_keys = {"parts", "chapters", "sections"}.intersection(toc.keys())
    if len(top_level_keys) > 1:
        raise MalformedError(
            f"There is more than one top-level key: {top_level_keys!r}"
        )
    # from the top-level key we can now derive the file-format (for key-mappings)
    file_format = {
        "": "jb-book",
        "parts": "jb-book",
        "chapters": "jb-book",
        "sections": "jb-article",
    }["" if not top_level_keys else list(top_level_keys)[0]]

    # change all parts to DEFAULT_SUBTREES_KEY
    # change all chapters to DEFAULT_ITEMS_KEY
    # change all part/chapter to caption
    dicts = [toc]
    while dicts:
        dct = dicts.pop(0)
        if "chapters" in dct and "sections" in dct:
            raise MalformedError(f"both 'chapters' and 'sections' in same dict: {dct}")
        if "parts" in dct:
            dct[DEFAULT_SUBTREES_KEY] = dct.pop("parts")
        if "sections" in dct:
            dct[DEFAULT_ITEMS_KEY] = dct.pop("sections")
        if "chapters" in dct:
            dct[DEFAULT_ITEMS_KEY] = dct.pop("chapters")
        for key in ("part", "chapter"):
            if key in dct:
                dct["caption"] = dct.pop(key)

        # add nested dicts
        for val in dct.values():
            for item in val if isinstance(val, Sequence) else [val]:
                if isinstance(item, dict):
                    dicts.append(item)

    # if `numbered` at top level, move to options or copy to each subtree
    if "numbered" in toc:
        numbered = toc.pop("numbered")
        if DEFAULT_ITEMS_KEY in toc:
            toc["options"] = {"numbered": numbered}
        for subtree in toc.get(DEFAULT_SUBTREES_KEY, []):
            if "numbered" not in subtree:
                subtree["numbered"] = numbered

    # now convert to a site map, so we can validate
    try:
        site_map = parse_toc_data(toc)
    except MalformedError as err:
        raise MalformedError(f"Error parsing migrated output: {err}") from err
    # change the file format and convert back to a dict
    site_map.file_format = file_format
    return create_toc_dict(site_map, skip_defaults=True)
