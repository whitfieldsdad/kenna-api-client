from kenna.api import Kenna

import click
import hodgepodge.types
import hodgepodge.click
import json


@click.group()
@click.option('--vulnerability-ids')
@click.option('--vulnerability-names')
@click.pass_context
def vulnerabilities(ctx, vulnerability_ids: str, vulnerability_names: str):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    ctx.obj.update({
        'vulnerability_ids': hodgepodge.click.str_to_list_of_int(vulnerability_ids),
        'vulnerability_names': hodgepodge.click.str_to_list_of_str(vulnerability_names),
    })


@vulnerabilities.command()
@click.pass_context
def count_vulnerabilities(ctx):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_vulnerabilities(
        vulnerability_ids=ctx.obj['vulnerability_ids'],
        vulnerability_names=ctx.obj['vulnerability_names'],
    )
    n = sum(1 for _ in rows)
    click.echo(n)


@vulnerabilities.command()
@click.option('--limit', type=int)
@click.pass_context
def get_vulnerabilities(ctx, limit):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_vulnerabilities(
        vulnerability_ids=ctx.obj['vulnerability_ids'],
        vulnerability_names=ctx.obj['vulnerability_names'],
        limit=limit,
    )
    for row in rows:
        row = hodgepodge.types.dict_to_json(row)
        click.echo(row)


@vulnerabilities.command()
@click.option('--limit', type=int)
@click.pass_context
def get_cves(ctx, limit):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_cves(
        vulnerability_ids=ctx.obj['vulnerability_ids'],
        vulnerability_names=ctx.obj['vulnerability_names'],
        limit=limit,
    )
    for row in rows:
        row = hodgepodge.types.dict_to_json(row)
        click.echo(row)
