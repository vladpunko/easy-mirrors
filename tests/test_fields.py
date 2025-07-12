# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

import os

import pytest

from easy_mirrors import exceptions, fields


@pytest.fixture
def configuration():
    class Config:
        path = fields.PathField()
        sequence = fields.SequenceField()

    return Config()


def test_path_field(configuration):
    path = os.path.normpath("~/root")
    configuration.path = path

    assert configuration.path == os.path.expanduser(path)


@pytest.mark.parametrize("path", ("", None, True, [], {}))
def test_validation_error_path_field(configuration, path):
    with pytest.raises(exceptions.ConfigError):
        configuration.path = path


def test_list_field(configuration):
    sequence = ["1", "1", "2", "2", "3", "3"]
    configuration.sequence = sequence

    assert configuration.sequence == sorted(set(sequence))


@pytest.mark.parametrize("sequence", (b"", "", [1, 2, 3], [1, "2", "3"]))
def test_validation_error_sequence_field(sequence, configuration):
    with pytest.raises(exceptions.ConfigError):
        configuration.sequence = sequence
