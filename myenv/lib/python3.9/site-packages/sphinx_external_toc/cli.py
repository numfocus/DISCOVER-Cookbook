from pathlib import Path, PurePosixPath

import click
import yaml

from sphinx_external_toc import __version__
from sphinx_external_toc.parsing import FILE_FORMATS, create_toc_dict, parse_toc_yaml
from sphinx_external_toc.tools import (
    create_site_from_toc,
    create_site_map_from_path,
    migrate_jupyter_book,
)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__)
def main():
    """Command-line for sphinx-external-toc."""


@main.command("parse")
@click.argument("toc_file", type=click.Path(exists=True, file_okay=True))
def parse_toc(toc_file):
    """Parse a ToC file to a site-map YAML."""
    site_map = parse_toc_yaml(toc_file)
    click.echo(yaml.dump(site_map.as_json(), sort_keys=False, default_flow_style=False))


@main.command("to-project")
@click.argument("toc_file", type=click.Path(exists=True, file_okay=True))
@click.option(
    "-p",
    "--path",
    default=None,
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    help="The root directory [default: ToC file directory].",
)
@click.option(
    "-e",
    "--extension",
    type=click.Choice(["rst", "md"]),
    default="rst",
    show_default=True,
    help="The default file extension to use.",
)
@click.option("-o", "--overwrite", is_flag=True, help="Overwrite existing files.")
def create_site(toc_file, path, extension, overwrite):
    """Create a project directory from a ToC file."""
    create_site_from_toc(
        toc_file, root_path=path, default_ext="." + extension, overwrite=overwrite
    )
    # TODO option to add basic conf.py?
    click.secho("SUCCESS!", fg="green")


@main.command("from-project")
@click.argument(
    "site_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.option(
    "-e",
    "--extension",
    multiple=True,
    default=[".rst", ".md"],
    show_default=True,
    help="File extensions to consider as documents (use multiple times)",
)
@click.option(
    "-i",
    "--index",
    default="index",
    show_default=True,
    help="File name (without suffix) considered as the index file in a folder",
)
@click.option(
    "-s",
    "--skip-match",
    multiple=True,
    default=[".*"],
    show_default=True,
    help="File/Folder names which match will be ignored (use multiple times)",
)
@click.option(
    "-t",
    "--guess-titles",
    is_flag=True,
    help="Guess titles of documents from path names",
)
@click.option(
    "-f",
    "--file-format",
    type=click.Choice(list(FILE_FORMATS)),
    default=list(FILE_FORMATS)[0],
    show_default=True,
    help="The key-mappings to use.",
)
def create_toc(site_dir, extension, index, skip_match, guess_titles, file_format):
    """Create a ToC file from a project directory."""
    site_map = create_site_map_from_path(
        site_dir,
        suffixes=extension,
        default_index=index,
        ignore_matches=skip_match,
        file_format=file_format,
    )
    if guess_titles:
        for docname in site_map:
            # don't give a title to the root document
            if docname == site_map.root.docname:
                continue
            filepath = PurePosixPath(docname)
            # use the folder name for index files
            name = filepath.parent.name if filepath.name == index else filepath.name
            # split into words
            words = name.split("_")
            # remove first word if is an integer
            words = words[1:] if words and all(c.isdigit() for c in words[0]) else words
            site_map[docname].title = " ".join(words).capitalize()
    data = create_toc_dict(site_map)
    click.echo(yaml.dump(data, sort_keys=False, default_flow_style=False))


@main.command("migrate")
@click.argument("toc_file", type=click.Path(exists=True, file_okay=True))
@click.option(
    "-f",
    "--format",
    type=click.Choice(["jb-v0.10"]),
    help="The format to migrate from.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(allow_dash=True, exists=False, file_okay=True, dir_okay=False),
    help="Write to a file path.",
)
def migrate_toc(toc_file, format, output):
    """Migrate a ToC from a previous revision."""
    toc = migrate_jupyter_book(Path(toc_file))
    content = yaml.dump(toc, sort_keys=False, default_flow_style=False)
    if output:
        path = Path(output)
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(content, encoding="utf8")
        click.secho(f"Written to: {path}", fg="green")
    else:
        click.echo(content)
