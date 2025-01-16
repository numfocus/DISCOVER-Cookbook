"""This module provides equivalent loggers for both docutils and sphinx.

These loggers act like standard Python logging.Logger objects,
but route messages via the docutils/sphinx reporting systems.

They are initialised with a docutils document,
in order to provide the source location of the log message,
and can also both handle ``line`` and ``subtype`` keyword arguments:
``logger.warning("message", line=1, subtype="foo")``

"""
import logging
from typing import Union

from docutils import nodes

DEFAULT_LOG_TYPE = "mystnb"


class SphinxDocLogger(logging.LoggerAdapter):
    """Wraps a Sphinx logger, which routes messages to the docutils document reporter.

    The document path and message type are automatically included in the message,
    and ``line`` is allowed as a keyword argument,
    as well as the standard sphinx logger keywords:
    ``subtype``, ``color``, ``once``, ``nonl``.

    As per the sphinx logger, warnings are suppressed,
    if their ``type.subtype`` are included in the ``suppress_warnings`` configuration.
    These are also appended to the end of messages.
    """

    def __init__(self, document: nodes.document, type_name: str = DEFAULT_LOG_TYPE):
        from sphinx.util import logging as sphinx_logging

        docname = document.settings.env.docname
        self.logger = sphinx_logging.getLogger(f"{type_name}-{docname}")
        # default extras to parse to sphinx logger
        # location can be: docname, (docname, lineno), or a node
        self.extra = {"docname": docname, "type": type_name}

    def process(self, msg, kwargs):
        self.extra: dict
        kwargs["extra"] = self.extra
        if "type" in kwargs:  # override type
            self.extra["type"] = kwargs.pop("type")
        subtype = ("." + kwargs["subtype"]) if "subtype" in kwargs else ""
        if kwargs.get("line", None) is not None:  # add line to location
            # note this will be overridden by the location keyword
            self.extra["location"] = (self.extra["docname"], kwargs.pop("line"))
        else:
            self.extra["location"] = self.extra["docname"]
        if "parent" in kwargs:
            # TODO ideally here we would append a system_message to this node,
            # then it could replace myst_parser.SphinxRenderer.create_warning
            self.extra["parent"] = kwargs.pop("parent")
        return f"{msg} [{self.extra['type']}{subtype}]", kwargs


class DocutilsDocLogger(logging.LoggerAdapter):
    """A logger which routes messages to the docutils document reporter.

    The document path and message type are automatically included in the message,
    and ``line`` is allowed as a keyword argument.
    The standard sphinx logger keywords are allowed but ignored:
    ``subtype``, ``color``, ``once``, ``nonl``.

    ``type.subtype`` are also appended to the end of messages.
    """

    KEYWORDS = [
        "type",
        "subtype",
        "location",
        "nonl",
        "color",
        "once",
        "line",
        "parent",
    ]

    def __init__(self, document: nodes.document, type_name: str = DEFAULT_LOG_TYPE):
        self.logger: logging.Logger = logging.getLogger(
            f"{type_name}-{document.source}"
        )
        # docutils handles the level of output logging
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            self.logger.addHandler(DocutilsLogHandler(document))

        # default extras to parse to sphinx logger
        # location can be: docname, (docname, lineno), or a node
        self.extra = {"type": type_name, "line": None, "parent": None}

    def process(self, msg, kwargs):
        kwargs["extra"] = self.extra
        subtype = ("." + kwargs["subtype"]) if "subtype" in kwargs else ""
        for keyword in self.KEYWORDS:
            if keyword in kwargs:
                kwargs["extra"][keyword] = kwargs.pop(keyword)
        etype = "" if not self.extra else self.extra.get("type", "")
        return f"{msg} [{etype}{subtype}]", kwargs


class DocutilsLogHandler(logging.Handler):
    """Handle logging via a docutils reporter."""

    def __init__(self, document: nodes.document) -> None:
        """Initialize a new handler."""
        super().__init__()
        self._document = document
        reporter = self._document.reporter
        self._name_to_level = {
            "DEBUG": reporter.DEBUG_LEVEL,
            "INFO": reporter.INFO_LEVEL,
            "WARN": reporter.WARNING_LEVEL,
            "WARNING": reporter.WARNING_LEVEL,
            "ERROR": reporter.ERROR_LEVEL,
            "CRITICAL": reporter.SEVERE_LEVEL,
            "FATAL": reporter.SEVERE_LEVEL,
        }

    def emit(self, record: logging.LogRecord) -> None:
        """Handle a log record."""
        levelname = record.levelname.upper()
        level = self._name_to_level.get(levelname, self._document.reporter.DEBUG_LEVEL)
        node = self._document.reporter.system_message(
            level,
            record.msg,
            **({"line": record.line} if record.line is not None else {}),  # type: ignore
        )
        if record.parent is not None:  # type: ignore
            record.parent.append(node)  # type: ignore


LoggerType = Union[DocutilsDocLogger, SphinxDocLogger]
