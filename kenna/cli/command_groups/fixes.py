from kenna.api import Kenna

import kenna.cli.click as click
import hodgepodge.time


@click.group()
@click.pass_context
def fixes(_):
    pass


@fixes.command()
@click.option('--fix-id', type=int, required=True)
@click.pass_context
def get_fix(ctx: click.Context, fix_id: int):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    row = api.get_fix(fix_id=fix_id)
    if row:
        click.echo(row, **ctx.obj['config']['kenna']['cli'])


@fixes.command()
@click.option('--fix-ids')
@click.option('--fix-names')
@click.option('--fix-vendors')
@click.option('--cve-ids')
@click.option('--asset-ids')
@click.option('--asset-hostnames')
@click.option('--asset-ip-addresses')
@click.option('--asset-mac-addresses')
@click.option('--asset-ip-addresses')
@click.option('--asset-mac-addresses')
@click.option('--asset-group-ids')
@click.option('--asset-group-names')
@click.option('--asset-tags')
@click.option('--min-fix-create-time')
@click.option('--max-fix-create-time')
@click.option('--min-fix-last-update-time')
@click.option('--max-fix-last-update-time')
@click.option('--limit', type=int)
@click.pass_context
def get_fixes(
        ctx: click.Context,
        fix_ids: str,
        fix_names: str,
        fix_vendors: str,
        cve_ids: str,
        asset_ids: str,
        asset_hostnames: str,
        asset_ip_addresses: str,
        asset_mac_addresses: str,
        asset_group_ids: str,
        asset_group_names: str,
        asset_tags: str,
        min_fix_create_time: str,
        max_fix_create_time: str,
        min_fix_last_update_time: str,
        max_fix_last_update_time: str,
        limit: int):

    api = Kenna(**ctx.obj['config']['kenna']['api'])
    for row in api.iter_fixes(
        fix_ids=click.str_to_ints(fix_ids),
        fix_names=click.str_to_strs(fix_names),
        fix_vendors=click.str_to_strs(fix_vendors),
        cve_ids=click.str_to_strs(cve_ids),
        asset_ids=click.str_to_ints(asset_ids),
        asset_hostnames=click.str_to_strs(asset_hostnames),
        asset_ip_addresses=click.str_to_strs(asset_ip_addresses),
        asset_mac_addresses=click.str_to_strs(asset_mac_addresses),
        asset_group_ids=click.str_to_ints(asset_group_ids),
        asset_group_names=click.str_to_strs(asset_group_names),
        asset_tags=click.str_to_strs(asset_tags),
        min_fix_create_time=hodgepodge.time.to_datetime(min_fix_create_time),
        max_fix_create_time=hodgepodge.time.to_datetime(max_fix_create_time),
        min_fix_last_update_time=hodgepodge.time.to_datetime(min_fix_last_update_time),
        max_fix_last_update_time=hodgepodge.time.to_datetime(max_fix_last_update_time),
        limit=limit,
    ):
        click.echo(row, **ctx.obj['config']['kenna']['cli'])


@fixes.command()
@click.option('--fix-ids')
@click.option('--fix-names')
@click.option('--fix-vendors')
@click.option('--cve-ids')
@click.option('--asset-ids')
@click.option('--asset-hostnames')
@click.option('--asset-ip-addresses')
@click.option('--asset-mac-addresses')
@click.option('--asset-ip-addresses')
@click.option('--asset-mac-addresses')
@click.option('--asset-group-ids')
@click.option('--asset-group-names')
@click.option('--asset-tags')
@click.option('--min-fix-create-time')
@click.option('--max-fix-create-time')
@click.option('--min-fix-last-update-time')
@click.option('--max-fix-last-update-time')
@click.pass_context
def count_fixes(
        ctx: click.Context,
        fix_ids: str,
        fix_names: str,
        fix_vendors: str,
        cve_ids: str,
        asset_ids: str,
        asset_hostnames: str,
        asset_ip_addresses: str,
        asset_mac_addresses: str,
        asset_group_ids: str,
        asset_group_names: str,
        asset_tags: str,
        min_fix_create_time: str,
        max_fix_create_time: str,
        min_fix_last_update_time: str,
        max_fix_last_update_time: str):

    api = Kenna(**ctx.obj['config']['kenna']['api'])
    n = api.count_fixes(
        fix_ids=click.str_to_ints(fix_ids),
        fix_names=click.str_to_strs(fix_names),
        fix_vendors=click.str_to_strs(fix_vendors),
        cve_ids=click.str_to_strs(cve_ids),
        asset_ids=click.str_to_ints(asset_ids),
        asset_hostnames=click.str_to_strs(asset_hostnames),
        asset_ip_addresses=click.str_to_strs(asset_ip_addresses),
        asset_mac_addresses=click.str_to_strs(asset_mac_addresses),
        asset_group_ids=click.str_to_ints(asset_group_ids),
        asset_group_names=click.str_to_strs(asset_group_names),
        asset_tags=click.str_to_strs(asset_tags),
        min_fix_create_time=hodgepodge.time.to_datetime(min_fix_create_time),
        max_fix_create_time=hodgepodge.time.to_datetime(max_fix_create_time),
        min_fix_last_update_time=hodgepodge.time.to_datetime(min_fix_last_update_time),
        max_fix_last_update_time=hodgepodge.time.to_datetime(max_fix_last_update_time),
    )
    click.echo(n)
