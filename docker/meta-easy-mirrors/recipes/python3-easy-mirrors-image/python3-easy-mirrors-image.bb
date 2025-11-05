# -*- coding: utf-8 -*-

# Copyright 2025 (c) Vladislav Punko <iam.vlad.punko@gmail.com>

# Tell yocto to build the image in a container-compatible format.
IMAGE_FSTYPES = "container"

inherit core-image

# Prevent generation of an empty container layer.
IMAGE_CONTAINER_NO_DUMMY = "1"

# Specify a list of packages to be included in the final image.
IMAGE_INSTALL = "\
    git \
    python3-core \
    python3-json \
    python3-logging \
    python3-easy-mirrors \
"

# Specify the locale for the image.
GLIBC_GENERATE_LOCALES = "C.UTF-8"
