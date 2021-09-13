from kenna.api import Kenna

import click
import hodgepodge.types
import hodgepodge.click


@click.group()
@click.pass_context
def vulnerabilities(_):
    pass


@vulnerabilities.command()
@click.option('--vulnerability-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def count_vulnerabilities(ctx, vulnerability_ids: str, limit: int):
    """
    Count matching vulnerabilities.
    """
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_vulnerabilities(
        vulnerability_ids=hodgepodge.click.str_to_list_of_int(vulnerability_ids),
        limit=limit,
    )
    count = sum(1 for _ in rows)
    click.echo(count)


@vulnerabilities.command()
@click.option('--vulnerability-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_vulnerabilities(ctx, vulnerability_ids: str, limit: int):
    """
    Lookup one or more vulnerabilities.
    """
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    apps = api.iter_vulnerabilities(
        vulnerability_ids=hodgepodge.click.str_to_list_of_int(vulnerability_ids),
        limit=limit,
    )
    for app in apps:
        app = hodgepodge.types.dict_to_json(app)
        click.echo(app)


@vulnerabilities.command()
@click.option('--vulnerability-id', required=True, type=int)
@click.pass_context
def get_vulnerability(ctx, vulnerability_id: int):
    """
    Lookup a single vulnerability.
    """
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    app = api.get_vulnerability(vulnerability_id=vulnerability_id)
    if app:
        app = hodgepodge.types.dict_to_json(app)
        click.echo(app)
