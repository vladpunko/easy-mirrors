# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

from __future__ import annotations

import pathlib
import typing

__all__ = ["CONFIG_PATH"]

CONFIG_PATH: typing.Final[pathlib.Path] = pathlib.Path.home() / "easy_mirrors.ini"
