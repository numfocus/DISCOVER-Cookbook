"""Compatibility for using dataclasses instead of attrs."""
from __future__ import annotations

import dataclasses as dc
import re
import sys
from typing import Any, Callable, Pattern, Type

from docutils.nodes import Element

if sys.version_info >= (3, 10):
    DC_SLOTS: dict = {"slots": True}
else:
    DC_SLOTS: dict = {}


def field(**kwargs: Any):
    if sys.version_info < (3, 10):
        kwargs.pop("kw_only", None)
    if "validator" in kwargs:
        kwargs.setdefault("metadata", {})["validator"] = kwargs.pop("validator")
    return dc.field(**kwargs)


field.__doc__ = dc.field.__doc__


def validate_fields(inst):
    """Validate the fields of a dataclass,
    according to `validator` functions set in the field metadata.

    This function should be called in the `__post_init__` of the dataclass.

    The validator function should take as input (inst, field, value) and
    raise an exception if the value is invalid.
    """
    for field in dc.fields(inst):
        if "validator" not in field.metadata:
            continue
        if isinstance(field.metadata["validator"], list):
            for validator in field.metadata["validator"]:
                validator(inst, field, getattr(inst, field.name))
        else:
            field.metadata["validator"](inst, field, getattr(inst, field.name))


ValidatorType = Callable[[Any, dc.Field, Any], None]


def instance_of(type: Type[Any] | tuple[Type[Any], ...]) -> ValidatorType:
    """
    A validator that raises a `TypeError` if the initializer is called
    with a wrong type for this particular attribute (checks are performed using
    `isinstance` therefore it's also valid to pass a tuple of types).

    :param type: The type to check for.
    """

    def _validator(inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if not isinstance(value, type):
            raise TypeError(
                f"'{attr.name}' must be {type!r} (got {value!r} that is a {value.__class__!r})."
            )

    return _validator


def matches_re(regex: str | Pattern, flags: int = 0) -> ValidatorType:
    r"""
    A validator that raises `ValueError` if the initializer is called
    with a string that doesn't match *regex*.

    :param regex: a regex string or precompiled pattern to match against
    :param flags: flags that will be passed to the underlying re function (default 0)

    """
    fullmatch = getattr(re, "fullmatch", None)

    if isinstance(regex, Pattern):
        if flags:
            raise TypeError(
                "'flags' can only be used with a string pattern; "
                "pass flags to re.compile() instead"
            )
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if fullmatch:
        match_func = pattern.fullmatch
    else:  # Python 2 fullmatch emulation (https://bugs.python.org/issue16203)
        pattern = re.compile(r"(?:{})\Z".format(pattern.pattern), pattern.flags)
        match_func = pattern.match

    def _validator(inst, attr, value):
        if not match_func(value):
            raise ValueError(
                f"'{attr.name}' must match regex {pattern!r} ({value!r} doesn't)"
            )

    return _validator


def optional(validator: ValidatorType) -> ValidatorType:
    """
    A validator that makes an attribute optional.  An optional attribute is one
    which can be set to ``None`` in addition to satisfying the requirements of
    the sub-validator.
    """

    def _validator(inst, attr, value):
        if value is None:
            return

        validator(inst, attr, value)

    return _validator


def deep_iterable(
    member_validator: ValidatorType, iterable_validator: ValidatorType | None = None
) -> ValidatorType:
    """
    A validator that performs deep validation of an iterable.

    :param member_validator: Validator to apply to iterable members
    :param iterable_validator: Validator to apply to iterable itself
    """

    def _validator(inst, attr, value):
        if iterable_validator is not None:
            iterable_validator(inst, attr, value)

        for member in value:
            member_validator(inst, attr, member)

    return _validator


# Docutils compatibility


def findall(node: Element):
    # findall replaces traverse in docutils v0.18
    # note a difference is that findall is an iterator
    return getattr(node, "findall", node.traverse)
