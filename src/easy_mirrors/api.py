# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

from __future__ import annotations

import logging
import os

from easy_mirrors import config, git_repository

__all__ = ["make_mirrors"]

logger = logging.getLogger("easy_mirrors")


def make_mirrors(configuration: config.Config) -> None:
    """Clones or updates mirrored git repositories based on configuration."""
    for url in configuration.repositories:
        logger.info("Mirroring repository: %s", url)

        repository = git_repository.GitRepository.from_url(
            parent_path=configuration.path, url=url
        )
        logger.debug(repr(repository))

        if not repository.exists_on_remote():
            logger.warning("The remote repository does not exist: %s", url)

            continue

        if repository.exists_locally():
            repository.update_local_copy()  # git fetch
        else:
            if os.path.isdir(repository.local_path):
                logger.warning(
                    "Non-mirror repository detected at path: %s", repository.local_path
                )
                logger.warning("Skipping cloning.")

                continue

            repository.create_local_copy()  # git clone
            repository.update_local_copy()  # git fetch -> FETCH_HEAD
