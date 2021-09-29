# kenna

![Kenna](https://raw.githubusercontent.com/whitfieldsdad/images/main/kenna-hero.png)

`kenna` is an [API](https://apidocs.kennasecurity.com/reference) client for [Kenna Security](https://www.kennasecurity.com/) that allows you to work with applications, assets, connectors, dashboard groups, users, roles, vulnerabilities, and fixes.

## FAQ

### What's included?

- An API client that allows you to lookup applications, assets, asset groups, connectors, connector runs, dashboard groups, users, roles, fixes, and vulnerabilities;
- A robust command-line interface to go along with it

## Installation

To install `kenna` using `pip`:

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
 
Finally, export an environment variable named `KENNA_API_KEY` to your shell (i.e. add it to your `~/.bashrc` or user profile).

## Important environment variables

- `KENNA_API_KEY`: your API key for accessing Kenna (required)
- `ENABLE_INTEGRATION_TESTS`: `true` or `false` (optional)

## Testing

You can run the unit tests and integration tests for this package as follows:

```shell
$ make test
```

If the value of the `$ENABLE_INTEGRATION_TESTS` environment variable is set to `true`, both the unit tests and integration tests will be executed:

```shell
$ ENABLE_INTEGRATION_TESTS=true make test
```

If you have separate tenants for development and production, you can select which tenant you'd like to work with as follows:

```shell
$ ENABLE_INTEGRATION_TESTS=true
$ KENNA_API_KEY=${KENNA_DEVELOPMENT_API_KEY} make test
$ KENNA_API_KEY=${KENNA_PRODUCTION_API_KEY} make test
```

## Tutorials

### Command-line interface

The command-line interface for `kenna` allows you to search for, list, and count [applications](https://apidocs.kennasecurity.com/reference#list-applications), [assets](https://apidocs.kennasecurity.com/reference#list-assets), [asset groups](https://apidocs.kennasecurity.com/reference#list-asset-groups), [connectors](https://apidocs.kennasecurity.com/reference#list-connectors), [connector runs](https://apidocs.kennasecurity.com/reference#list-connector-runs), [dashboard groups](https://apidocs.kennasecurity.com/reference#list-dashboard-groups), [fixes](https://apidocs.kennasecurity.com/reference#list-fixes), [roles](https://apidocs.kennasecurity.com/reference#list-roles), [users](https://apidocs.kennasecurity.com/reference#list-users), and [vulnerabilities](https://apidocs.kennasecurity.com/reference#list-vulnerabilities).

After installing `kenna` you can access the command-line interface as follows:

```shell
$ poetry run kenna
```

If you're not using `poetry` (you should use it), you can access the command line as follows:

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
````

#### Applications

The following options are available when working with applications:

```shell
$ poetry run kenna applications --help
Usage: kenna applications [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  get-applications
```

##### List applications

The following options are available when listing applications:

```shell
$ poetry run kenna applications get-applications --help
Usage: kenna applications get-applications [OPTIONS]

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
  --limit INTEGER
  --help                          Show this message and exit.
```

#### Assets

The following options are available when working with assets:

```shell
$ poetry run kenna assets --help
Usage: kenna assets [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  get-assets
```

##### List assets

The following options are available when listing assets:

```shell
$ poetry run kenna assets get-assets --help
Usage: kenna assets get-assets [OPTIONS]

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
  --limit INTEGER
  --help                          Show this message and exit.
```

#### Asset groups

The following options are available when working with asset groups:

```shell
$ poetry run kenna asset-groups --help
Usage: kenna asset-groups [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  get-asset-groups
```

##### List asset groups

The following options are available when listing asset groups:

```shell
$ poetry run kenna asset-groups get-asset-groups --help
Usage: kenna asset-groups get-asset-groups [OPTIONS]

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
  --limit INTEGER
  --help                          Show this message and exit.
```

For example, let's list the ID, name, asset count, vulnerability count, and fix count associated with each asset group that has a name containing the string "Europe":

```shell
$ poetry run kenna asset-groups get-asset-groups --asset-group-names "*Europe*" | jq '{"id": .id, "name": .name, "asset_count": .asset_count, "vulnerability_count": .vulnerability_count, "fix_count": .fix_count}' | jq --slurp
[
  {
    "id": 123456,
    "name": "All European assets",
    "asset_count": 12345,
    "vulnerability_count": 1234567,
    "fix_count": 12345
  }
]
```

#### Connectors

The following options are available when working with connectors:

```shell
$ poetry run kenna connectors --help
Usage: kenna connectors [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  get-connectors
```

##### List connectors

The following options are available when listing connectors:

```shell
$ poetry run kenna connectors get-connectors --help
Usage: kenna connectors get-connectors [OPTIONS]

Options:
  --connector-ids TEXT
  --connector-names TEXT
  --min-connector-run-start-time TEXT
  --max-connector-run-start-time TEXT
  --min-connector-run-end-time TEXT
  --max-connector-run-end-time TEXT
  --limit INTEGER
  --help                          Show this message and exit.
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

##### List connector runs

The following options are available when listing connector runs:

```shell
$ poetry run kenna connector-runs get-connector-runs --help
Usage: kenna connector-runs get-connector-runs [OPTIONS]

Options:
  --connector-ids TEXT
  --connector-names TEXT
  --connector-run-ids TEXT
  --min-connector-run-start-time TEXT
  --max-connector-run-start-time TEXT
  --min-connector-run-end-time TEXT
  --max-connector-run-end-time TEXT
  --limit INTEGER
  --help                          Show this message and exit.
```

#### Dashboard groups

The following options are available when working with dashboard groups:

```shell
$ poetry run kenna dashboard-groups --help
Usage: kenna dashboard-groups [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  get-dashboard-groups
```

##### List dashboard groups

The following options are available when listing dashboard groups:

```shell
$ poetry run kenna dashboard-groups get-dashboard-groups --help
Usage: kenna dashboard-groups get-dashboard-groups [OPTIONS]

Options:
  --dashboard-group-ids TEXT
  --dashboard-group-names TEXT
  --role-ids TEXT
  --role-names TEXT
  --min-dashboard-group-create-time TEXT
  --max-dashboard-group-create-time TEXT
  --min-dashboard-group-last-update-time TEXT
  --max-dashboard-group-last-update-time TEXT
  --limit INTEGER
  --help                          Show this message and exit.
```

#### Users

The following options are available when working with users:

```shell
$ poetry run kenna users --help
Usage: kenna users [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  get-users
```

##### List users

The following options are available when listing users:

```shell
$ poetry run kenna users get-users --help
poetry run kenna users get-users --help
Usage: kenna users get-users [OPTIONS]

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
  --limit INTEGER
  --help                          Show this message and exit.
```

#### Roles

The following options are available when working with roles:

```shell
$ poetry run kenna roles --help
Usage: kenna roles [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  get-roles
```

##### List roles

The following options are available when listing roles:

```shell
$ poetry run kenna roles get-roles --help
Usage: kenna roles get-roles [OPTIONS]

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
  --limit INTEGER
  --help                          Show this message and exit.
```

#### Vulnerabilities

The following options are available when working with vulnerabilities:

```shell
$ poetry run kenna vulnerabilities --help
Usage: kenna vulnerabilities [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  get-vulnerabilities
```

##### List vulnerabilities

The following options are available when listing vulnerabilities:

```shell
$ poetry run kenna vulnerabilities get-vulnerabilities --help
Usage: kenna vulnerabilities get-vulnerabilities [OPTIONS]

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
  --limit INTEGER
  --help                          Show this message and exit.
```

#### Fixes

The following options are available when working with fixes:

```shell
$ poetry run kenna fixes --help
Usage: kenna fixes [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  get-fixes
```

##### List fixes

The following options are available when listing fixes:

```shell
$ poetry run kenna fixes get-fixes --help
Usage: kenna fixes get-fixes [OPTIONS]

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
  --limit INTEGER
  --help                          Show this message and exit.
```
