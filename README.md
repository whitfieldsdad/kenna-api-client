# Kenna

> An API client for Kenna Security

![Kenna](https://raw.githubusercontent.com/whitfieldsdad/images/main/kenna-hero.png)

## Installation

To install using `pip`:

```shell
$ pip install kenna
```

To install from source using `poetry`

```shell
$ git clone git@github.com:whitfieldsdad/python-kenna-api-client.git
$ poetry install
```

To install from source using `setup.py`:

```shell
$ git clone git@github.com:whitfieldsdad/python-kenna-api-client.git
$ python3 setup.py install
```

## Authentication

You have two options when it comes to providing your Kenna API key:
- Set the value of the `KENNA_API_KEY` environment variable to your Kenna API key (recommended); or
- Provide your API key on the command line.

```shell
$ poetry run kenna
Usage: kenna [OPTIONS] COMMAND [ARGS]...

Options:
  --api-key TEXT
  --region TEXT
  --help          Show this message and exit.
...
```

### Makefile targets

#### `make install`

Install the module using `poetry`.

#### `make clean`

Remove `dist/`.

#### `make update`

Update the project's dependencies using `poetry`, overwrite `requirements.txt`, show the updated dependency tree.

#### `make unit-test`

Run the unit tests (fast).

#### `make integration-test`

Run the integration tests (slow).

Tests will be skipped unless the `$KENNA_API_KEY` environment variable is set.

#### `make test`

Combines the `unit-test` and `integration-test` targets.

#### `make coverage`

Measure code coverage and write a code coverage report to `htmlcov/index.html`.

#### `make view-coverage`

Open the generated code coverage report from `htmlcov/index.html` in your default web browser.

#### `make build`

Create a source distribution tarball and wheel file for this package.

#### `make release`

Release the source distribution tarball and wheel file in `dist/` to [PyPi](https://pypi.org/project/kenna/).

## Tutorials (CLI)

The following options are available:

```shell
$ poetry run kenna
Usage: kenna [OPTIONS] COMMAND [ARGS]...

Options:
  --api-key TEXT
  --region TEXT
  --help          Show this message and exit.

Commands:
  applications
  assets
  connector-runs
  connectors
  dashboard-groups
  fixes
  roles
  users
  vulnerabilities
```

If you're not using `poetry`, you can access the command line interface as follows:

```shell
$ python3 -m kenna.cli
```

### Applications

The following options are available when listing applications.

```shell
$ poetry run kenna applications
Usage: kenna applications [OPTIONS] COMMAND [ARGS]...

Options:
  --application-ids TEXT
  --application-names TEXT
  --help                    Show this message and exit.

Commands:
  count-applications
  get-applications
```

### Assets

The following options are available when listing assets: 

```shell
$ poetry run kenna assets
Usage: kenna assets [OPTIONS] COMMAND [ARGS]...

Options:
  --asset-ids TEXT
  --asset-names TEXT
  --help              Show this message and exit.

Commands:
  count-assets
  get-assets
```

### Connectors

The following options are available when listing connectors:

```shell
$ poetry run kenna connectors
Usage: kenna connectors [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  count-connectors
  get-connectors
```

### Dashboard groups

The following options are available when listing dashboard groups:

```shell
$ poetry run kenna dashboard-groups
Usage: kenna dashboard-groups [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  count-dashboard-groups
  get-dashboard-groups
```

### Fixes

The following options are available when listing fixes:

```shell
$ poetry run kenna fixes
Usage: kenna fixes [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  count-fixes
  get-fixes
```

### Users

The following options are available when listing users:

```shell
$ poetry run kenna users
Usage: kenna users [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  count-users
  get-users
```

### Vulnerabilities

The following options are available when listing vulnerabilities:

```shell
$ poetry run kenna vulnerabilities
Usage: kenna vulnerabilities [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  count-vulnerabilities
  get-cves
  get-vulnerabilities
```
