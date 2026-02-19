#!/usr/bin/env python3

# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

from __future__ import annotations

import argparse
import errno
import logging
import os
import sys
import time
import typing

from easy_mirrors import api, config, defaults, exceptions, logger_wrapper

logger = logging.getLogger("easy_mirrors")


class ArgumentsNamespace(argparse.Namespace):
    """Typed namespace representing all supported CLI parameters."""

    config_path: str
    synchronization_period: int
    verbosity: str


def main() -> typing.NoReturn:
    parser = argparse.ArgumentParser(
        description="Simplest way to mirror and restore git repositories."
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        type=str.upper,
        metavar="LEVEL",
        choices=[
            "CRITICAL",
            "ERROR",
            "WARNING",
            "INFO",
            "DEBUG",
            "NOTSET",
        ],
        default="INFO",
        dest="verbosity",
        help="select the logging level to determine which messages are displayed",
    )
    parser.add_argument(
        "-p",
        "--period",
        type=int,
        metavar="MINUTES",
        default=1440,  # 24 * 60
        dest="synchronization_period",
        help="synchronization period in minutes (default: once per day)",
    )
    parser.add_argument(
        "-c",
        "--config-path",
        type=str,
        metavar="PATH",
        default=defaults.CONFIG_PATH,
        dest="config_path",
        help="the local path to a configuration file",
    )
    try:
        arguments = parser.parse_args(namespace=ArgumentsNamespace())

        # Assign a new severity level to the logging system.
        logger_wrapper.setup(arguments.verbosity)

        configuration = config.Config.load(
            path=os.path.normpath(os.path.expanduser(arguments.config_path))
        )
        logger.info(configuration)

        while True:
            api.make_mirrors(configuration)

            logger.info("Next attempt: %d minute(s)", arguments.synchronization_period)
            time.sleep(arguments.synchronization_period * 60)
    except (
        exceptions.ConfigError,
        exceptions.ExternalProcessError,
        exceptions.FileSystemError,
    ) as err:
        logger.debug(
            "An unexpected error occurred at this program runtime:", exc_info=True
        )
        # Stop this program runtime and return the exit status code.
        sys.exit(getattr(err, "errno", errno.EPERM))

    except KeyboardInterrupt:
        logger.info(
            "Abort this program runtime as a consequence of a keyboard interrupt."
        )
        # Terminate the execution of this program due to a keyboard interruption.
        sys.exit(os.EX_OK)

    finally:
        # Exit without errors.
        sys.exit(os.EX_OK)


if __name__ == "__main__":
    main()
