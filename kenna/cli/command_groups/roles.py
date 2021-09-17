from kenna.api import Kenna

import click
import hodgepodge.types
import hodgepodge.click
import json


@click.group()
@click.option('--role-ids')
@click.option('--role-names')
@click.pass_context
def roles(ctx, role_ids: str, role_names: str):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    ctx.obj.update({
        'role_ids': hodgepodge.click.str_to_list_of_int(role_ids),
        'role_names': hodgepodge.click.str_to_list_of_str(role_names),
    })


@roles.command()
@click.pass_context
def count_roles(ctx):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_roles(
        role_ids=ctx.obj['role_ids'],
        role_names=ctx.obj['role_names'],
    )
    n = sum(1 for _ in rows)
    click.echo(n)


@roles.command()
@click.option('--limit', type=int)
@click.pass_context
def get_roles(ctx, limit):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_roles(
        role_ids=ctx.obj['role_ids'],
        role_names=ctx.obj['role_names'],
        limit=limit,
    )
    for row in rows:
        row = hodgepodge.types.dict_to_json(row)
        click.echo(row)
