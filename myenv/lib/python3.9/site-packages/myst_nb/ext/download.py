import os
from pathlib import Path

from docutils import nodes
from sphinx.addnodes import download_reference
from sphinx.util.docutils import ReferenceRole

from myst_nb.sphinx_ import SphinxEnvType


class NbDownloadRole(ReferenceRole):
    """Role to download an executed notebook."""

    def run(self):
        """Run the role."""
        # get a path relative to the current document
        self.env: SphinxEnvType
        path = Path(self.env.mystnb_config.output_folder).joinpath(
            *(self.env.docname.split("/")[:-1] + self.target.split("/"))
        )
        reftarget = (
            path.as_posix()
            if os.name == "nt"
            else ("/" + os.path.relpath(path, self.env.app.srcdir))
        )
        node = download_reference(self.rawtext, reftarget=reftarget)
        self.set_source_info(node)
        title = self.title if self.has_explicit_title else self.target
        node += nodes.literal(
            self.rawtext, title, classes=["xref", "download", "myst-nb"]
        )
        return [node], []
