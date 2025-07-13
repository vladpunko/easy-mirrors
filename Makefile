.DEFAULT: help

CONTAINER_NAME = docker.io/vladpunko/easy-mirrors
.ONESHELL:
CONTAINER_VERSION ?= $(shell poetry version --short)

.PHONY: help
help:
	@echo 'help         - show help'
	@echo 'lock         - lock the project dependencies'
	@echo 'bootstrap    - install the project dependencies'
	@echo 'build        - build project packages'
	@echo 'upload       - upload built packages to package repository'
	@echo 'containers   - build the docker images on the current machine'
	@echo 'hooks        - install all git hooks'
	@echo 'tests        - run project tests'
	@echo 'docs         - generate the project documentation'
	@echo 'lint         - inspect project source code for problems and errors'
	@echo 'clean        - clean up project environment and all the build artifacts'

.PHONY: lock
lock:
	@poetry lock --no-cache

bootstrap: poetry.lock poetry.toml pyproject.toml
	@poetry check
	@poetry install -vv --compile --no-cache --with dev --with tests

build: bootstrap
	@poetry build --clean

upload: build
	@poetry run twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	@poetry run twine upload dist/*

.PHONY: containers
containers:
	@env DOCKER_BUILDKIT=1 docker build \
			--build-arg BASE_IMAGE='vladpunko/python3-easy-mirrors:3.10' \
			--network host \
			--platform linux/amd64 \
			--tag $(CONTAINER_NAME):$(CONTAINER_VERSION) \
		$(PWD)
	@env DOCKER_BUILDKIT=1 docker build \
			--build-arg BASE_IMAGE='vladpunko/python3-easy-mirrors:3.10-aarch64' \
			--network host \
			--platform linux/arm64 \
			--tag $(CONTAINER_NAME):$(CONTAINER_VERSION)-aarch64 \
		$(PWD)

hooks: bootstrap
	@poetry run pre-commit install --config .githooks.yml

tests: bootstrap
	@poetry run tox

lint: bootstrap
	@poetry run tox -e lint

.PHONY: clean
clean:
	git clean -X -d --force
