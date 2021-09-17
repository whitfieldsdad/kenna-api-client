from kenna.api import Kenna

import click
import hodgepodge.types
import hodgepodge.click


@click.group()
@click.option('--asset-ids')
@click.option('--asset-names')
@click.pass_context
def assets(ctx, asset_ids: str, asset_names: str):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    ctx.obj.update({
        'asset_ids': hodgepodge.click.str_to_list_of_int(asset_ids),
        'asset_names': hodgepodge.click.str_to_list_of_str(asset_names),
    })


@assets.command()
@click.pass_context
def count_assets(ctx):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_assets(
        asset_ids=ctx.obj['asset_ids'],
        asset_names=ctx.obj['asset_names'],
    )
    n = sum(1 for _ in rows)
    click.echo(n)


@assets.command()
@click.option('--limit', type=int)
@click.pass_context
def get_assets(ctx, limit):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_assets(
        asset_ids=ctx.obj['asset_ids'],
        asset_names=ctx.obj['asset_names'],
        limit=limit,
    )
    for row in rows:
        row = hodgepodge.types.dict_to_json(row)
        click.echo(row)
