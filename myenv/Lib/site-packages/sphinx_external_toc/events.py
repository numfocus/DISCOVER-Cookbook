"""Sphinx event functions and directives."""
import glob
from pathlib import Path, PurePosixPath
from typing import Any, List, Optional, Set

from docutils import nodes
from sphinx.addnodes import toctree as toctree_node
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.environment import BuildEnvironment
from sphinx.errors import ExtensionError
from sphinx.transforms import SphinxTransform
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective
from sphinx.util.matching import Matcher, patfilter, patmatch

from ._compat import findall
from .api import Document, FileItem, GlobItem, SiteMap, UrlItem
from .parsing import parse_toc_yaml

logger = logging.getLogger(__name__)


def create_warning(
    app: Sphinx,
    doctree: nodes.document,
    category: str,
    message: str,
    *,
    line: Optional[int] = None,
    append_to: Optional[nodes.Element] = None,
    wtype: str = "etoc",
) -> Optional[nodes.system_message]:
    """Generate a warning, logging it if necessary.

    If the warning type is listed in the ``suppress_warnings`` configuration,
    then ``None`` will be returned and no warning logged.
    """
    message = f"{message} [{wtype}.{category}]"
    kwargs = {"line": line} if line is not None else {}

    if not logging.is_suppressed_warning(wtype, category, app.config.suppress_warnings):
        msg_node = doctree.reporter.warning(message, **kwargs)
        if append_to is not None:
            append_to.append(msg_node)
        return msg_node
    return None


def remove_suffix(docname: str, suffixes: List[str]) -> str:
    """Remove any suffixes."""
    for suffix in suffixes:
        if docname.endswith(suffix):
            return docname[: -len(suffix)]
    return docname


def parse_toc_to_env(app: Sphinx, config: Config) -> None:
    """Parse the external toc file and store it in the Sphinx environment.

    Also, change the ``master_doc`` and add to ``exclude_patterns`` if necessary.
    """
    # TODO this seems to work in the tests, but I still want to double check
    external_toc_path = PurePosixPath(app.config["external_toc_path"])
    if not external_toc_path.is_absolute():
        path = Path(app.srcdir) / str(external_toc_path)
    else:
        path = Path(str(external_toc_path))
    if not path.exists():
        raise ExtensionError(f"[etoc] `external_toc_path` does not exist: {path}")
    if not path.is_file():
        raise ExtensionError(f"[etoc] `external_toc_path` is not a file: {path}")
    try:
        site_map = parse_toc_yaml(path)
    except Exception as exc:
        raise ExtensionError(f"[etoc] {exc}") from exc
    config.external_site_map = site_map

    # Update the master_doc to the root doc of the site map
    root_doc = remove_suffix(site_map.root.docname, config.source_suffix)
    if config["master_doc"] != root_doc:
        logger.info("[etoc] Changing master_doc to '%s'", root_doc)
    config["master_doc"] = root_doc

    if config["external_toc_exclude_missing"]:
        # add files not specified in ToC file to exclude list
        new_excluded: List[str] = []
        already_excluded = Matcher(config["exclude_patterns"])
        for suffix in config["source_suffix"]:
            # recurse files in source directory, with this suffix, note
            # we do not use `Path.glob` here, since it does not ignore hidden files:
            # https://stackoverflow.com/questions/49862648/why-do-glob-glob-and-pathlib-path-glob-treat-hidden-files-differently
            for path_str in glob.iglob(
                str(Path(app.srcdir) / "**" / f"*{suffix}"), recursive=True
            ):
                path = Path(path_str)
                if not path.is_file():
                    continue
                posix = path.relative_to(app.srcdir).as_posix()
                posix_no_suffix = posix[: -len(suffix)]
                components = posix.split("/")
                if not (
                    # files can be stored with or without suffixes
                    posix in site_map
                    or posix_no_suffix in site_map
                    # ignore anything already excluded, we have to check against
                    # the file path and all its sub-directory paths
                    or any(
                        already_excluded("/".join(components[: i + 1]))
                        for i in range(len(components))
                    )
                    # don't exclude docnames matching globs
                    or any(patmatch(posix_no_suffix, pat) for pat in site_map.globs())
                ):
                    new_excluded.append(posix)
        if new_excluded:
            logger.info(
                "[etoc] Excluded %s extra file(s) not in toc", len(new_excluded)
            )
            logger.debug("[etoc] Excluded extra file(s) not in toc: %r", new_excluded)
            # Note, don't `extend` list, as it alters the default `Config.config_values`
            config["exclude_patterns"] = config["exclude_patterns"] + new_excluded


