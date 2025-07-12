# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

import io
import json
import logging
import os

import pytest

from easy_mirrors import config, exceptions

CONFIG_TEMPLATE = """
[easy_mirrors]
    path = {0!s}
    repositories = {1!s}
"""


@pytest.fixture
def path():
    return os.path.normpath("~/root")


@pytest.fixture
def repositories():
    return [
        "1.git",
        "2.git",
        "3.git",
    ]


@pytest.fixture
def configuration_path(fs, path, repositories):
    config_path = os.path.normpath("config.ini")

    with io.open(config_path, mode="wt", encoding="utf-8") as stream_out:
        stream_out.write(CONFIG_TEMPLATE.format(path, "\t".join(repositories)))

    return config_path


@pytest.fixture
def expected_configuration(path, repositories):
    return {"path": os.path.expanduser(path), "repositories": repositories}


def test_config_initialization(expected_configuration, path, repositories):
    configuration = config.Config(path=path, repositories=repositories * 5)

    assert configuration.path == os.path.expanduser(path)
    assert configuration.repositories == repositories  # check deduplication

    assert repr(configuration) == (
        "Config(path={0!r}, repositories={1!s})".format(
            os.path.expanduser(path), repositories
        )
    )
    assert str(configuration) == json.dumps(
        expected_configuration, default=str, indent=2
    )


def test_config_to_dict(expected_configuration, path, repositories):
    configuration = config.Config(path=path, repositories=repositories)

    assert configuration.to_dict() == expected_configuration


@pytest.mark.parametrize(
    "raw_repositories",
    [
        "1.git \t 2.git \t 3.git",
        "1.git \t 2.git;3.git",
        "1.git \t\t 2.git,3.git",
        "1.git,2.git,3.git",
        "1.git;2.git;3.git",
    ],
)
def test_config_load(fs, configuration_path, path, repositories, raw_repositories):
    with io.open(configuration_path, mode="wt", encoding="utf-8") as stream_out:
        stream_out.write(CONFIG_TEMPLATE.format(path, raw_repositories))

    configuration = config.Config.load(configuration_path)

    assert configuration.path == os.path.expanduser(path)
    assert configuration.repositories == repositories


def test_config_load_with_error(caplog, fs, configuration_path):
    os.unlink(configuration_path)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(exceptions.FileSystemError) as error:
            config.Config.load(configuration_path)

    message = "Unable to access the configuration file at the specified location."
    assert message in caplog.text

    message = "Unable to load configurations from the specified path: {0!s}.".format(
        str(configuration_path)
    )
    assert message == str(error.value)


def test_config_load_with_decode_error(caplog, fs, configuration_path):
    with io.open(configuration_path, mode="wt", encoding="utf-8") as stream_out:
        stream_out.write("12345")

    with caplog.at_level(logging.ERROR):
        with pytest.raises(exceptions.ConfigError) as error:
            config.Config.load(configuration_path)

    message = "The provided configuration contains syntax errors or missing fields."
    assert message in caplog.text

    message = "Invalid or unreadable configurations at path: {0!s}.".format(
        str(configuration_path)
    )
    assert message == str(error.value)


def test_validation_during_load_settings(configuration_path):
    with io.open(configuration_path, mode="wt", encoding="utf-8") as stream_out:
        stream_out.write("[easy_mirrors]\n")

    with pytest.raises(exceptions.ConfigError) as error:
        config.Config.load(configuration_path)

    assert str(error.value) == "File does not match expected schema."
