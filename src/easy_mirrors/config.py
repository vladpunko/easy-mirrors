# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

from __future__ import annotations

import configparser
import dataclasses
import json
import logging
import pathlib
import re
import typing

from easy_mirrors import exceptions, fields

logger = logging.getLogger("easy_mirrors")

__all__ = ["Config"]

_T = typing.TypeVar("_T", bound="Config")


@dataclasses.dataclass(frozen=True)
class Config:
    """Configuration for local repository mirroring.

    This configuration class is immutable and holds the local mirror path along
    with a list of remote repository urls to mirror.

    Attributes
    ----------
    path : str or pathlib.Path
        The local root directory where mirrored repositories will be stored.

    repositories : list[str]
        A list of remote repository urls to be mirrored.
    """

    section: typing.ClassVar[str] = "easy_mirrors"

    path: pathlib.Path = dataclasses.field(default=fields.PathField())  # type: ignore
    repositories: list[str] = dataclasses.field(
        default=fields.SequenceField()  # type: ignore
    )

    @classmethod
    def load(cls: type[_T], path: str | pathlib.Path) -> _T:
        """Factory method to create a new configuration instance.

        Parameters
        ----------
        path : str or pathlib.Path
            The local path to the configurations.

        Returns
        -------
        Config
            A populated instance of the configuration class.

        Raises
        ------
        ConfigError
            Raised when the configuration is malformed or does not match the
            expected schema.

        FileSystemError
            Raised when the local path cannot be accessed due to input or output errors.
        """
        config_parser = configparser.ConfigParser()
        try:
            with pathlib.Path(path).expanduser().open(encoding="utf-8") as stream_in:
                config_parser.read_file(stream_in)
        except OSError as err:
            logger.error(
                "Unable to access the configuration file at the specified location."
            )
            raise exceptions.FileSystemError(
                f"Unable to load configurations from the specified path: {str(path)!s}."
            ) from err

        except configparser.Error as err:
            logger.error(
                "The provided configuration contains syntax errors or missing fields."
            )
            raise exceptions.ConfigError(
                f"Invalid or unreadable configurations at path: {str(path)!s}."
            ) from err

        logger.debug(dict(config_parser[cls.section]))

        # Ensure that the configurations conform to the expected schema.
        if not all(
            config_parser.has_option(cls.section, name)
            for name in {"path", "repositories"}
        ):
            raise exceptions.ConfigError("File does not match expected schema.")

        return cls(
            path=config_parser.get(cls.section, "path"),  # type: ignore
            repositories=[
                url
                for item in re.split(
                    r"[^\w:/@.-]+", config_parser.get(cls.section, "repositories")
                )
                if (url := item.strip())
            ],
        )

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), default=str, indent=2)  # serialize

    def __repr__(self) -> str:
        """Returns string representation of an instance for debugging."""

        return (
            f"{self.__class__.__name__!s}"
            f"(path={str(self.path)!r}, repositories={self.repositories!s})"
        )

    def to_dict(self) -> dict[str, pathlib.Path | list[str]]:
        return dataclasses.asdict(self)
