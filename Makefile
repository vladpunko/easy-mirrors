.DEFAULT: help

IMAGE_TAG := $(shell poetry version --short)

.PHONY: help
help:
	@echo 'help            - show help'
	@echo 'lock            - lock the project dependencies'
	@echo 'bootstrap       - install the project dependencies'
	@echo 'build           - build project packages'
	@echo 'upload          - upload built packages to package repository'
	@echo 'containers      - build the docker images on the current machine'
	@echo 'push_containers - push all docker images to the primary repository'
	@echo 'docker_manifest - create a manifest for the generated docker images'
	@echo 'hooks           - install all git hooks'
	@echo 'tests           - run project tests'
	@echo 'lint            - inspect project source code for problems and errors'
	@echo 'clean           - clean up project environment and all the build artifacts'

.PHONY: lock
lock:
	@poetry lock --no-cache

bootstrap: poetry.lock poetry.toml pyproject.toml
	@poetry check
	@poetry install -vv --compile --no-cache --with dev --with tests

build: bootstrap
	@poetry build --clean

upload: TWINE_NON_INTERACTIVE = true
upload: build
	@poetry run twine upload --repository pypi --skip-existing dist/*

.PHONY: containers
containers:
	@env IMAGE_TAG=$(IMAGE_TAG) docker buildx bake

push_containers: containers
	@docker push docker.io/vladpunko/easy-mirrors:$(IMAGE_TAG)-amd64
	@docker push docker.io/vladpunko/easy-mirrors:$(IMAGE_TAG)-arm64

docker_manifest: push_containers
	@docker manifest create docker.io/vladpunko/easy-mirrors:$(IMAGE_TAG) \
		--amend docker.io/vladpunko/easy-mirrors:$(IMAGE_TAG)-amd64 \
		--amend docker.io/vladpunko/easy-mirrors:$(IMAGE_TAG)-arm64
	@docker manifest push docker.io/vladpunko/easy-mirrors:$(IMAGE_TAG)

hooks: bootstrap
	@poetry run pre-commit install --config .githooks.yml

tests: bootstrap
	@poetry run tox

lint: bootstrap
	@poetry run tox -e lint

.PHONY: clean
clean:
	git clean -X -d --force
