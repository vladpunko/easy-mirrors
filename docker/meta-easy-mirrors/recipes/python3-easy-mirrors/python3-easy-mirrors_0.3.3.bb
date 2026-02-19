# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

HOMEPAGE = "https://github.com/vladpunko/easy-mirrors"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=f2b48c6b5565659a3aed6766c79e9a76"

SRC_URI = "git://github.com/vladpunko/easy-mirrors.git;branch=master;protocol=https"
SRCREV="e76dc320108931e905cfe9e5c6ede6ba73c7da76"
S = "${WORKDIR}/git"

inherit python_poetry_core

BBCLASSEXTEND += "native nativesdk"
