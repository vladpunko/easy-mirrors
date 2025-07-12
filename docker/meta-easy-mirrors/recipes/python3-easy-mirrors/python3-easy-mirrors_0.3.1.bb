# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

LICENSE = "CLOSED"

WHEEL_NAME = "easy_mirrors-0.3.1-py3-none-any.whl"

SRC_URI = "https://files.pythonhosted.org/packages/4f/cf/9cdcce5e073171d826a80ed4dcb7cabfd3fc513cb430aa7754a311f8c5c9/${WHEEL_NAME}"
SRC_URI[md5sum] = "f8bc70ffedcdce6c5d4203778c63c179"
SRC_URI[sha256sum] = "66c68b9f378e51ad849d1ad1831daa552aa581a227c7663fb63dda7d8980bbbb"

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