def add_changed_toctrees(
    app: Sphinx,
    env: BuildEnvironment,
    added: Set[str],
    changed: Set[str],
    removed: Set[str],
) -> Set[str]:
    """Add docs with new or changed toctrees to changed list."""
    previous_map = getattr(app.env, "external_site_map", None)
    # move external_site_map from config to env
    site_map: SiteMap
    app.env.external_site_map = site_map = app.config.external_site_map
    # Compare to previous map, to record docnames with new or changed toctrees
    if not previous_map:
        return set()
    filenames = site_map.get_changed(previous_map)
    return {remove_suffix(name, app.config.source_suffix) for name in filenames}


class TableOfContentsNode(nodes.Element):
    """A placeholder for the insertion of a toctree (in ``insert_toctrees``)."""

    def __init__(self, **attributes: Any) -> None:
        super().__init__(rawsource="", **attributes)


class TableofContents(SphinxDirective):
    """Insert a placeholder for toctree insertion."""

    # TODO allow for name option of tableofcontents (to reference it)
    def run(self) -> List[TableOfContentsNode]:
        """Insert a ``TableOfContentsNode`` node."""
        node = TableOfContentsNode()
        self.set_source_info(node)
        return [node]


def insert_toctrees(app: Sphinx, doctree: nodes.document) -> None:
    """Create the toctree nodes and add it to the document.

    Adapted from `sphinx/directives/other.py::TocTree`
    """
    # check for existing toctrees and raise warning
    for node in findall(doctree)(toctree_node):
        create_warning(
            app,
            doctree,
            "toctree",
            "toctree directive not expected with external-toc",
            line=node.line,
        )

    toc_placeholders: List[TableOfContentsNode] = list(
        findall(doctree)(TableOfContentsNode)
    )

    site_map: SiteMap = app.env.external_site_map
    doc_item: Optional[Document] = site_map.get(app.env.docname)

    # check for matches with suffix
    # TODO check in sitemap, that we do not have multiple docs of the same name
    # (strip extensions on creation)
    for suffix in app.config.source_suffix:
        if doc_item is not None:
            break
        doc_item = site_map.get(app.env.docname + suffix)

    if doc_item is None or not doc_item.subtrees:
        if toc_placeholders:
            create_warning(
                app,
                doctree,
                "tableofcontents",
                "tableofcontents directive in document with no descendants",
            )
        for node in toc_placeholders:
            node.replace_self([])
        return

    # TODO allow for more than one tableofcontents, i.e. per part?
    for node in toc_placeholders[1:]:
        create_warning(
            app,
            doctree,
            "tableofcontents",
            "more than one tableofcontents directive in document",
            line=node.line,
        )
        node.replace_self([])

    # initial variables
    all_docnames = app.env.found_docs.copy()
    all_docnames.remove(app.env.docname)  # remove current document
    excluded = Matcher(app.config.exclude_patterns)

    node_list: List[nodes.Element] = []

    for toctree in doc_item.subtrees:
        subnode = toctree_node()
        subnode["parent"] = app.env.docname
        subnode.source = doctree["source"]
        subnode.line = 1
        subnode["entries"] = []
        subnode["includefiles"] = []
        subnode["maxdepth"] = toctree.maxdepth
        subnode["caption"] = toctree.caption
        # TODO this wasn't in the original code,
        # but alabaster theme intermittently raised `KeyError('rawcaption')`
        subnode["rawcaption"] = toctree.caption or ""
        subnode["glob"] = any(isinstance(entry, GlobItem) for entry in toctree.items)
        subnode["hidden"] = False if toc_placeholders else toctree.hidden
        subnode["includehidden"] = False
        subnode["numbered"] = (
            0
            if toctree.numbered is False
            else (999 if toctree.numbered is True else int(toctree.numbered))
        )
        subnode["titlesonly"] = toctree.titlesonly
        wrappernode = nodes.compound(classes=["toctree-wrapper"])
        wrappernode.append(subnode)

        for entry in toctree.items:
            if isinstance(entry, UrlItem):
                subnode["entries"].append((entry.title, entry.url))

            elif isinstance(entry, FileItem):
                child_doc_item = site_map[entry]
                docname = str(entry)
                title = child_doc_item.title

                docname = remove_suffix(docname, app.config.source_suffix)

                if docname not in app.env.found_docs:
                    if excluded(app.env.doc2path(docname, None)):
                        message = f"toctree contains reference to excluded document {docname!r}"
                    else:
                        message = f"toctree contains reference to nonexisting document {docname!r}"

                    create_warning(app, doctree, "ref", message, append_to=node_list)
                    app.env.note_reread()
                else:
                    subnode["entries"].append((title, docname))
                    subnode["includefiles"].append(docname)

            elif isinstance(entry, GlobItem):
                patname = str(entry)
                docnames = sorted(patfilter(all_docnames, patname))
                for docname in docnames:
                    all_docnames.remove(docname)  # don't include it again
                    subnode["entries"].append((None, docname))
                    subnode["includefiles"].append(docname)
                if not docnames:
                    message = (
                        f"toctree glob pattern '{entry}' didn't match any documents"
                    )
                    create_warning(app, doctree, "glob", message, append_to=node_list)

        # reversing entries can be useful when globbing
        if toctree.reversed:
            subnode["entries"] = list(reversed(subnode["entries"]))
            subnode["includefiles"] = list(reversed(subnode["includefiles"]))

        node_list.append(wrappernode)

    if toc_placeholders:
        toc_placeholders[0].replace_self(node_list)
    elif doctree.children and isinstance(doctree.children[-1], nodes.section):
        # note here the toctree cannot not just be appended to the end of the doc,
        # since `TocTreeCollector.process_doc` expects it in a section
        # otherwise it will result in the child documents being on the same level as this document
        # TODO check if there is this is always ok
        doctree.children[-1].extend(node_list)
    else:
        doctree.children.extend(node_list)


