"""Central handling of warnings for the myst-nb extension."""
from __future__ import annotations

from enum import Enum
from typing import Sequence

from docutils import nodes
from myst_parser.warnings_ import MystWarnings
from myst_parser.warnings_ import create_warning as myst_parser_create_warnings

__all__ = [
    "MystWarnings",
    "MystNBWarnings",
    "create_warning",
]


class MystNBWarnings(Enum):
    """MySTNB warning types."""

    LEXER = "lexer"
    """Issue resolving lexer"""

    FIG_CAPTION = "fig_caption"
    """Issue resoliving figure caption"""

    MIME_TYPE = "mime_type"
    """Issue resolving MIME type"""
    OUTPUT_TYPE = "output_type"
    """Issue resolving Output type"""

    CELL_METADATA_KEY = "cell_metadata_key"
    """Issue with a key in a cell's `metadata` dictionary."""
    CELL_CONFIG = "cell_config"
    """Issue with a cell's configuration or metadata."""


def _is_suppressed_warning(
    type: str, subtype: str, suppress_warnings: Sequence[str]
) -> bool:
    """Check whether the warning is suppressed or not.

    Mirrors:
    https://github.com/sphinx-doc/sphinx/blob/47d9035bca9e83d6db30a0726a02dc9265bd66b1/sphinx/util/logging.py
    """
    if type is None:
        return False

    subtarget: str | None

    for warning_type in suppress_warnings:
        if "." in warning_type:
            target, subtarget = warning_type.split(".", 1)
        else:
            target, subtarget = warning_type, None

        if target == type and subtarget in (None, subtype, "*"):
            return True

    return False


def create_warning(
    document: nodes.document,
    message: str,
    subtype: MystNBWarnings | MystWarnings,
    *,
    line: int | None = None,
    append_to: nodes.Element | None = None,
) -> nodes.system_message | None:
    """Generate a warning, logging if it is necessary.

    If the warning type is listed in the ``suppress_warnings`` configuration,
    then ``None`` will be returned and no warning logged.
    """
    # Pass off Myst Parser warnings to that package
    if isinstance(subtype, MystWarnings):
        myst_parser_create_warnings(
            document=document,
            message=message,
            subtype=subtype,
            line=line,
            append_to=append_to,
        )

    wtype = "myst-nb"
    # figure out whether to suppress the warning, if sphinx is available,
    # it will have been set up by the Sphinx environment,
    # otherwise we will use the configuration set by docutils
    suppress_warnings: Sequence[str] = []
    try:
        suppress_warnings = document.settings.env.app.config.suppress_warnings
    except AttributeError:
        suppress_warnings = document.settings.myst_suppress_warnings or []
    if _is_suppressed_warning(wtype, subtype.value, suppress_warnings):
        return None

    kwargs = {"line": line} if line is not None else {}
    message = f"{message} [{wtype}.{subtype.value}]"
    msg_node = document.reporter.warning(message, **kwargs)
    if append_to is not None:
        append_to.append(msg_node)
    return msg_node
