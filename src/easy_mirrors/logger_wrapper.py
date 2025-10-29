# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

from __future__ import annotations

import logging
import logging.config
import os
import typing

__all__ = ["setup"]


def setup(level: str = "INFO") -> None:
    """Sets up the logging system for the application."""
    logging.config.dictConfig(
        {
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(levelname)s :: %(name)s :: %(message)s",
                },
            },
            "handlers": {
                "stderr": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stderr",
                },
            },
            "loggers": {
                "easy_mirrors": {
                    "handlers": ["stderr"],
                    "level": typing.cast(
                        int,
                        {
                            "CRITICAL": logging.CRITICAL,
                            "ERROR": logging.ERROR,
                            "WARNING": logging.WARNING,
                            "INFO": logging.INFO,
                            "DEBUG": logging.DEBUG,
                            "NOTSET": logging.NOTSET,
                        }.get(
                            os.environ.get("EASY_MIRRORS_LOGGER_LEVEL", level).upper()
                        ),
                    ),
                },
            },
            "version": 1,
        }
    )
