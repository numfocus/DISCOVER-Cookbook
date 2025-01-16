"""Shared utilities."""
from __future__ import annotations

import re

from nbformat import NotebookNode

_RGX_CARRIAGERETURN = re.compile(r".*\r(?=[^\n])")
_RGX_BACKSPACE = re.compile(r"[^\n]\b")


def coalesce_streams(outputs: list[NotebookNode]) -> list[NotebookNode]:
    """Merge all stream outputs with shared names into single streams.

    This ensure deterministic outputs.

    Adapted from:
    https://github.com/computationalmodelling/nbval/blob/master/nbval/plugin.py.
    """
    if not outputs:
        return []

    new_outputs = []
    streams: dict[str, NotebookNode] = {}
    for output in outputs:
        if output["output_type"] == "stream":
            if output["name"] in streams:
                out = output["text"].strip()
                if out:
                    streams[output["name"]]["text"] += f"{out}\n"
            else:
                output["text"] = output["text"].strip() + "\n"
                new_outputs.append(output)
                streams[output["name"]] = output
        else:
            new_outputs.append(output)

    # process \r and \b characters
    for output in streams.values():
        old = output["text"]
        while len(output["text"]) < len(old):
            old = output["text"]
            # Cancel out anything-but-newline followed by backspace
            output["text"] = _RGX_BACKSPACE.sub("", output["text"])
        # Replace all carriage returns not followed by newline
        output["text"] = _RGX_CARRIAGERETURN.sub("", output["text"])

    # We also want to ensure stdout and stderr are always in the same consecutive order,
    # because they are asynchronous, so order isn't guaranteed.
    for i, output in enumerate(new_outputs):
        if output["output_type"] == "stream" and output["name"] == "stderr":
            if (
                len(new_outputs) >= i + 2
                and new_outputs[i + 1]["output_type"] == "stream"
                and new_outputs[i + 1]["name"] == "stdout"
            ):
                stdout = new_outputs.pop(i + 1)
                new_outputs.insert(i, stdout)

    return new_outputs
