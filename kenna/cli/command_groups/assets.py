from kenna.api import Kenna

import click

import hodgepodge.network
import hodgepodge.click
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
    api = Kenna(**ctx.obj['kenna']['config'])
    row = api.get_asset(asset_id=asset_id)
    if row:
        hodgepodge.click.echo_as_json(row)


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

    api = Kenna(**ctx.obj['kenna']['config'])
    for row in api.iter_assets(
        asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids),
        asset_group_ids=hodgepodge.click.str_to_list_of_int(asset_group_ids),
        asset_group_names=hodgepodge.click.str_to_list_of_str(asset_group_names),
        asset_tags=hodgepodge.click.str_to_list_of_str(asset_tags),
        asset_hostnames=hodgepodge.click.str_to_list_of_str(asset_hostnames),
        asset_ip_addresses=hodgepodge.click.str_to_list_of_str(asset_ip_addresses),
        asset_mac_addresses=hodgepodge.click.str_to_list_of_str(asset_mac_addresses),
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
        hodgepodge.click.echo_as_json(row)


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
        max_asset_last_boot_time: str,
        limit: int):

    api = Kenna(**ctx.obj['kenna']['config'])
    rows = api.iter_assets(
        asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids),
        asset_group_ids=hodgepodge.click.str_to_list_of_int(asset_group_ids),
        asset_group_names=hodgepodge.click.str_to_list_of_str(asset_group_names),
        asset_tags=hodgepodge.click.str_to_list_of_str(asset_tags),
        asset_hostnames=hodgepodge.click.str_to_list_of_str(asset_hostnames),
        asset_ip_addresses=hodgepodge.click.str_to_list_of_str(asset_ip_addresses),
        asset_mac_addresses=hodgepodge.click.str_to_list_of_str(asset_mac_addresses),
        min_asset_risk_meter_score=min_asset_risk_meter_score,
        max_asset_risk_meter_score=max_asset_risk_meter_score,
        min_asset_first_seen_time=hodgepodge.time.to_datetime(min_asset_first_seen_time),
        max_asset_first_seen_time=hodgepodge.time.to_datetime(max_asset_first_seen_time),
        min_asset_last_seen_time=hodgepodge.time.to_datetime(min_asset_last_seen_time),
        max_asset_last_seen_time=hodgepodge.time.to_datetime(max_asset_last_seen_time),
        min_asset_last_boot_time=hodgepodge.time.to_datetime(min_asset_last_boot_time),
        max_asset_last_boot_time=hodgepodge.time.to_datetime(max_asset_last_boot_time),
        limit=limit,
    )
    count = sum(1 for _ in rows)
    click.echo(count)


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
def get_asset_hostnames(
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

    api = Kenna(**ctx.obj['kenna']['config'])
    rows = api.iter_assets(
        asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids),
        asset_group_ids=hodgepodge.click.str_to_list_of_int(asset_group_ids),
        asset_group_names=hodgepodge.click.str_to_list_of_str(asset_group_names),
        asset_tags=hodgepodge.click.str_to_list_of_str(asset_tags),
        asset_hostnames=hodgepodge.click.str_to_list_of_str(asset_hostnames),
        asset_ip_addresses=hodgepodge.click.str_to_list_of_str(asset_ip_addresses),
        asset_mac_addresses=hodgepodge.click.str_to_list_of_str(asset_mac_addresses),
        min_asset_risk_meter_score=min_asset_risk_meter_score,
        max_asset_risk_meter_score=max_asset_risk_meter_score,
        min_asset_first_seen_time=hodgepodge.time.to_datetime(min_asset_first_seen_time),
        max_asset_first_seen_time=hodgepodge.time.to_datetime(max_asset_first_seen_time),
        min_asset_last_seen_time=hodgepodge.time.to_datetime(min_asset_last_seen_time),
        max_asset_last_seen_time=hodgepodge.time.to_datetime(max_asset_last_seen_time),
        min_asset_last_boot_time=hodgepodge.time.to_datetime(min_asset_last_boot_time),
        max_asset_last_boot_time=hodgepodge.time.to_datetime(max_asset_last_boot_time),
        limit=limit,
    )
    hostnames = set(map(str.lower, filter(bool, map(lambda a: a['hostname'], rows))))
    hodgepodge.click.echo_as_json(sorted(hostnames))


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
def get_asset_ip_addresses(
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

    api = Kenna(**ctx.obj['kenna']['config'])
    rows = api.iter_assets(
        asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids),
        asset_group_ids=hodgepodge.click.str_to_list_of_int(asset_group_ids),
        asset_group_names=hodgepodge.click.str_to_list_of_str(asset_group_names),
        asset_tags=hodgepodge.click.str_to_list_of_str(asset_tags),
        asset_hostnames=hodgepodge.click.str_to_list_of_str(asset_hostnames),
        asset_ip_addresses=hodgepodge.click.str_to_list_of_str(asset_ip_addresses),
        asset_mac_addresses=hodgepodge.click.str_to_list_of_str(asset_mac_addresses),
        min_asset_risk_meter_score=min_asset_risk_meter_score,
        max_asset_risk_meter_score=max_asset_risk_meter_score,
        min_asset_first_seen_time=hodgepodge.time.to_datetime(min_asset_first_seen_time),
        max_asset_first_seen_time=hodgepodge.time.to_datetime(max_asset_first_seen_time),
        min_asset_last_seen_time=hodgepodge.time.to_datetime(min_asset_last_seen_time),
        max_asset_last_seen_time=hodgepodge.time.to_datetime(max_asset_last_seen_time),
        min_asset_last_boot_time=hodgepodge.time.to_datetime(min_asset_last_boot_time),
        max_asset_last_boot_time=hodgepodge.time.to_datetime(max_asset_last_boot_time),
        limit=limit,
    )
    ips = set(filter(bool, map(lambda a: a['ip_address'] or a['ipv6'], rows)))
    hodgepodge.click.echo_as_json(sorted(ips))


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
def get_asset_mac_addresses(
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

    api = Kenna(**ctx.obj['kenna']['config'])
    rows = api.iter_assets(
        asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids),
        asset_group_ids=hodgepodge.click.str_to_list_of_int(asset_group_ids),
        asset_group_names=hodgepodge.click.str_to_list_of_str(asset_group_names),
        asset_tags=hodgepodge.click.str_to_list_of_str(asset_tags),
        asset_hostnames=hodgepodge.click.str_to_list_of_str(asset_hostnames),
        asset_ip_addresses=hodgepodge.click.str_to_list_of_str(asset_ip_addresses),
        asset_mac_addresses=hodgepodge.click.str_to_list_of_str(asset_mac_addresses),
        min_asset_risk_meter_score=min_asset_risk_meter_score,
        max_asset_risk_meter_score=max_asset_risk_meter_score,
        min_asset_first_seen_time=hodgepodge.time.to_datetime(min_asset_first_seen_time),
        max_asset_first_seen_time=hodgepodge.time.to_datetime(max_asset_first_seen_time),
        min_asset_last_seen_time=hodgepodge.time.to_datetime(min_asset_last_seen_time),
        max_asset_last_seen_time=hodgepodge.time.to_datetime(max_asset_last_seen_time),
        min_asset_last_boot_time=hodgepodge.time.to_datetime(min_asset_last_boot_time),
        max_asset_last_boot_time=hodgepodge.time.to_datetime(max_asset_last_boot_time),
        limit=limit,
    )
    macs = set(map(hodgepodge.network.parse_mac_address, filter(bool, map(lambda row: row['mac_address'], rows))))
    hodgepodge.click.echo_as_json(sorted(macs))
