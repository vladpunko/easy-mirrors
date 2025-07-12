# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

import logging
import os

import pytest

from easy_mirrors import api


@pytest.fixture
def config_mock(mocker):
    config = mocker.Mock()
    config.path = "/root/"
    config.repositories = [
        "1.git",
    ]

    return config


@pytest.fixture
def repository_mock(mocker):
    repository = mocker.Mock()
    repository.local_path = "/root/"

    return repository


@pytest.fixture
def git_repository_mock(mocker):
    return mocker.patch("easy_mirrors.api.git_repository.GitRepository")


def test_existing_remote_and_local_repository(
    caplog, config_mock, repository_mock, git_repository_mock
):
    repository_mock.exists_locally.return_value = True
    repository_mock.exists_on_remote.return_value = True

    git_repository_mock.from_url.return_value = repository_mock

    with caplog.at_level(logging.INFO):
        api.make_mirrors(config_mock)

    for url in config_mock.repositories:
        message = "Mirroring repository: {0!s}.".format(url)
        assert message in caplog.text

        repository_mock.create_local_copy.assert_not_called()
        repository_mock.update_local_copy.assert_called_once()


def test_existing_remote_not_local(
    fs, config_mock, repository_mock, git_repository_mock
):
    repository_mock.exists_locally.return_value = False
    repository_mock.exists_on_remote.return_value = True

    git_repository_mock.from_url.return_value = repository_mock

    api.make_mirrors(config_mock)

    repository_mock.create_local_copy.assert_called_once()
    repository_mock.update_local_copy.assert_called_once()


def test_existing_remote_path_is_non_mirror_directory(
    caplog, fs, config_mock, repository_mock, git_repository_mock
):
    os.mkdir(repository_mock.local_path)

    repository_mock.exists_locally.return_value = False
    repository_mock.exists_on_remote.return_value = True

    git_repository_mock.from_url.return_value = repository_mock

    with caplog.at_level(logging.WARNING):
        api.make_mirrors(config_mock)

    assert "Non-mirror repository detected at path:" in caplog.text
    assert "Skipping cloning." in caplog.text

    repository_mock.create_local_copy.assert_not_called()
    repository_mock.update_local_copy.assert_not_called()


def test_remote_repository_does_not_exist(
    caplog, config_mock, repository_mock, git_repository_mock
):
    repository_mock.exists_on_remote.return_value = False

    git_repository_mock.from_url.return_value = repository_mock

    with caplog.at_level(logging.WARNING):
        api.make_mirrors(config_mock)

    assert "The remote repository does not exist:" in caplog.text

    repository_mock.exists_locally.assert_not_called()
    repository_mock.create_local_copy.assert_not_called()
    repository_mock.update_local_copy.assert_not_called()
