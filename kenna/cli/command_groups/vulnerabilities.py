from kenna.api import Kenna

import click

import hodgepodge.time
import hodgepodge.click
import hodgepodge.types


@click.group()
@click.pass_context
def vulnerabilities(_):
    pass


@vulnerabilities.command()
@click.option('--vulnerability-id', type=int, required=True)
@click.pass_context
def get_vulnerability(ctx: click.Context, vulnerability_id: int):
    api = Kenna(**ctx.obj['kenna']['config'])
    row = api.get_vulnerability(vulnerability_id=vulnerability_id)
    if row:
        hodgepodge.click.echo_as_json(row)


@vulnerabilities.command()
@click.option('--vulnerability-ids')
@click.option('--cve-ids')
@click.option('--fix-ids')
@click.option('--fix-names')
@click.option('--fix-vendors')
@click.option('--asset-ids')
@click.option('--asset-hostnames')
@click.option('--asset-ip-addresses')
@click.option('--asset-mac-addresses')
@click.option('--asset-group-ids')
@click.option('--asset-group-names')
@click.option('--asset-tags')
@click.option('--min-vulnerability-risk-meter-score', type=int)
@click.option('--max-vulnerability-risk-meter-score', type=int)
@click.option('--min-vulnerability-first-seen-time')
@click.option('--max-vulnerability-first-seen-time')
@click.option('--min-vulnerability-last-seen-time')
@click.option('--max-vulnerability-last-seen-time')
@click.option('--min-cve-publish-time')
@click.option('--max-cve-publish-time')
@click.option('--min-patch-publish-time')
@click.option('--max-patch-publish-time')
@click.option('--min-patch-due-date')
@click.option('--max-patch-due-date')
@click.option('--limit', type=int)
@click.pass_context
def get_vulnerabilities(
        ctx: click.Context,
        vulnerability_ids: str,
        cve_ids: str,
        fix_ids: str,
        fix_names: str,
        fix_vendors: str,
        asset_ids: str,
        asset_hostnames: str,
        asset_ip_addresses: str,
        asset_mac_addresses: str,
        asset_group_ids: str,
        asset_group_names: str,
        asset_tags: str,
        min_vulnerability_risk_meter_score: int,
        max_vulnerability_risk_meter_score: int,
        min_vulnerability_first_seen_time: str,
        max_vulnerability_first_seen_time: str,
        min_vulnerability_last_seen_time: str,
        max_vulnerability_last_seen_time: str,
        min_cve_publish_time: str,
        max_cve_publish_time: str,
        min_patch_publish_time: str,
        max_patch_publish_time: str,
        min_patch_due_date: str,
        max_patch_due_date: str,
        limit: int):

    api = Kenna(**ctx.obj['kenna']['config'])
    for row in api.get_vulnerabilities(
        vulnerability_ids=hodgepodge.click.str_to_list_of_int(vulnerability_ids),
        cve_ids=hodgepodge.click.str_to_list_of_str(cve_ids),
        fix_ids=hodgepodge.click.str_to_list_of_int(fix_ids),
        fix_names=hodgepodge.click.str_to_list_of_str(fix_names),
        fix_vendors=hodgepodge.click.str_to_list_of_str(fix_vendors),
        asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids),
        asset_hostnames=hodgepodge.click.str_to_list_of_str(asset_hostnames),
        asset_ip_addresses=hodgepodge.click.str_to_list_of_str(asset_ip_addresses),
        asset_mac_addresses=hodgepodge.click.str_to_list_of_str(asset_mac_addresses),
        asset_group_ids=hodgepodge.click.str_to_list_of_int(asset_group_ids),
        asset_group_names=hodgepodge.click.str_to_list_of_str(asset_group_names),
        asset_tags=hodgepodge.click.str_to_list_of_str(asset_tags),
        min_vulnerability_risk_meter_score=min_vulnerability_risk_meter_score,
        max_vulnerability_risk_meter_score=max_vulnerability_risk_meter_score,
        min_vulnerability_first_seen_time=hodgepodge.time.to_datetime(min_vulnerability_first_seen_time),
        max_vulnerability_first_seen_time=hodgepodge.time.to_datetime(max_vulnerability_first_seen_time),
        min_vulnerability_last_seen_time=hodgepodge.time.to_datetime(min_vulnerability_last_seen_time),
        max_vulnerability_last_seen_time=hodgepodge.time.to_datetime(max_vulnerability_last_seen_time),
        min_cve_publish_time=hodgepodge.time.to_datetime(min_cve_publish_time),
        max_cve_publish_time=hodgepodge.time.to_datetime(max_cve_publish_time),
        min_patch_publish_time=hodgepodge.time.to_datetime(min_patch_publish_time),
        max_patch_publish_time=hodgepodge.time.to_datetime(max_patch_publish_time),
        min_patch_due_date=hodgepodge.time.to_datetime(min_patch_due_date),
        max_patch_due_date=hodgepodge.time.to_datetime(max_patch_due_date),
        limit=limit,
    ):
        hodgepodge.click.echo_as_json(row)


