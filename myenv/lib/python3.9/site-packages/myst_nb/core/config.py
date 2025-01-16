"""Configuration for myst-nb."""
import dataclasses as dc
from enum import Enum
from typing import Any, Callable, Dict, Iterable, Literal, Optional, Sequence, Tuple

from myst_parser.config.dc_validators import (
    ValidatorType,
    deep_iterable,
    deep_mapping,
    in_,
    instance_of,
    optional,
    validate_fields,
)

from myst_nb.warnings_ import MystNBWarnings


def custom_formats_converter(value: dict) -> Dict[str, Tuple[str, dict, bool]]:
    """Convert the custom format dict."""
    if not isinstance(value, dict):
        raise TypeError(f"`nb_custom_formats` must be a dict: {value}")
    output: Dict[str, Tuple[str, dict, bool]] = {}
    for suffix, reader in value.items():
        if not isinstance(suffix, str):
            raise TypeError(f"`nb_custom_formats` keys must be a string: {suffix}")
        if isinstance(reader, str):
            output[suffix] = (reader, {}, False)
        elif not isinstance(reader, Sequence):
            raise TypeError(
                f"`nb_custom_formats` values must be a string or sequence: {reader}"
            )
        elif len(reader) == 2:
            output[suffix] = (reader[0], reader[1], False)
        elif len(reader) == 3:
            output[suffix] = (reader[0], reader[1], reader[2])
        else:
            raise TypeError(
                f"`nb_custom_formats` values must be a string, of sequence of length "
                f"2 or 3: {reader}"
            )
        if not isinstance(output[suffix][0], str):
            raise TypeError(
                f"`nb_custom_formats` values[0] must be a string: {output[suffix][0]}"
            )
            # TODO check can be loaded as a python object?
        if not isinstance(output[suffix][1], dict):
            raise TypeError(
                f"`nb_custom_formats` values[1] must be a dict: {output[suffix][1]}"
            )
        if not isinstance(output[suffix][2], bool):
            raise TypeError(
                f"`nb_custom_formats` values[2] must be a bool: {output[suffix][2]}"
            )
    return output


def ipywidgets_js_factory() -> Dict[str, Dict[str, str]]:
    """Create a default ipywidgets js dict."""
    # see: https://ipywidgets.readthedocs.io/en/7.6.5/embedding.html
    return {
        # Load RequireJS, used by the IPywidgets for dependency management
        "https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js": {
            "integrity": "sha256-Ae2Vz/4ePdIu6ZyI/5ZGsYnb+m0JlOmKPjt6XZ9JJkA=",
            "crossorigin": "anonymous",
        },
        # Load IPywidgets bundle for embedding.
        "https://cdn.jsdelivr.net/npm/@jupyter-widgets/html-manager@1.0.6/dist/embed-amd.js": {
            "data-jupyter-widgets-cdn": "https://cdn.jsdelivr.net/npm/",
            "crossorigin": "anonymous",
        },
    }


def has_items(*validators) -> ValidatorType:
    """
    A validator that performs validation per item of a sequence.

    :param validators: Validator to apply per item
    """

    def _validator(inst, field: dc.Field, value, suffix=""):
        if not isinstance(value, Sequence):
            raise TypeError(f"{suffix}{field.name} must be a sequence: {value}")
        if len(value) != len(validators):
            raise TypeError(
                f"{suffix}{field.name!r} must be a sequence of length "
                f"{len(validators)}: {value}"
            )

        for idx, (validator, member) in enumerate(zip(validators, value)):
            validator(inst, field, member, suffix=f"{suffix}[{idx}]")

    return _validator


class Section(Enum):
    """Config section tags."""

    global_lvl = "global"
    """Global level configuration."""
    file_lvl = "notebook"
    """File level configuration."""
    cell_lvl = "cell"
    """Cell level configuration."""
    config = "config"
    """Meta configuration."""
    read = "read"
    """Configuration for reading files."""
    execute = "execute"
    """Configuration for executing notebooks."""
    render = "render"
    """Configuration for rendering notebook elements."""


