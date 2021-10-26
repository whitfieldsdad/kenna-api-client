from kenna.api import Kenna

import kenna.cli.click as click
import hodgepodge.networking
import hodgepodge.types
import hodgepodge.time


@click.group()
@click.pass_context
def assets(_):
    pass


@assets.command()
@click.option('--asset-id', type=int, required=True)
@click.pass_context
def get_asset(ctx: click.Context, asset_id: int):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    row = api.get_asset(asset_id=asset_id)
    if row:
        click.echo(row, **ctx.obj['config']['kenna']['cli'])


@assets.command()
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
@click.option('--limit', type=int)
@click.pass_context
def get_assets(
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
        max_asset_last_boot_time: str,
        limit: int):

    api = Kenna(**ctx.obj['config']['kenna']['api'])
    for row in api.iter_assets(
        asset_ids=click.str_to_ints(asset_ids),
        asset_group_ids=click.str_to_ints(asset_group_ids),
        asset_group_names=click.str_to_strs(asset_group_names),
        asset_tags=click.str_to_strs(asset_tags),
        asset_hostnames=click.str_to_strs(asset_hostnames),
        asset_ip_addresses=click.str_to_strs(asset_ip_addresses),
        asset_mac_addresses=click.str_to_strs(asset_mac_addresses),
        min_asset_risk_meter_score=min_asset_risk_meter_score,
        max_asset_risk_meter_score=max_asset_risk_meter_score,
        min_asset_first_seen_time=hodgepodge.time.to_datetime(min_asset_first_seen_time),
        max_asset_first_seen_time=hodgepodge.time.to_datetime(max_asset_first_seen_time),
        min_asset_last_seen_time=hodgepodge.time.to_datetime(min_asset_last_seen_time),
        max_asset_last_seen_time=hodgepodge.time.to_datetime(max_asset_last_seen_time),
        min_asset_last_boot_time=hodgepodge.time.to_datetime(min_asset_last_boot_time),
        max_asset_last_boot_time=hodgepodge.time.to_datetime(max_asset_last_boot_time),
        limit=limit,
    ):
        click.echo(row, **ctx.obj['config']['kenna']['cli'])


@assets.command()
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
def count_assets(
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

    api = Kenna(**ctx.obj['config']['kenna']['api'])
    n = api.count_assets(
        asset_ids=click.str_to_ints(asset_ids),
        asset_group_ids=click.str_to_ints(asset_group_ids),
        asset_group_names=click.str_to_strs(asset_group_names),
        asset_tags=click.str_to_strs(asset_tags),
        asset_hostnames=click.str_to_strs(asset_hostnames),
        asset_ip_addresses=click.str_to_strs(asset_ip_addresses),
        asset_mac_addresses=click.str_to_strs(asset_mac_addresses),
        min_asset_risk_meter_score=min_asset_risk_meter_score,
        max_asset_risk_meter_score=max_asset_risk_meter_score,
        min_asset_first_seen_time=hodgepodge.time.to_datetime(min_asset_first_seen_time),
        max_asset_first_seen_time=hodgepodge.time.to_datetime(max_asset_first_seen_time),
        min_asset_last_seen_time=hodgepodge.time.to_datetime(min_asset_last_seen_time),
        max_asset_last_seen_time=hodgepodge.time.to_datetime(max_asset_last_seen_time),
        min_asset_last_boot_time=hodgepodge.time.to_datetime(min_asset_last_boot_time),
        max_asset_last_boot_time=hodgepodge.time.to_datetime(max_asset_last_boot_time),
    )
    click.echo(n)


@assets.command()
@click.option('--asset-ids', required=True)
@click.option('--tags', required=True)
@click.pass_context
def tag(ctx: click.Context, asset_ids: str, tags: str):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    api.tag_assets(asset_ids=click.str_to_ints(asset_ids), tags=click.str_to_strs(tags))


@assets.command()
@click.option('--asset-ids', required=True)
@click.option('--tags', required=True)
@click.pass_context
def untag(ctx: click.Context, asset_ids: str, tags: str):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    api.untag_assets(asset_ids=click.str_to_ints(asset_ids), tags=click.str_to_strs(tags))


@assets.command()
@click.option('--asset-ids', required=True)
@click.pass_context
def reset_tags(ctx: click.Context, asset_ids: str):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    api.reset_asset_tags(asset_ids=click.str_to_ints(asset_ids))
