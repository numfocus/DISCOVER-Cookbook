"""Pygments lexers"""
from __future__ import annotations

import re

# this is not added as an entry point in ipython, so we add it in this package
from IPython.lib.lexers import IPythonTracebackLexer  # noqa: F401
import pygments.lexer
import pygments.token

_ansi_code_to_color = {
    0: "Black",
    1: "Red",
    2: "Green",
    3: "Yellow",
    4: "Blue",
    5: "Magenta",
    6: "Cyan",
    7: "White",
}


def _token_from_lexer_state(
    bold: bool, faint: bool, fg_color: str | None, bg_color: str | None
):
    """Construct a token given the current lexer state.

    We can only emit one token even though we have a multiple-tuple state.
    To do work around this, we construct tokens like "Bold.Red".
    """
    components: tuple[str, ...] = ()

    if bold:
        components += ("Bold",)

    if faint:
        components += ("Faint",)

    if fg_color:
        components += (fg_color,)

    if bg_color:
        components += ("BG" + bg_color,)

    if len(components) == 0:
        return pygments.token.Text
    else:
        token = pygments.token.Token.Color
        for component in components:
            token = getattr(token, component)
        return token


class AnsiColorLexer(pygments.lexer.RegexLexer):
    """Pygments lexer for text containing ANSI color codes.

    Adapted from https://github.com/chriskuehl/pygments-ansi-color
    """

    name = "ANSI Color"
    aliases = ("myst-ansi",)
    flags = re.DOTALL | re.MULTILINE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset_state()

    def reset_state(self):
        self.bold = False
        self.faint = False
        self.fg_color = None
        self.bg_color = None

    @property
    def current_token(self):
        return _token_from_lexer_state(
            self.bold,
            self.faint,
            self.fg_color,
            self.bg_color,
        )

    def process(self, match):
        """Produce the next token and bit of text.

        Interprets the ANSI code (which may be a color code or some other
        code), changing the lexer state and producing a new token. If it's not
        a color code, we just strip it out and move on.

        Some useful reference for ANSI codes:
          * http://ascii-table.com/ansi-escape-sequences.php
        """
        # "after_escape" contains everything after the start of the escape
        # sequence, up to the next escape sequence. We still need to separate
        # the content from the end of the escape sequence.
        after_escape = match.group(1)

        # TODO: this doesn't handle the case where the values are non-numeric.
        # This is rare but can happen for keyboard remapping, e.g.
        # '\x1b[0;59;"A"p'
        parsed = re.match(
            r"([0-9;=]*?)?([a-zA-Z])(.*)$",
            after_escape,
            re.DOTALL | re.MULTILINE,
        )
        if parsed is None:
            # This shouldn't ever happen if we're given valid text + ANSI, but
            # people can provide us with utter junk, and we should tolerate it.
            text = after_escape
        else:
            value, code, text = parsed.groups()
            if code == "m":  # "m" is "Set Graphics Mode"
                # Special case \x1b[m is a reset code
                if value == "":
                    self.reset_state()
                else:
                    try:
                        values = [int(v) for v in value.split(";")]
                    except ValueError:
                        # Shouldn't ever happen, but could with invalid ANSI.
                        values = []

                    while len(values) > 0:
                        value = values.pop(0)
                        fg_color = _ansi_code_to_color.get(value - 30)
                        bg_color = _ansi_code_to_color.get(value - 40)
                        if fg_color:
                            self.fg_color = fg_color
                        elif bg_color:
                            self.bg_color = bg_color
                        elif value == 1:
                            self.bold = True
                        elif value == 2:
                            self.faint = True
                        elif value == 22:
                            self.bold = False
                            self.faint = False
                        elif value == 39:
                            self.fg_color = None
                        elif value == 49:
                            self.bg_color = None
                        elif value == 0:
                            self.reset_state()
                        elif value in (38, 48):
                            try:
                                five = values.pop(0)
                                color = values.pop(0)
                            except IndexError:
                                continue
                            else:
                                if five != 5:
                                    continue
                                if not 0 <= color <= 255:
                                    continue
                                if value == 38:
                                    self.fg_color = f"C{color}"
                                else:
                                    self.bg_color = f"C{color}"

        yield match.start(), self.current_token, text

    tokens = {
        "root": [(r"\x1b\[([^\x1b]*)", process), (r"[^\x1b]+", pygments.token.Text)],
    }
