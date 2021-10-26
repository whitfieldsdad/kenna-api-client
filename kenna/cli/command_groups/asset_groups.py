from kenna.api import Kenna

import kenna.cli.click as click
import hodgepodge.types
import hodgepodge.time


@click.group()
@click.pass_context
def asset_groups(_):
    pass


@asset_groups.command()
@click.option('--asset-group-id', type=int, required=True)
@click.pass_context
def get_asset_group(ctx: click.Context, asset_group_id: int):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    row = api.get_asset_group(asset_group_id=asset_group_id)
    if row:
        click.echo(row, **ctx.obj['config']['kenna']['cli'])


@asset_groups.command()
@click.option('--asset-group-ids')
@click.option('--asset-group-names')
@click.option('--asset-ids')
@click.option('--asset-tags')
@click.option('--asset-hostnames')
@click.option('--asset-ip-addresses')
@click.option('--asset-mac-addresses')
@click.option('--min-asset-group-create-time')
@click.option('--max-asset-group-create-time')
@click.option('--min-asset-group-last-update-time')
@click.option('--max-asset-group-last-update-time')
@click.option('--limit', type=int)
@click.pass_context
def get_asset_groups(
        ctx: click.Context,
        asset_group_ids: str,
        asset_group_names: str,
        asset_ids: str,
        asset_tags: str,
        asset_hostnames: str,
        asset_ip_addresses: str,
        asset_mac_addresses: str,
        min_asset_group_create_time: str,
        max_asset_group_create_time: str,
        min_asset_group_last_update_time: str,
        max_asset_group_last_update_time: str,
        limit: int):

    api = Kenna(**ctx.obj['config']['kenna']['api'])
    for row in api.iter_asset_groups(
        asset_group_ids=click.str_to_ints(asset_group_ids),
        asset_group_names=click.str_to_strs(asset_group_names),
        asset_ids=click.str_to_ints(asset_ids),
        asset_tags=click.str_to_strs(asset_tags),
        asset_hostnames=click.str_to_strs(asset_hostnames),
        asset_ip_addresses=click.str_to_strs(asset_ip_addresses),
        asset_mac_addresses=click.str_to_strs(asset_mac_addresses),
        min_asset_group_create_time=hodgepodge.time.to_datetime(min_asset_group_create_time),
        max_asset_group_create_time=hodgepodge.time.to_datetime(max_asset_group_create_time),
        min_asset_group_last_update_time=hodgepodge.time.to_datetime(min_asset_group_last_update_time),
        max_asset_group_last_update_time=hodgepodge.time.to_datetime(max_asset_group_last_update_time),
        limit=limit,
    ):
        click.echo(row, **ctx.obj['config']['kenna']['cli'])


@asset_groups.command()
@click.option('--asset-group-ids')
@click.option('--asset-group-names')
@click.option('--asset-ids')
@click.option('--asset-tags')
@click.option('--asset-hostnames')
@click.option('--asset-ip-addresses')
@click.option('--asset-mac-addresses')
@click.option('--min-asset-group-create-time')
@click.option('--max-asset-group-create-time')
@click.option('--min-asset-group-last-update-time')
@click.option('--max-asset-group-last-update-time')
@click.pass_context
def count_asset_groups(
        ctx: click.Context,
        asset_group_ids: str,
        asset_group_names: str,
        asset_ids: str,
        asset_tags: str,
        asset_hostnames: str,
        asset_ip_addresses: str,
        asset_mac_addresses: str,
        min_asset_group_create_time: str,
        max_asset_group_create_time: str,
        min_asset_group_last_update_time: str,
        max_asset_group_last_update_time: str):

    api = Kenna(**ctx.obj['config']['kenna']['api'])
    n = api.count_asset_groups(
        asset_group_ids=click.str_to_ints(asset_group_ids),
        asset_group_names=click.str_to_strs(asset_group_names),
        asset_ids=click.str_to_ints(asset_ids),
        asset_tags=click.str_to_strs(asset_tags),
        asset_hostnames=click.str_to_strs(asset_hostnames),
        asset_ip_addresses=click.str_to_strs(asset_ip_addresses),
        asset_mac_addresses=click.str_to_strs(asset_mac_addresses),
        min_asset_group_create_time=hodgepodge.time.to_datetime(min_asset_group_create_time),
        max_asset_group_create_time=hodgepodge.time.to_datetime(max_asset_group_create_time),
        min_asset_group_last_update_time=hodgepodge.time.to_datetime(min_asset_group_last_update_time),
        max_asset_group_last_update_time=hodgepodge.time.to_datetime(max_asset_group_last_update_time),
    )
    click.echo(n)


@asset_groups.command()
@click.option('--asset-group-ids', required=True)
@click.pass_context
def delete_asset_groups(ctx: click.Context, asset_group_ids: str):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    asset_group_ids = [row['id'] for row in api.iter_asset_groups(asset_group_ids=click.str_to_ints(asset_group_ids))]
    if asset_group_ids:
        api.delete_asset_groups(asset_group_ids)
