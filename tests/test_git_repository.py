# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

import io
import json
import logging
import os
import shutil

import pytest

from easy_mirrors import exceptions, git_repository

GIT_CONFIG_TEMPLATE = """
[remote "origin"]
    mirror = true
    url = {0!s}
"""


@pytest.fixture
def local_path(fs):
    path = os.path.normpath("root")
    fs.create_dir(path)

    return path


@pytest.fixture
def url():
    return "https://github.com/python/cpython"


@pytest.fixture
def repository(local_path, url):
    return git_repository.GitRepository(local_path=local_path, url=url)


@pytest.fixture
def git_directory(fs, local_path, url):
    fs.create_file(os.path.join(local_path, "HEAD"))

    for path in {"objects", "refs"}:
        fs.create_dir(os.path.join(local_path, path))

    with io.open(
        os.path.join(local_path, "config"), mode="wt", encoding="utf-8"
    ) as stream_out:
        stream_out.write(GIT_CONFIG_TEMPLATE.format(url))


@pytest.fixture
def run_git_command_mock(mocker):
    return mocker.patch("easy_mirrors.git_repository._run_git_command")


def test_repository_string_representation(local_path, url):
    repository = git_repository.GitRepository(local_path=local_path, url=url)

    assert repr(repository) == (
        "GitRepository(local_path={0!r}, url={1!r})".format(str(local_path), url)
    )
    assert str(repository) == json.dumps(repository.to_dict(), indent=2)


def test_repository_to_dict(repository, local_path, url):
    assert repository.to_dict() == {
        "local_path": local_path,
        "url": url,
    }


@pytest.mark.parametrize(
    "url",
    [
        "git@github.com:python/cpython.git",
        "git@github.com:python/cpython",
        "https://github.com/python/cpython.git",
        "https://github.com/python/cpython.git/",
        "https://github.com/python/cpython",
        "https://github.com/python/cpython/",
    ],
)
def test_repository_from_url(local_path, url):
    repository = git_repository.GitRepository.from_url(parent_path=local_path, url=url)

    assert repository.local_path == os.path.join(local_path, "cpython.git")


def test_repository_create_local_copy(
    run_git_command_mock, repository, local_path, url
):
    repository.create_local_copy()

    run_git_command_mock.assert_called_once_with(
        "git clone --mirror --no-hardlinks -- {0!r} {1!r}".format(url, str(local_path))
    )


def test_repository_update_local_copy(run_git_command_mock, repository, local_path):
    repository.update_local_copy()

    run_git_command_mock.assert_called_once_with(
        "git fetch --all --prune --verbose", cwd=local_path
    )


def test_repository_exists_locally(git_directory, repository):
    assert repository.exists_locally() is True


def test_repository_exists_locally_no_sections(git_directory, repository, local_path):
    with io.open(
        os.path.join(local_path, "config"), mode="wt", encoding="utf-8"
    ) as stream_out:
        stream_out.write("")

    assert repository.exists_locally() is False


def test_repository_exists_locally_wrong_url(git_directory, repository, local_path):
    with io.open(
        os.path.join(local_path, "config"), mode="wt", encoding="utf-8"
    ) as stream_out:
        stream_out.write(GIT_CONFIG_TEMPLATE.format("https://google.com"))

    assert repository.exists_locally() is False


def test_repository_not_exists_locally(repository, local_path):
    assert not repository.exists_locally()  # directory exists but not a git repository
    shutil.rmtree(local_path)
    assert not repository.exists_locally()


def test_repository_exists_on_remote(run_git_command_mock, repository, url):
    repository.exists_on_remote()

    run_git_command_mock.assert_called_once_with(
        "git ls-remote --exit-code -- {0!r}".format(url), silent=True
    )


def test_repository_not_exists_on_remote(local_path):
    repository = git_repository.GitRepository(
        local_path=local_path, url="https://google.com"
    )

    assert not repository.exists_on_remote()


def test_repository_update_local_copy_with_error(caplog, repository, local_path):
    shutil.rmtree(local_path)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(exceptions.ExternalProcessError) as error:
            repository.update_local_copy()

    message = "An error occurred on while attempting to execute the command."
    assert message in caplog.text

    message = "Failed to execute the command: git fetch --all --prune --verbose."
    assert message == str(error.value)
