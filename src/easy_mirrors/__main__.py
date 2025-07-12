#!/usr/bin/env python3

# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

from __future__ import annotations

import argparse
import errno
import logging
import sys
import time
import typing
from importlib.metadata import version

from easy_mirrors import api, config, defaults, exceptions

logger = logging.getLogger("easy_mirrors")


def main() -> typing.NoReturn:
    parser = argparse.ArgumentParser(
        description="Simplest way to mirror and restore git repositories."
    )
    parser.add_argument(
        "-v", "--version", action="version", version=version("easy_mirrors")
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=logging.DEBUG,  # level must be an int or a str
        default=logging.INFO,
        dest="logging_level",
        help="generate extensive debugging output during command execution",
    )
    parser.add_argument(
        "-p",
        "--period",
        type=int,
        default=1440,  # 24 * 60
        metavar="MINUTES",
        dest="synchronization_period",
        help="synchronization period in minutes (default: once per day)",
    )
    try:
        arguments = vars(parser.parse_args())

        # Assign a new severity level to the logging system.
        logger.setLevel(arguments["logging_level"])

        # Step -- 1.
        configuration = config.Config.load(path=defaults.CONFIG_PATH)
        logger.info(configuration)

        # Step -- 2.
        while True:
            api.make_mirrors(configuration)

            logger.info(
                "Next attempt: %d minute(s).", arguments["synchronization_period"]
            )
            time.sleep(arguments["synchronization_period"] * 60)
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
        sys.exit(0)


if __name__ == "__main__":
    main()
