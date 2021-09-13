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
$ make install
```

To install from source using `setup.py`:

```shell
$ git clone git@github.com:whitfieldsdad/python-kenna-api-client.git
$ python3 setup.py install
```

## Tutorials

The following general options are available:

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
  --help  Show this message and exit.

Commands:
  count-applications
  get-application
  get-application-ids
  get-application-names
  get-application-owners
  get-applications
```

### Assets

The following options are available when listing assets: 

```shell
$ poetry run kenna assets
Usage: kenna assets [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  count-assets
  get-asset
  get-asset-hostnames
  get-asset-ipv4-addresses
  get-asset-ipv6-addresses
  get-asset-tags
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
  get-connector
  get-connector-run
  get-connector-runs
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
  get-dashboard-group
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
  get-fix
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
  get-user
  get-users
```

### Roles

The following options are available when listing roles:

```shell
$ poetry run kenna roles
Usage: kenna roles [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  count-roles
  get-role
  get-roles
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
  get-vulnerabilities
  get-vulnerability
```
