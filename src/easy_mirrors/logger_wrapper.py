# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

from __future__ import annotations

import logging
import logging.config

__all__ = ["setup"]


def setup(level: int = logging.INFO) -> None:
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
                    "level": level,
                },
            },
            "version": 1,
        }
    )
