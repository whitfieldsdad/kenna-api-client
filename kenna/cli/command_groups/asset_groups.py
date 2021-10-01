from kenna.api import Kenna

import click

import hodgepodge.click
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
    api = Kenna(**ctx.obj['kenna']['config'])
    row = api.get_asset_group(asset_group_id=asset_group_id)
    if row:
        hodgepodge.click.echo_as_json(row)


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

    api = Kenna(**ctx.obj['kenna']['config'])
    for row in api.get_asset_groups(
        asset_group_ids=hodgepodge.click.str_to_list_of_int(asset_group_ids),
        asset_group_names=hodgepodge.click.str_to_list_of_str(asset_group_names),
        asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids),
        asset_tags=hodgepodge.click.str_to_list_of_str(asset_tags),
        asset_hostnames=hodgepodge.click.str_to_list_of_str(asset_hostnames),
        asset_ip_addresses=hodgepodge.click.str_to_list_of_str(asset_ip_addresses),
        asset_mac_addresses=hodgepodge.click.str_to_list_of_str(asset_mac_addresses),
        min_asset_group_create_time=hodgepodge.time.to_datetime(min_asset_group_create_time),
        max_asset_group_create_time=hodgepodge.time.to_datetime(max_asset_group_create_time),
        min_asset_group_last_update_time=hodgepodge.time.to_datetime(min_asset_group_last_update_time),
        max_asset_group_last_update_time=hodgepodge.time.to_datetime(max_asset_group_last_update_time),
        limit=limit,
    ):
        hodgepodge.click.echo_as_json(row)


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
        max_asset_group_last_update_time: str,
        limit: int):

    api = Kenna(**ctx.obj['kenna']['config'])
    rows = api.get_asset_groups(
        asset_group_ids=hodgepodge.click.str_to_list_of_int(asset_group_ids),
        asset_group_names=hodgepodge.click.str_to_list_of_str(asset_group_names),
        asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids),
        asset_tags=hodgepodge.click.str_to_list_of_str(asset_tags),
        asset_hostnames=hodgepodge.click.str_to_list_of_str(asset_hostnames),
        asset_ip_addresses=hodgepodge.click.str_to_list_of_str(asset_ip_addresses),
        asset_mac_addresses=hodgepodge.click.str_to_list_of_str(asset_mac_addresses),
        min_asset_group_create_time=hodgepodge.time.to_datetime(min_asset_group_create_time),
        max_asset_group_create_time=hodgepodge.time.to_datetime(max_asset_group_create_time),
        min_asset_group_last_update_time=hodgepodge.time.to_datetime(min_asset_group_last_update_time),
        max_asset_group_last_update_time=hodgepodge.time.to_datetime(max_asset_group_last_update_time),
        limit=limit,
    )
    count = sum(1 for _ in rows)
    click.echo(count)
