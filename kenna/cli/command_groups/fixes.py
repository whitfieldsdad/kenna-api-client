from kenna.api import Kenna

import click
import hodgepodge.types
import hodgepodge.click
import json


@click.group()
@click.option('--fix-ids')
@click.option('--fix-names')
@click.pass_context
def fixes(ctx, fix_ids: str, fix_names: str):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    ctx.obj.update({
        'fix_ids': hodgepodge.click.str_to_list_of_int(fix_ids),
        'fix_names': hodgepodge.click.str_to_list_of_str(fix_names),
    })


@fixes.command()
@click.pass_context
def count_fixes(ctx):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_fixes(
        fix_ids=ctx.obj['fix_ids'],
        fix_names=ctx.obj['fix_names'],
    )
    n = sum(1 for _ in rows)
    click.echo(n)


@fixes.command()
@click.option('--limit', type=int)
@click.pass_context
def get_fixes(ctx, limit):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_fixes(
        fix_ids=ctx.obj['fix_ids'],
        fix_names=ctx.obj['fix_names'],
        limit=limit,
    )
    for row in rows:
        row = hodgepodge.types.dict_to_json(row)
        click.echo(row)
