# docker

To minimize the docker image size and ensure that no unnecessary components were installed, the [yocto project](https://www.yoctoproject.org) was used to build a minimal root filesystem image. This custom image includes only the python interpreter and the required python packages, providing a lean and controlled runtime environment tailored specifically for the target application. By leveraging yocto's fine-grained control over package inclusion, the resulting image maintains a minimal footprint while preserving full functionality.

## Basic usage

To launch the container using a custom configuration file and output directory, execute the following `docker run` command:

```bash
docker run -d -v "$(pwd)/easy_mirrors.ini:/easy_mirrors.ini:ro" "vladpunko/easy-mirrors:${IMAGE_TAG?err}"
```

By default, repositories will be cloned inside the container. It is strongly recommended to mount a directory from your host system to the path specified in the configuration file to persist cloned data and prevent data loss when the container is removed.

## Build

To create a minimal docker-compatible image using the yocto project and the `meta-easy-mirrors` layer, follow these steps:

```bash
# Step -- 1.
git clone --branch kirkstone git://git.yoctoproject.org/poky.git

cd ./poky/

# Step -- 2.
source ./oe-init-build-env

bitbake-layers -h  # to validate

# Step -- 3.
bitbake-layers add-layer ../../meta-easy-mirrors
```

Open `conf/local.conf` in your preferred editor and locate the following line. Override the default value set by the meta-layer to specify your desired target architecture.

```conf
MACHINE ??= "qemux86-64"  # options include arch-aarch64 or arch-x86-64
```

To minimize the number of installed packages within the docker image, it is strongly recommended to use the ipk package format. Ensure this is configured by setting the following in your configuration file:

```conf
PACKAGE_CLASSES ?= "package_ipk"
```

The next step is to build the base image by executing the following commands in sequence:

```bash
# Step -- 1.
bitbake python3-image

# Step -- 2.
docker import ./tmp/deploy/images/<machine>/python3-image-<machine>.tar.bz2 python3-minimal:latest

# Step -- 3.
docker run --rm python3-minimal:latest python3 -c 'print(__import__("sys").executable)'
```
