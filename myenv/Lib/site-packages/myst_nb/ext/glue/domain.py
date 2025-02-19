"""A domain to register in sphinx.

This is required for any directive/role names using `:`.
"""
from sphinx.domains import Domain

from .directives import (
    PasteAnyDirective,
    PasteFigureDirective,
    PasteMarkdownDirective,
    PasteMathDirective,
)
from .roles import PasteMarkdownRole, PasteRoleAny, PasteTextRole


class NbGlueDomain(Domain):
    """A sphinx domain for defining glue roles and directives.

    Note, the only reason we use this,
    is that sphinx will not allow for `:` in a directive/role name,
    if it is part of a domain.
    """

    name = "glue"
    label = "NotebookGlue"

    # data version, bump this when the format of self.data changes
    data_version = 1

    roles = {
        "": PasteRoleAny(),
        "any": PasteRoleAny(),
        "text": PasteTextRole(),
        "md": PasteMarkdownRole(),
    }
    directives = {
        "": PasteAnyDirective,
        "any": PasteAnyDirective,
        "figure": PasteFigureDirective,
        "math": PasteMathDirective,
        "md": PasteMarkdownDirective,
    }

    def merge_domaindata(self, *args, **kwargs):
        pass

    def resolve_any_xref(self, *args, **kwargs):
        return []
