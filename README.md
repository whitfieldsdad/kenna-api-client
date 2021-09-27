# Kenna

> An API client for Kenna Security

![Kenna](https://raw.githubusercontent.com/whitfieldsdad/images/main/kenna-hero.png)

## Installation

To install using `pip`:

```shell
$ pip install kenna
```

To install `kenna` from source (requires [`poetry`](https://github.com/python-poetry/poetry)):

```shell
$ git clone git@github.com:whitfieldsdad/python-kenna.git
$ cd python-kenna
$ make install
```

To install `kenna` from source using `setup.py` (i.e. if you're not using `poetry`):

```shell
$ git clone git@github.com:whitfieldsdad/python-kenna.git
$ cd python-kenna
$ python3 setup.py install
```

## Required environment variables

- `$KENNA_API_KEY`: your API key for accessing Kenna.

## Tutorials

### Command-line interface

The command-line interface for `kenna` allows you to search for, list, and count [applications](https://apidocs.kennasecurity.com/reference#list-applications), [assets](https://apidocs.kennasecurity.com/reference#list-assets), [asset groups](https://apidocs.kennasecurity.com/reference#list-asset-groups), [connectors](https://apidocs.kennasecurity.com/reference#list-connectors), [connector runs](https://apidocs.kennasecurity.com/reference#list-connector-runs), [dashboard groups](https://apidocs.kennasecurity.com/reference#list-dashboard-groups), [fixes](https://apidocs.kennasecurity.com/reference#list-fixes), [roles](https://apidocs.kennasecurity.com/reference#list-roles), [users](https://apidocs.kennasecurity.com/reference#list-users), and [vulnerabilities](https://apidocs.kennasecurity.com/reference#list-vulnerabilities).

After installing `kenna` you can access the command-line interface as follows:

```shell
$ poetry run kenna
```

If you're not using `poetry`, you can access the command line as follows:

```shell
$ python3 -m kenna.cli
```

#### General

The following general options are available within the command-line interface:

```shell
$ poetry run kenna
Usage: kenna [OPTIONS] COMMAND [ARGS]...

Options:
  --api-key TEXT
  --region TEXT
  --help          Show this message and exit.

Commands:
  applications
  asset-groups
  assets
  connector-runs
  connectors
  dashboard-groups
  fixes
  roles
  users
  vulnerabilities
```

#### Applications

The following options are available when working with applications:

```shell
$ poetry run kenna applications --help
Usage: kenna applications [OPTIONS] COMMAND [ARGS]...

Options:
  --application-ids TEXT
  --application-names TEXT
  --application-owners TEXT
  --application-teams TEXT
  --application-business-units TEXT
  --min-application-risk-meter-score INTEGER
  --max-application-risk-meter-score INTEGER
  --min-asset-count INTEGER
  --max-asset-count INTEGER
  --min-vulnerability-count INTEGER
  --max-vulnerability-count INTEGER
  --help                          Show this message and exit.

Commands:
  get-applications
```

#### Assets

The following options are available when working with assets:

```shell
$ poetry run kenna assets --help
Usage: kenna assets [OPTIONS] COMMAND [ARGS]...

Options:
  --asset-ids TEXT
  --asset-group-ids TEXT
  --asset-group-names TEXT
  --asset-tags TEXT
  --asset-hostnames TEXT
  --asset-ip-addresses TEXT
  --asset-mac-addresses TEXT
  --min-asset-risk-meter-score INTEGER
  --max-asset-risk-meter-score INTEGER
  --min-asset-first-seen-time TEXT
  --max-asset-first-seen-time TEXT
  --min-asset-last-seen-time TEXT
  --max-asset-last-seen-time TEXT
  --min-asset-last-boot-time TEXT
  --max-asset-last-boot-time TEXT
  --help                          Show this message and exit.

Commands:
  get-assets
```

#### Asset groups

The following options are available when working with asset groups:

```shell
$ poetry run kenna asset-groups --help
Usage: kenna asset-groups [OPTIONS] COMMAND [ARGS]...

Options:
  --asset-group-ids TEXT
  --asset-group-names TEXT
  --asset-ids TEXT
  --asset-tags TEXT
  --asset-hostnames TEXT
  --asset-ip-addresses TEXT
  --asset-mac-addresses TEXT
  --min-asset-group-create-time TEXT
  --max-asset-group-create-time TEXT
  --min-asset-group-last-update-time TEXT
  --max-asset-group-last-update-time TEXT
  --help                          Show this message and exit.

Commands:
  get-asset-groups
```

#### Connectors

The following options are available when working with connectors:

```shell
$ poetry run kenna connectors --help
Usage: kenna connectors [OPTIONS] COMMAND [ARGS]...

Options:
  --connector-ids TEXT
  --connector-names TEXT
  --min-connector-run-start-time TEXT
  --max-connector-run-start-time TEXT
  --min-connector-run-end-time TEXT
  --max-connector-run-end-time TEXT
  --help                          Show this message and exit.

Commands:
  get-connectors
```

#### Connector runs

The following options are available when working with connector runs:

```shell
$ poetry run kenna connector-runs --help

Usage: kenna connector-runs [OPTIONS] COMMAND [ARGS]...

Options:
  --connector-ids TEXT
  --connector-names TEXT
  --connector-run-ids TEXT
  --min-connector-run-start-time TEXT
  --max-connector-run-start-time TEXT
  --min-connector-run-end-time TEXT
  --max-connector-run-end-time TEXT
  --help                          Show this message and exit.

Commands:
  get-connector-runs
```

#### Dashboard groups

The following options are available when working with dashboard groups:

```shell
$ poetry run kenna dashboard-groups --help
Usage: kenna dashboard-groups [OPTIONS] COMMAND [ARGS]...

Options:
  --dashboard-group-ids TEXT
  --dashboard-group-names TEXT
  --role-ids TEXT
  --role-names TEXT
  --min-dashboard-group-create-time TEXT
  --max-dashboard-group-create-time TEXT
  --min-dashboard-group-last-update-time TEXT
  --max-dashboard-group-last-update-time TEXT
  --help                          Show this message and exit.

Commands:
  get-dashboard-groups
```

#### Users

The following options are available when working with users:

```shell
$ poetry run kenna users --help
Usage: kenna users [OPTIONS] COMMAND [ARGS]...

Options:
  --user-ids TEXT
  --user-names TEXT
  --user-email-addresses TEXT
  --min-user-create-time TEXT
  --max-user-create-time TEXT
  --min-user-last-sign-in-time TEXT
  --max-user-last-sign-in-time TEXT
  --min-user-last-update-time TEXT
  --max-user-last-update-time TEXT
  --help                          Show this message and exit.

Commands:
  get-users
```

#### Roles

The following options are available when working with roles:

```shell
$ poetry run kenna roles --help
Usage: kenna roles [OPTIONS] COMMAND [ARGS]...

Options:
  --role-ids TEXT
  --role-names TEXT
  --role-types TEXT
  --role-access-levels TEXT
  --role-custom-permissions TEXT
  --user-ids TEXT
  --user-email-addresses TEXT
  --user-names TEXT
  --min-role-create-time TEXT
  --max-role-create-time TEXT
  --min-role-last-update-time TEXT
  --max-role-last-update-time TEXT
  --help                          Show this message and exit.

Commands:
  get-roles
```

#### Vulnerabilities

The following options are available when working with vulnerabilities:

```shell
$ poetry run kenna vulnerabilities --help
Usage: kenna vulnerabilities [OPTIONS] COMMAND [ARGS]...

Options:
  --vulnerability-ids TEXT
  --cve-ids TEXT
  --fix-ids TEXT
  --fix-names TEXT
  --fix-vendors TEXT
  --asset-ids TEXT
  --asset-hostnames TEXT
  --asset-ip-addresses TEXT
  --asset-mac-addresses TEXT
  --asset-group-ids TEXT
  --asset-group-names TEXT
  --asset-tags TEXT
  --min-vulnerability-risk-meter-score INTEGER
  --max-vulnerability-risk-meter-score INTEGER
  --min-vulnerability-first-seen-time TEXT
  --max-vulnerability-first-seen-time TEXT
  --min-vulnerability-last-seen-time TEXT
  --max-vulnerability-last-seen-time TEXT
  --min-cve-publish-time TEXT
  --max-cve-publish-time TEXT
  --min-patch-publish-time TEXT
  --max-patch-publish-time TEXT
  --min-patch-due-date TEXT
  --max-patch-due-date TEXT
  --help                          Show this message and exit.

Commands:
  get-vulnerabilities
```

#### Fixes

The following options are available when working with fixes:

```shell
$ poetry run kenna fixes --help
Usage: kenna fixes [OPTIONS] COMMAND [ARGS]...

Options:
  --fix-ids TEXT
  --fix-names TEXT
  --fix-vendors TEXT
  --cve-ids TEXT
  --asset-ids TEXT
  --asset-hostnames TEXT
  --asset-ip-addresses TEXT
  --asset-mac-addresses TEXT
  --asset-ip-addresses TEXT
  --asset-mac-addresses TEXT
  --asset-group-ids TEXT
  --asset-group-names TEXT
  --asset-tags TEXT
  --min-fix-create-time TEXT
  --max-fix-create-time TEXT
  --min-fix-last-update-time TEXT
  --max-fix-last-update-time TEXT
  --help                          Show this message and exit.

Commands:
  get-fixes
```
