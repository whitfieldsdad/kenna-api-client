import click
import hodgepodge.types
import hodgepodge.click
from kenna.api import Kenna


@click.group()
@click.pass_context
def assets(_):
    pass


@assets.command()
@click.option('--asset-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def count_assets(ctx, asset_ids: str, limit: int):
    """
    Count matching assets.
    """
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    apps = api.iter_assets(asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids), limit=limit)
    count = sum(1 for _ in apps)
    click.echo(count)


@assets.command()
@click.option('--asset-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_assets(ctx, asset_ids: str, limit: int):
    """
    Lookup one or more assets.
    """
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    for app in api.iter_assets(asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids), limit=limit):
        app = hodgepodge.types.dict_to_json(app)
        click.echo(app)


@assets.command()
@click.option('--asset-id', required=True, type=int)
@click.pass_context
def get_asset(ctx, asset_id: int):
    """
    Lookup a single asset.
    """
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    app = api.get_asset(asset_id=asset_id)
    if app:
        app = hodgepodge.types.dict_to_json(app)
        click.echo(app)