class InsertToctrees(SphinxTransform):
    """Create the toctree nodes and add it to the document.

    This needs to occur at least before the ``DoctreeReadEvent`` (priority 880),
    which triggers the `TocTreeCollector.process_doc` event (priority 500)
    """

    default_priority = 100

    def apply(self, **kwargs: Any) -> None:
        insert_toctrees(self.app, self.document)


def ensure_index_file(app: Sphinx, exception: Optional[Exception]) -> None:
    """Ensure that an index.html exists for HTML builds.

    This is required when navigating to the site, without specifying a page,
    which will then route to index.html by default.
    """
    index_path = Path(app.outdir).joinpath("index.html")
    if (
        exception is not None
        or "html" not in app.builder.format
        or app.config.master_doc == "index"
        # TODO: rewrite the redirect if master_doc has changed since last build
        or index_path.exists()
    ):
        return

    root_name = remove_suffix(app.config.master_doc, app.config.source_suffix)

    if app.builder.name == "dirhtml":
        redirect_url = f"{root_name}/index.html"
    else:
        # Assume a single index for all non dir-HTML builders
        redirect_url = f"{root_name}.html"

    redirect_text = f'<meta http-equiv="Refresh" content="0; url={redirect_url}" />\n'
    index_path.write_text(redirect_text, encoding="utf8")
    logger.info("[etoc] missing index.html written as redirect to '%s.html'", root_name)
