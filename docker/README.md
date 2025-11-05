# docker

To reduce the Docker image size and avoid installing unnecessary components, the [Yocto Project](https://www.yoctoproject.org/) was used to build a minimal root filesystem. This custom image contains only the [Python interpreter](https://www.python.org/) and the required packages, creating a lightweight and controlled runtime environment tailored to the target application. By leveraging Yocto's precise control over package inclusion, the resulting image achieves a minimal footprint without compromising functionality.

## Basic usage

To launch the container using a custom configuration file and output directory, execute the following `docker run` command:

```bash
docker run -d -v "$(pwd)/easy_mirrors.ini:/easy_mirrors.ini:ro" "docker.io/vladpunko/easy-mirrors:${IMAGE_TAG:?err}"
```

By default, repositories will be cloned inside the container. It is strongly recommended to mount a directory from your host system to the path specified in the configuration file to persist cloned data and prevent data loss when the container is removed.

## Build

To create a minimal docker-compatible image using the Yocto Project and the `meta-easy-mirrors` layer, follow these steps:

```bash
# Step -- 1.
git clone --branch scarthgap git://git.yoctoproject.org/poky.git

cd ./poky/

# Step -- 2.
source ./oe-init-build-env

bitbake-layers -h  # to validate

# Step -- 3.
bitbake-layers add-layer ../../meta-easy-mirrors
```

Open `conf/local.conf` in your preferred editor and locate the following line. Override the default value set by the meta-layer to specify your desired target architecture.

```conf
MACHINE ??= "qemuarm64"  # for ARM-based systems

# or

MACHINE ??= "qemux86-64"  # for x86_64-based systems
```

To minimize the number of installed packages within the docker image, it is strongly recommended to use the `ipk` package format. Ensure this is configured by setting the following in your configuration file:

```conf
PACKAGE_CLASSES ?= "package_ipk"
```

The next step is to build the base image by executing the following commands in sequence:

```bash
# Step -- 1.
bitbake python3-easy-mirrors-image

# Step -- 2.
docker import "$(find "./tmp/deploy/images/${MACHINE:?err}" -name 'python3-image-*.tar.bz2' | head -n 1)" "python3-minimal:3.10-${MACHINE:?err}"

# Step -- 3.
docker run --rm "python3-minimal:3.10-${MACHINE:?err}" python3 -c 'print(__import__("sys").executable)'
```

To maintain architecture compatibility when using `docker import`, include the `--platform` flag **only** if the image was built for a different architecture than your host system. By default, Docker imports images for [the daemon's native platform](https://docs.docker.com/reference/cli/docker/image/import/#platform). To avoid runtime issues across different CPU architectures, specify the platform explicitly -- use `--platform=linux/arm64` for ARM targets or `--platform=linux/amd64` for x86 systems.
