from kenna.api import Kenna

import hodgepodge.time
import hodgepodge.click
import click


@click.group()
@click.pass_context
def fixes(_):
    pass


@fixes.command()
@click.option('--fix-id', type=int, required=True)
@click.pass_context
def get_fix(ctx: click.Context, fix_id: int):
    api = Kenna(**ctx.obj['kenna']['config'])
    row = api.get_fix(fix_id=fix_id)
    if row:
        hodgepodge.click.echo_as_json(row)


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

    api = Kenna(**ctx.obj['kenna']['config'])
    for row in api.iter_fixes(
        fix_ids=hodgepodge.click.str_to_list_of_int(fix_ids),
        fix_names=hodgepodge.click.str_to_list_of_str(fix_names),
        fix_vendors=hodgepodge.click.str_to_list_of_str(fix_vendors),
        cve_ids=hodgepodge.click.str_to_list_of_str(cve_ids),
        asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids),
        asset_hostnames=hodgepodge.click.str_to_list_of_str(asset_hostnames),
        asset_ip_addresses=hodgepodge.click.str_to_list_of_str(asset_ip_addresses),
        asset_mac_addresses=hodgepodge.click.str_to_list_of_str(asset_mac_addresses),
        asset_group_ids=hodgepodge.click.str_to_list_of_int(asset_group_ids),
        asset_group_names=hodgepodge.click.str_to_list_of_str(asset_group_names),
        asset_tags=hodgepodge.click.str_to_list_of_str(asset_tags),
        min_fix_create_time=hodgepodge.time.to_datetime(min_fix_create_time),
        max_fix_create_time=hodgepodge.time.to_datetime(max_fix_create_time),
        min_fix_last_update_time=hodgepodge.time.to_datetime(min_fix_last_update_time),
        max_fix_last_update_time=hodgepodge.time.to_datetime(max_fix_last_update_time),
        limit=limit,
    ):
        hodgepodge.click.echo_as_json(row)


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
        max_fix_last_update_time: str,
        limit: int):

    api = Kenna(**ctx.obj['kenna']['config'])
    rows = api.iter_fixes(
        fix_ids=hodgepodge.click.str_to_list_of_int(fix_ids),
        fix_names=hodgepodge.click.str_to_list_of_str(fix_names),
        fix_vendors=hodgepodge.click.str_to_list_of_str(fix_vendors),
        cve_ids=hodgepodge.click.str_to_list_of_str(cve_ids),
        asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids),
        asset_hostnames=hodgepodge.click.str_to_list_of_str(asset_hostnames),
        asset_ip_addresses=hodgepodge.click.str_to_list_of_str(asset_ip_addresses),
        asset_mac_addresses=hodgepodge.click.str_to_list_of_str(asset_mac_addresses),
        asset_group_ids=hodgepodge.click.str_to_list_of_int(asset_group_ids),
        asset_group_names=hodgepodge.click.str_to_list_of_str(asset_group_names),
        asset_tags=hodgepodge.click.str_to_list_of_str(asset_tags),
        min_fix_create_time=hodgepodge.time.to_datetime(min_fix_create_time),
        max_fix_create_time=hodgepodge.time.to_datetime(max_fix_create_time),
        min_fix_last_update_time=hodgepodge.time.to_datetime(min_fix_last_update_time),
        max_fix_last_update_time=hodgepodge.time.to_datetime(max_fix_last_update_time),
        limit=limit,
    )
    count = sum(1 for _ in rows)
    click.echo(count)
