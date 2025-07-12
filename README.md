# easy-mirrors

![hooks](https://github.com/vladpunko/easy-mirrors/actions/workflows/hooks.yml/badge.svg)
![tests](https://github.com/vladpunko/easy-mirrors/actions/workflows/tests.yml/badge.svg)

Simplest way to back up and restore git repositories.

## Installation

Ensure that [git](https://git-scm.com) is installed on your system.

Use the package manager [pip](https://pip.pypa.io/en/stable) to install `easy-mirrors` along with its command-line interface by running:

```bash
python3 -m pip install --user easy-mirrors
```

## Basic usage

This program enables you to mirror your git repositories to a backup destination.

> **Warning:**
> Ensure that git is correctly configured and that you have access to the repositories you intend to mirror before starting.
> This guarantees a smooth backup process and safeguards your valuable data.

Create a configuration file named `easy_mirrors.ini` in your home directory containing the following content:

```ini
[easy_mirrors]
path = /tmp/repositories
repositories =
  https://github.com/vladpunko/easy-mirrors.git
```

Use the following commands to mirror and restore your repository:

```bash
# Step -- 1.
easy-mirrors --period 30  # make mirrors every 30 minutes

# Step -- 2.
cd /tmp/repositories/easy-mirrors.git

# Step -- 3.
git push --mirror https://github.com/vladpunko/easy-mirrors.git
```

## Contributing

Pull requests are welcome.
Please open an issue first to discuss what should be changed.

Please make sure to update tests as appropriate.

```bash
# Step -- 1.
python3 -m venv .venv && source ./.venv/bin/activate && pip install pre-commit tox

# Step -- 2.
pre-commit install --config .githooks.yml

# Step -- 3.
tox && tox -e lint
```

## License

[MIT](https://choosealicense.com/licenses/mit)
