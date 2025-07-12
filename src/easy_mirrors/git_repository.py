# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

from __future__ import annotations

import configparser
import json
import logging
import os
import shlex
import subprocess  # nosec
import typing

from easy_mirrors import exceptions

logger = logging.getLogger("easy_mirrors")

__all__ = ["GitRepository"]

_T = typing.TypeVar("_T", bound="GitRepository")


def _get_repository_name(url: str) -> str:
    """Returns the name of a particular repository specified by its url.

    Parameters
    ----------
    url : str
        The repository url.

    Returns
    -------
    str
        The extracted repository name.
    """
    name = url.rstrip("/").split("/").pop()

    return name if name.endswith(".git") else f"{name}.git"


def _run_git_command(cmd: str, /, cwd: str | None = None, silent: bool = False) -> None:
    """Executes the provided git command in a new process.

    This function is required to run the specified git command in a controlled
    environment to avoid authentication prompts interfering with execution.
    In silent mode, no output is generated during its execution.

    Parameters
    ----------
    cmd : str
        The git command to execute. It should look like a normal shell command.

    cwd : str, optional
        The working directory in which to run the command. The command will be
        executed in the current working directory unless a path is provided.

    silent : bool, default=False
        Suppresses stdout and stderr output during execution when enabled.

    Raises
    ------
    ExternalProcessError
        Raised when the git command execution fails.
    """
    env: dict[str, str] = {
        "TERM": "dump",
        # Disable the prompting of the git credential helper and avoids blocking
        # when the user is required to enter authentication credentials.
        "GIT_TERMINAL_PROMPT": "0",
    }
    env.update(os.environ)

    stdout = stderr = subprocess.DEVNULL if silent else None  # streams
    try:
        subprocess.check_call(  # nosec
            shlex.split(cmd),
            cwd=cwd,
            env=env,
            shell=False,
            stderr=stderr,
            stdout=stdout,
        )
    except subprocess.CalledProcessError as err:
        if not silent:
            logger.error(
                "An error occurred on while attempting to execute the command."
            )
        raise exceptions.ExternalProcessError(
            f"Failed to execute the command: {cmd!s}."
        ) from err


class GitRepository:
    """Represents a git repository with local and remote references.

    Attributes
    ----------
    local_path : str
        The local directory where the repository is stored.

    url : str
        The remote repository url.
    """

    def __init__(self, local_path: str, url: str) -> None:
        self.local_path = local_path
        self.url = url

    @classmethod
    def from_url(cls: type[_T], parent_path: str, url: str) -> _T:
        """Creates a repository instance from its remote url.

        This method initializes a repository object using only the remote
        repository url and a parent directory path on the local machine. The
        repository's local path is determined automatically based on its name.

        Parameters
        ----------
        parent_path : str
            The directory where the repository should be stored locally.

        url : str
            The remote repository url.

        Returns
        -------
        Repository
            A new instance of the repository class with the computed local path.
        """
        return cls(
            local_path=os.path.join(
                os.path.expanduser(parent_path), _get_repository_name(url)
            ),
            url=url,
        )

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def __repr__(self) -> str:
        """Returns string representation of an instance for debugging."""

        return (
            f"{self.__class__.__name__!s}"
            f"(local_path={str(self.local_path)!r}, url={self.url!r})"
        )

    def to_dict(self) -> dict[str, str]:
        return vars(self)

    def create_local_copy(self) -> None:
        """Clones a mirrored copy of the repository onto the local machine.

        This method creates a local mirror of the repository, providing the most
        efficient way to back up a git repository while optimizing storage. It retains
        all branches, tags, and references while significantly reducing disk space.

        Raises
        ------
        ExternalProcessError
            If the cloning process fails or the repository cannot be fetched.
        """
        _run_git_command(
            "git clone --mirror --no-hardlinks -- {0!r} {1!r}".format(
                self.url, str(self.local_path)
            )
        )

    def exists_locally(self) -> bool:
        """Determines whether the repository exists locally.

        This method verifies if the repository is present at the specified local
        path and is a valid git repository.

        Returns
        -------
        bool
            True if the repository is present locally, otherwise false.
        """
        if not os.path.isdir(self.local_path):
            return False

        for component_name in {
            "config",  # repository configurations
            "objects",
            "refs",
            "HEAD",  # holds reference to the checked-out branch's commit
        }:
            if not os.path.exists(os.path.join(self.local_path, component_name)):
                return False

        config_parser = configparser.ConfigParser()
        config_parser.read(os.path.join(self.local_path, "config"))

        # Check each remote section for a matching url.
        for section in (
            section
            for section in config_parser.sections()
            if section.startswith("remote")
        ):
            if config_parser[section].get("url", "").strip() == self.url.strip():
                return config_parser.getboolean(section, "mirror", fallback=False)

        return False

    def exists_on_remote(self) -> bool:
        """Determines whether the repository exists on the remote server.

        This method verifies if the repository is accessible at the given remote url.

        Returns
        -------
        bool
            True if the repository exists on the remote server, otherwise false.
        """
        try:
            _run_git_command(
                "git ls-remote --exit-code -- {0!r}".format(self.url), silent=True
            )
        except exceptions.ExternalProcessError:
            return False

        return True

    def update_local_copy(self) -> None:
        """Fetchs the latest updates from the remote repository.

        This method synchronizes the local repository with the remote.

        Raises
        ------
        ExternalProcessError
            If fetching updates from the remote repository fails.
        """
        _run_git_command("git fetch --all --prune --verbose", cwd=self.local_path)