@vulnerabilities.command()
@click.option('--vulnerability-ids')
@click.option('--cve-ids')
@click.option('--fix-ids')
@click.option('--fix-names')
@click.option('--fix-vendors')
@click.option('--asset-ids')
@click.option('--asset-hostnames')
@click.option('--asset-ip-addresses')
@click.option('--asset-mac-addresses')
@click.option('--asset-group-ids')
@click.option('--asset-group-names')
@click.option('--asset-tags')
@click.option('--min-vulnerability-risk-meter-score', type=int)
@click.option('--max-vulnerability-risk-meter-score', type=int)
@click.option('--min-vulnerability-first-seen-time')
@click.option('--max-vulnerability-first-seen-time')
@click.option('--min-vulnerability-last-seen-time')
@click.option('--max-vulnerability-last-seen-time')
@click.option('--min-cve-publish-time')
@click.option('--max-cve-publish-time')
@click.option('--min-patch-publish-time')
@click.option('--max-patch-publish-time')
@click.option('--min-patch-due-date')
@click.option('--max-patch-due-date')
@click.option('--limit', type=int)
@click.pass_context
def get_vulnerabilities(
        ctx: click.Context,
        vulnerability_ids: str,
        cve_ids: str,
        fix_ids: str,
        fix_names: str,
        fix_vendors: str,
        asset_ids: str,
        asset_hostnames: str,
        asset_ip_addresses: str,
        asset_mac_addresses: str,
        asset_group_ids: str,
        asset_group_names: str,
        asset_tags: str,
        min_vulnerability_risk_meter_score: int,
        max_vulnerability_risk_meter_score: int,
        min_vulnerability_first_seen_time: str,
        max_vulnerability_first_seen_time: str,
        min_vulnerability_last_seen_time: str,
        max_vulnerability_last_seen_time: str,
        min_cve_publish_time: str,
        max_cve_publish_time: str,
        min_patch_publish_time: str,
        max_patch_publish_time: str,
        min_patch_due_date: str,
        max_patch_due_date: str,
        limit: int):

    api = Kenna(**ctx.obj['kenna']['config'])
    rows = api.get_vulnerabilities(
        vulnerability_ids=hodgepodge.click.str_to_list_of_int(vulnerability_ids),
        cve_ids=hodgepodge.click.str_to_list_of_str(cve_ids),
        fix_ids=hodgepodge.click.str_to_list_of_int(fix_ids),
        fix_names=hodgepodge.click.str_to_list_of_str(fix_names),
        fix_vendors=hodgepodge.click.str_to_list_of_str(fix_vendors),
        asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids),
        asset_hostnames=hodgepodge.click.str_to_list_of_str(asset_hostnames),
        asset_ip_addresses=hodgepodge.click.str_to_list_of_str(asset_ip_addresses),
        asset_mac_addresses=hodgepodge.click.str_to_list_of_str(asset_mac_addresses),
        asset_group_ids=hodgepodge.click.str_to_list_of_int(asset_group_ids),
        asset_group_names=hodgepodge.click.str_to_list_of_str(asset_group_names),
        asset_tags=hodgepodge.click.str_to_list_of_str(asset_tags),
        min_vulnerability_risk_meter_score=min_vulnerability_risk_meter_score,
        max_vulnerability_risk_meter_score=max_vulnerability_risk_meter_score,
        min_vulnerability_first_seen_time=hodgepodge.time.to_datetime(min_vulnerability_first_seen_time),
        max_vulnerability_first_seen_time=hodgepodge.time.to_datetime(max_vulnerability_first_seen_time),
        min_vulnerability_last_seen_time=hodgepodge.time.to_datetime(min_vulnerability_last_seen_time),
        max_vulnerability_last_seen_time=hodgepodge.time.to_datetime(max_vulnerability_last_seen_time),
        min_cve_publish_time=hodgepodge.time.to_datetime(min_cve_publish_time),
        max_cve_publish_time=hodgepodge.time.to_datetime(max_cve_publish_time),
        min_patch_publish_time=hodgepodge.time.to_datetime(min_patch_publish_time),
        max_patch_publish_time=hodgepodge.time.to_datetime(max_patch_publish_time),
        min_patch_due_date=hodgepodge.time.to_datetime(min_patch_due_date),
        max_patch_due_date=hodgepodge.time.to_datetime(max_patch_due_date),
        limit=limit,
    )
    count = sum(1 for _ in rows)
    click.echo(count)
