import click

import hodgepodge.click
import hodgepodge.types


@click.group()
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
def asset_groups(
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

    ctx.obj['kwargs'] = {
        'asset_group_ids': hodgepodge.click.str_to_list_of_int(asset_group_ids),
        'asset_group_names': hodgepodge.click.str_to_list_of_str(asset_group_names),
        'asset_ids': hodgepodge.click.str_to_list_of_int(asset_ids),
        'asset_tags': hodgepodge.click.str_to_list_of_str(asset_tags),
        'asset_hostnames': hodgepodge.click.str_to_list_of_str(asset_hostnames),
        'asset_ip_addresses': hodgepodge.click.str_to_list_of_str(asset_ip_addresses),
        'asset_mac_addresses': hodgepodge.click.str_to_list_of_str(asset_mac_addresses),
        'min_asset_group_create_time': min_asset_group_create_time,
        'max_asset_group_create_time': max_asset_group_create_time,
        'min_asset_group_last_update_time': min_asset_group_last_update_time,
        'max_asset_group_last_update_time': max_asset_group_last_update_time,
    }


@asset_groups.command()
@click.option('--limit', type=int)
@click.pass_context
def get_asset_groups(ctx: click.Context, limit: int):
    rows = ctx.obj['kenna_api'].iter_asset_groups(**ctx.obj['kwargs'], limit=limit)
    hodgepodge.click.echo_as_jsonl(rows)
