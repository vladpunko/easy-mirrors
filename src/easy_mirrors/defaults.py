# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

from __future__ import annotations

import os
import typing

__all__ = ["CONFIG_PATH"]

CONFIG_PATH: typing.Final[str] = os.path.join(
    os.path.expanduser("~"), "easy_mirrors.ini"
)