@dc.dataclass()
class NbParserConfig:
    """Global configuration options for the MyST-NB parser.

    Note: in the docutils/sphinx configuration,
    these option names are prepended with ``nb_``
    """

    def __post_init__(self):
        self.custom_formats = custom_formats_converter(self.custom_formats)
        validate_fields(self)

    # file read options

    custom_formats: Dict[str, Tuple[str, dict, bool]] = dc.field(
        default_factory=dict,
        metadata={
            "help": "Custom formats for reading notebook; suffix -> reader",
            "omit": ["docutils"],
            "sections": (Section.global_lvl, Section.read),
        },
    )
    # docutils does not support the custom formats mechanism
    read_as_md: bool = dc.field(
        default=False,
        metadata={
            "validator": instance_of(bool),
            "help": "Read as the MyST Markdown format",
            "sphinx_exclude": True,
        },
        repr=False,
    )

    # configuration override keys (applied after file read)

    # TODO previously we had `nb_render_key` (default: "render"),
    # for cell.metadata.render.image and cell.metadata.render.figure`,
    # and also `timeout`/`allow_errors` in notebook.metadata.execution
    # do we still support these or deprecate?
    # (plus also cell.metadata.tags:
    #   nbclient: `skip-execution` and `raises-exception`,
    #   myst_nb: `remove_cell`, `remove-cell`, `remove_input`, `remove-input`,
    #            `remove_output`, `remove-output`, `remove-stderr`
    # )
    # see also:
    # https://nbformat.readthedocs.io/en/latest/format_description.html#cell-metadata
    metadata_key: str = dc.field(
        default="mystnb",
        metadata={
            "validator": instance_of(str),
            "help": "Notebook level metadata key for config overrides",
            "sections": (Section.global_lvl, Section.config),
        },
    )
    cell_metadata_key: str = dc.field(
        default="mystnb",
        metadata={
            "validator": instance_of(str),
            "help": "Cell level metadata key for config overrides",
            "legacy_name": "nb_render_key",
            "sections": (Section.global_lvl, Section.file_lvl, Section.config),
        },
    )

    # notebook execution options

    kernel_rgx_aliases: Dict[str, str] = dc.field(
        default_factory=dict,
        metadata={
            "validator": deep_mapping(instance_of(str), instance_of(str)),
            "help": "Mapping of kernel name regex to replacement kernel name"
            "(applied before execution)",
            "omit": ["docutils"],
            "sections": (Section.global_lvl, Section.execute),
        },
    )
    eval_name_regex: str = dc.field(
        default=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
        metadata={
            "validator": instance_of(str),
            "help": "Regex that matches permitted values of eval expressions",
            "sections": (Section.global_lvl, Section.file_lvl, Section.execute),
        },
    )
    execution_mode: Literal["off", "force", "auto", "cache", "inline"] = dc.field(
        default="auto",
        metadata={
            "validator": in_(
                [
                    "off",
                    "auto",
                    "force",
                    "cache",
                    "inline",
                ]
            ),
            "help": "Execution mode for notebooks",
            "legacy_name": "jupyter_execute_notebooks",
            "sections": (Section.global_lvl, Section.file_lvl, Section.execute),
        },
    )
    execution_cache_path: str = dc.field(
        default="",  # No default, so that sphinx can set it inside outdir, if empty
        metadata={
            "validator": instance_of(str),
            "help": "Path to folder for caching notebooks (default: <outdir>)",
            "legacy_name": "jupyter_cache",
            "sections": (Section.global_lvl, Section.file_lvl, Section.execute),
        },
    )
    execution_excludepatterns: Sequence[str] = dc.field(
        default=(),
        metadata={
            "validator": deep_iterable(instance_of(str)),
            "help": "Exclude (POSIX) glob patterns for notebooks",
            "legacy_name": "execution_excludepatterns",
            "omit": ["docutils"],
            "sections": (Section.global_lvl, Section.execute),
        },
    )
    execution_timeout: int = dc.field(
        default=30,
        metadata={
            "validator": instance_of(int),
            "help": "Execution timeout (seconds)",
            "legacy_name": "execution_timeout",
            "sections": (Section.global_lvl, Section.file_lvl, Section.execute),
        },
    )
    execution_in_temp: bool = dc.field(
        default=False,
        metadata={
            "validator": instance_of(bool),
            "help": "Use temporary folder for the execution current working directory",
            "legacy_name": "execution_in_temp",
            "sections": (Section.global_lvl, Section.file_lvl, Section.execute),
        },
    )
    execution_allow_errors: bool = dc.field(
        default=False,
        metadata={
            "validator": instance_of(bool),
            "help": "Allow errors during execution",
            "legacy_name": "execution_allow_errors",
            "sections": (Section.global_lvl, Section.file_lvl, Section.execute),
        },
    )
    execution_raise_on_error: bool = dc.field(
        default=False,
        metadata={
            "validator": instance_of(bool),
            "help": "Raise an exception on failed execution, "
            "rather than emitting a warning",
            "sections": (Section.global_lvl, Section.file_lvl, Section.execute),
        },
    )
    execution_show_tb: bool = dc.field(
        default=False,
        metadata={
            "validator": instance_of(bool),
            "help": "Print traceback to stderr on execution error",
            "legacy_name": "execution_show_tb",
            "sections": (Section.global_lvl, Section.file_lvl, Section.execute),
        },
    )

    # pre-processing options

    merge_streams: bool = dc.field(
        default=False,
        metadata={
            "validator": instance_of(bool),
            "help": "Merge stdout/stderr execution output streams",
            "sections": (
                Section.global_lvl,
                Section.file_lvl,
                Section.cell_lvl,
                Section.render,
            ),
        },
    )

    # render options

    render_plugin: str = dc.field(
        default="default",
        metadata={
            "validator": instance_of(str),
            "help": "The entry point for the execution output render class "
            "(in group `myst_nb.output_renderer`)",
            "sections": (Section.global_lvl, Section.file_lvl, Section.render),
        },
    )
    remove_code_source: bool = dc.field(
        default=False,
        metadata={
            "validator": instance_of(bool),
            "help": "Remove code cell source",
            "sections": (
                Section.global_lvl,
                Section.file_lvl,
                Section.cell_lvl,
                Section.render,
            ),
        },
    )
    remove_code_outputs: bool = dc.field(
        default=False,
        metadata={
            "validator": instance_of(bool),
            "help": "Remove code cell outputs",
            "sections": (
                Section.global_lvl,
                Section.file_lvl,
                Section.cell_lvl,
                Section.render,
            ),
        },
    )

    code_prompt_show: str = dc.field(
        default="Show code cell {type}",
        metadata={
            "validator": instance_of(str),
            "help": "Prompt to expand hidden code cell {content|source|outputs}",
            "sections": (
                Section.global_lvl,
                Section.file_lvl,
                Section.cell_lvl,
                Section.render,
            ),
        },
    )

    code_prompt_hide: str = dc.field(
        default="Hide code cell {type}",
        metadata={
            "validator": instance_of(str),
            "help": "Prompt to collapse hidden code cell {content|source|outputs}",
            "sections": (
                Section.global_lvl,
                Section.file_lvl,
                Section.cell_lvl,
                Section.render,
            ),
        },
    )

    number_source_lines: bool = dc.field(
        default=False,
        metadata={
            "validator": instance_of(bool),
            "help": "Number code cell source lines",
            "sections": (
                Section.global_lvl,
                Section.file_lvl,
                Section.cell_lvl,
                Section.render,
            ),
        },
    )
    # we cannot directly obtain a sphinx builder name from docutils,
    # so must set it manually
    builder_name: str = dc.field(
        default="html",
        metadata={
            "validator": instance_of(str),
            "help": "Builder name, to select render priority for mime types",
            "sphinx_exclude": True,
        },
        repr=False,
    )
    mime_priority_overrides: Sequence[Tuple[str, str, Optional[int]]] = dc.field(
        default=(),
        metadata={
            "validator": deep_iterable(
                has_items(
                    instance_of(str), instance_of(str), optional(instance_of(int))
                ),
            ),
            "help": "Overrides for the base render priority of mime types: "
            "list of (builder name, mime type, priority)",
            # TODO how to allow this in docutils?
            "omit": ["docutils"],
            "sections": (Section.global_lvl, Section.file_lvl, Section.render),
        },
        repr=False,
    )
    output_stderr: Literal[
        "show", "remove", "remove-warn", "warn", "error", "severe"
    ] = dc.field(
        default="show",
        metadata={
            "validator": in_(
                [
                    "show",
                    "remove",
                    "remove-warn",
                    "warn",
                    "error",
                    "severe",
                ]
            ),
            "help": "Behaviour for stderr output",
            "sections": (
                Section.global_lvl,
                Section.file_lvl,
                Section.cell_lvl,
                Section.render,
            ),
        },
    )
    render_text_lexer: str = dc.field(
        default="myst-ansi",
        # TODO allow None -> "none"?
        # TODO check it can be loaded?
        metadata={
            "validator": optional(instance_of(str)),
            "help": "Pygments lexer applied to stdout/stderr and text/plain outputs",
            "cell_key": "text_lexer",
            "sections": (
                Section.global_lvl,
                Section.file_lvl,
                Section.cell_lvl,
                Section.render,
            ),
        },
    )
    render_error_lexer: str = dc.field(
        default="ipythontb",
        # TODO allow None -> "none"?
        # TODO check it can be loaded?
        metadata={
            "validator": optional(instance_of(str)),
            "help": "Pygments lexer applied to error/traceback outputs",
            "cell_key": "error_lexer",
            "sections": (
                Section.global_lvl,
                Section.file_lvl,
                Section.cell_lvl,
                Section.render,
            ),
        },
    )
    render_image_options: Dict[str, str] = dc.field(
        default_factory=dict,
        # see https://docutils.sourceforge.io/docs/ref/rst/directives.html#image
        metadata={
            "validator": deep_mapping(instance_of(str), instance_of((str, int))),
            "help": "Options for image outputs (class|alt|height|width|scale|align)",
            "omit": ["docutils"],
            # TODO backward-compatible change to "image_options"?
            "cell_key": "image",
            "sections": (
                Section.global_lvl,
                Section.file_lvl,
                Section.cell_lvl,
                Section.render,
            ),
        },
    )
    render_figure_options: Dict[str, str] = dc.field(
        default_factory=dict,
        # see https://docutils.sourceforge.io/docs/ref/rst/directives.html#figure
        metadata={
            "validator": deep_mapping(instance_of(str), instance_of((str, int))),
            "help": "Options for figure outputs (classes|name|caption|caption_before)",
            "omit": ["docutils"],
            "cell_key": "figure",
            "sections": (
                Section.global_lvl,
                Section.file_lvl,
                Section.cell_lvl,
                Section.render,
            ),
        },
    )
    render_markdown_format: Literal["commonmark", "gfm", "myst"] = dc.field(
        default="commonmark",
        metadata={
            "validator": in_(["commonmark", "gfm", "myst"]),
            "help": "The format to use for text/markdown rendering",
            "cell_key": "markdown_format",
            "sections": (
                Section.global_lvl,
                Section.file_lvl,
                Section.cell_lvl,
                Section.render,
            ),
        },
    )
    # TODO jupyter_sphinx_require_url and jupyter_sphinx_embed_url (undocumented),
    # are no longer used by this package, replaced by ipywidgets_js
    # do we add any deprecation warnings?
    ipywidgets_js: Dict[str, Dict[str, str]] = dc.field(
        default_factory=ipywidgets_js_factory,
        metadata={
            "validator": deep_mapping(
                instance_of(str), deep_mapping(instance_of(str), instance_of(str))
            ),
            "help": "Javascript to be loaded on pages containing ipywidgets",
            "omit": ["docutils"],
            "sections": (Section.global_lvl, Section.render),
        },
        repr=False,
    )

    # write options for docutils
    output_folder: str = dc.field(
        default="build",
        metadata={
            "validator": instance_of(str),
            "help": "Folder for external outputs (like images), skipped if empty",
            "sphinx_exclude": True,  # in sphinx we always output to the build folder
        },
    )
    append_css: bool = dc.field(
        default=True,
        metadata={
            "validator": instance_of(bool),
            "help": "Add default MyST-NB CSS to HTML outputs",
            "sphinx_exclude": True,
        },
    )
    metadata_to_fm: bool = dc.field(
        default=False,
        metadata={
            "validator": instance_of(bool),
            "help": "Convert unhandled metadata to frontmatter",
            "sphinx_exclude": True,
        },
    )

    @classmethod
    def get_fields(cls) -> Tuple[dc.Field, ...]:
        return dc.fields(cls)

    def as_dict(self, dict_factory=dict) -> dict:
        return dc.asdict(self, dict_factory=dict_factory)

    def as_triple(self) -> Iterable[Tuple[str, Any, dc.Field]]:
        """Yield triples of (name, value, field)."""
        fields = {f.name: f for f in dc.fields(self.__class__)}
        for name, value in dc.asdict(self).items():
            yield name, value, fields[name]

    def copy(self, **changes) -> "NbParserConfig":
        """Return a copy of the configuration with optional changes applied."""
        return dc.replace(self, **changes)

    def __getitem__(self, field: str) -> Any:
        """Get a field value by name."""
        if field in ("get_fields", "as_dict", "as_triple", "copy"):
            raise KeyError(field)
        try:
            return getattr(self, field)
        except AttributeError:
            raise KeyError(field)

    def get_cell_level_config(
        self,
        field_name: str,
        cell_metadata: Dict[str, Any],
        warning_callback: Callable[[str, MystNBWarnings], Any],
    ) -> Any:
        """Get a configuration value at the cell level.

        Takes the highest priority configuration from:
        `cell > document > global > default`

        :param field: the field name to get the value for
        :param cell_metadata: the metadata for the cell
        :param warning_callback: a callback to use to warn about issues (msg, subtype)

        :raises KeyError: if the field is not found
        """
        field: dc.Field = self.__dataclass_fields__[field_name]

        cell_key = field.metadata.get("cell_key", field.name)

        if (
            self.cell_metadata_key not in cell_metadata
            and "render" in cell_metadata
            and isinstance(cell_metadata["render"], dict)
            and cell_key in cell_metadata["render"]
        ):
            warning_callback(
                f"Deprecated `cell_metadata_key` 'render' "
                f"found, replace with {self.cell_metadata_key!r}",
                MystNBWarnings.CELL_METADATA_KEY,
            )
            cell_meta = cell_metadata["render"]
        else:
            cell_meta = cell_metadata.get(self.cell_metadata_key, None)

        if cell_meta:
            try:
                if cell_key in cell_meta:
                    value = cell_meta[cell_key]
                    if "validator" in field.metadata:
                        if isinstance(field.metadata["validator"], list):
                            for validator in field.metadata["validator"]:
                                validator(self, field, value)
                        else:
                            field.metadata["validator"](self, field, value)
                    return value
            except Exception as exc:
                warning_callback(
                    f"Cell metadata invalid: {exc}",
                    MystNBWarnings.CELL_CONFIG,
                )

        # default/global/file level should have already been merged
        return getattr(self, field.name)
