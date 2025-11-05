# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

HOMEPAGE = "https://github.com/vladpunko/easy-mirrors"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=f2b48c6b5565659a3aed6766c79e9a76"

WHEEL_NAME = "easy_mirrors-0.3.2-py3-none-any.whl"

SRC_URI = "https://files.pythonhosted.org/packages/07/4d/5504f4171e4e85b2e00184f8a31d7ba81b8a497d2df88c45e59be00c1334/${WHEEL_NAME}"
SRC_URI[md5sum] = "9879715b72027a39401d8e7b7eeb30df"
SRC_URI[sha256sum] = "7ab73aa3a3ff4795e67c9a0016df6e0c116c928ee79bf71b09f3db8c04a558f8"

# Enable native python build environment.
inherit python3native

do_unpack[depends] += "python3-pip-native:do_populate_sysroot"

# Install the package using pip into the source directory.
do_unpack () {
    echo "Installing package..."

    ${STAGING_BINDIR_NATIVE}/pip3 install \
        --disable-pip-version-check \
        --no-cache-dir \
        --no-deps \
        --target ${S} \
    ${DL_DIR}/${WHEEL_NAME}
}

# Copy installed files into target python site-packages.
do_install () {
    echo "Installing to the target image..."

    install -d ${D}${PYTHON_SITEPACKAGES_DIR}
    cp -f -r ${S}/* ${D}${PYTHON_SITEPACKAGES_DIR}/
    rm -f -r ${D}${PYTHON_SITEPACKAGES_DIR}/*.dist*
}

# Disable unnecessary configure and compile steps.
do_configure[noexec] = "1"
do_compile[noexec] = "1"

# Include python libraries in the package.
FILES:${PN} += "${libdir}/*"
