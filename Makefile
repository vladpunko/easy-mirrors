.DEFAULT: help

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

upload: TWINE_NON_INTERACTIVE = true
upload: build
	@poetry run twine upload --repository pypi --skip-existing dist/*

.PHONY: containers
containers:
	@env TAG=$(shell poetry version --short) docker buildx bake

hooks: bootstrap
	@poetry run pre-commit install --config .githooks.yml

tests: bootstrap
	@poetry run tox

lint: bootstrap
	@poetry run tox -e lint

.PHONY: clean
clean:
	git clean -X -d --force
