from kenna.api import Kenna

import click
import hodgepodge.types
import hodgepodge.click
import json


@click.group()
@click.option('--user-ids')
@click.option('--user-names')
@click.pass_context
def users(ctx, user_ids: str, user_names: str):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    ctx.obj.update({
        'user_ids': hodgepodge.click.str_to_list_of_int(user_ids),
        'user_names': hodgepodge.click.str_to_list_of_str(user_names),
    })


@users.command()
@click.pass_context
def count_users(ctx):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_users(
        user_ids=ctx.obj['user_ids'],
        user_names=ctx.obj['user_names'],
    )
    n = sum(1 for _ in rows)
    click.echo(n)


@users.command()
@click.option('--limit', type=int)
@click.pass_context
def get_users(ctx, limit):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_users(
        user_ids=ctx.obj['user_ids'],
        user_names=ctx.obj['user_names'],
        limit=limit,
    )
    for row in rows:
        row = hodgepodge.types.dict_to_json(row)
        click.echo(row)
