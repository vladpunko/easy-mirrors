# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

ARG BASE_IMAGE="vladpunko/python3-easy-mirrors:3.10-qemuarm64"

FROM ${BASE_IMAGE}

LABEL maintainer="Vladislav Punko <iam.vlad.punko@gmail.com>"

STOPSIGNAL SIGTERM

ENTRYPOINT ["python3", "-m", "easy_mirrors"]
