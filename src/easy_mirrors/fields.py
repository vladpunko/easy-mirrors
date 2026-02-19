# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

from __future__ import annotations

import abc
import collections.abc
import os
import typing

from easy_mirrors import exceptions

__all__ = ["PathField", "SequenceField"]

_T = typing.TypeVar("_T")
_V = typing.TypeVar("_V")


class _Field(abc.ABC, typing.Generic[_V, _T]):
    def __set_name__(self, owner: type[typing.Any], name: str) -> None:
        self.name = name

    @typing.no_type_check
    def __get__(self, instance: typing.Any, owner: type[typing.Any]) -> _T:
        if instance is None:
            return self  # pragma: no cover

        return typing.cast(_T, instance.__dict__[self.name])

    def __set__(self, instance: typing.Any, value: _V) -> None:
        instance.__dict__[self.name] = self.process_value(value)

    @abc.abstractmethod
    def process_value(self, value: _V) -> _T:
        """Validates and normalize the value of the field and return it if valid."""
        raise NotImplementedError


class PathField(_Field[str, str]):
    """A specialized field for handling file system path inputs in configurations."""

    def process_value(self, value: str) -> str:
        """Checks the path input for validity and expand it to an absolute format.

        Parameters
        ----------
        value : str
            The input value to process.

        Returns
        -------
        str
            A normalized and user-expanded path object.

        Raises
        ------
        ConfigError
            Raised when the provided value is empty or not a valid path type.
        """
        if not isinstance(value, str):
            raise exceptions.ConfigError(
                f"Path must be string, but received: {type(value).__name__!s}"
            )

        if not value:
            raise exceptions.ConfigError("Path can not be empty.")

        return os.path.expanduser(os.path.normpath(value))


class SequenceField(_Field[typing.Iterable[str], list[str]]):
    """A field that accepts a sequence of strings and normalizes it into a
    sorted list with duplicates removed.
    """

    def process_value(self, value: typing.Iterable[str]) -> list[str]:
        """Validates a sequence of strings and returns a sorted list with
        duplicates removed.

        Parameters
        ----------
        value : Iterable[str]
            A sequence-like input containing only string elements.

        Returns
        -------
        list[str]
            A sorted list of unique strings from the input sequence.

        Raises
        ------
        ConfigError
            Raised when the input is not a valid sequence or
            contains non-string elements.
        """
        if not isinstance(value, collections.abc.Sequence) or isinstance(
            value, (bytes, str)
        ):
            raise exceptions.ConfigError(
                "The data required for a list field must be inputted as a sequence."
            )

        if not all(isinstance(item, str) for item in value):
            raise exceptions.ConfigError("All items in sequence must be strings.")

        return sorted(set(value))  # remove all duplicates
