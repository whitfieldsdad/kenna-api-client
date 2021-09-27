import click

import hodgepodge.click
import hodgepodge.types


@click.group()
@click.option('--asset-ids')
@click.option('--asset-group-ids')
@click.option('--asset-group-names')
@click.option('--asset-tags')
@click.option('--asset-hostnames')
@click.option('--asset-ip-addresses')
@click.option('--asset-mac-addresses')
@click.option('--min-asset-risk-meter-score', type=int)
@click.option('--max-asset-risk-meter-score', type=int)
@click.option('--min-asset-first-seen-time')
@click.option('--max-asset-first-seen-time')
@click.option('--min-asset-last-seen-time')
@click.option('--max-asset-last-seen-time')
@click.option('--min-asset-last-boot-time')
@click.option('--max-asset-last-boot-time')
@click.pass_context
def assets(
        ctx: click.Context,
        asset_ids: str,
        asset_group_ids: str,
        asset_group_names: str,
        asset_tags: str,
        asset_hostnames: str,
        asset_ip_addresses: str,
        asset_mac_addresses: str,
        min_asset_risk_meter_score: int,
        max_asset_risk_meter_score: int,
        min_asset_first_seen_time: str,
        max_asset_first_seen_time: str,
        min_asset_last_seen_time: str,
        max_asset_last_seen_time: str,
        min_asset_last_boot_time: str,
        max_asset_last_boot_time: str):

    ctx.obj['kwargs'] = {
        'asset_ids': hodgepodge.click.str_to_list_of_int(asset_ids),
        'asset_group_ids': hodgepodge.click.str_to_list_of_int(asset_group_ids),
        'asset_group_names': hodgepodge.click.str_to_list_of_str(asset_group_names),
        'asset_tags': hodgepodge.click.str_to_list_of_str(asset_tags),
        'asset_hostnames': hodgepodge.click.str_to_list_of_str(asset_hostnames),
        'asset_ip_addresses': hodgepodge.click.str_to_list_of_str(asset_ip_addresses),
        'asset_mac_addresses': hodgepodge.click.str_to_list_of_str(asset_mac_addresses),
        'min_asset_risk_meter_score': min_asset_risk_meter_score,
        'max_asset_risk_meter_score': max_asset_risk_meter_score,
        'min_asset_first_seen_time': min_asset_first_seen_time,
        'max_asset_first_seen_time': max_asset_first_seen_time,
        'min_asset_last_seen_time': min_asset_last_seen_time,
        'max_asset_last_seen_time': max_asset_last_seen_time,
        'min_asset_last_boot_time': min_asset_last_boot_time,
        'max_asset_last_boot_time': max_asset_last_boot_time,
    }


@assets.command()
@click.option('--limit', type=int)
@click.pass_context
def get_assets(ctx: click.Context, limit: int):
    rows = ctx.obj['kenna_api'].iter_assets(**ctx.obj['kwargs'], limit=limit)
    hodgepodge.click.echo_as_jsonl(rows)
