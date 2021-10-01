import click

import hodgepodge.click
import hodgepodge.types
from kenna.api import Kenna


@click.group()
@click.pass_context
def applications(_):
    pass


@applications.command()
@click.option('--application-id', type=int, required=True)
@click.pass_context
def get_application(ctx: click.Context, application_id: int):
    api = Kenna(**ctx.obj['kenna']['config'])
    row = api.get_application(application_id=application_id)
    if row:
        hodgepodge.click.echo_as_json(row)


@applications.command()
@click.option('--application-ids')
@click.option('--application-names')
@click.option('--application-owners')
@click.option('--application-teams')
@click.option('--application-business-units')
@click.option('--min-application-risk-meter-score', type=int)
@click.option('--max-application-risk-meter-score', type=int)
@click.option('--min-asset-count', type=int)
@click.option('--max-asset-count', type=int)
@click.option('--min-vulnerability-count', type=int)
@click.option('--max-vulnerability-count', type=int)
@click.option('--limit', type=int)
@click.pass_context
def get_applications(
        ctx: click.Context,
        application_ids: str,
        application_names: str,
        application_owners: str,
        application_teams: str,
        application_business_units: str,
        min_application_risk_meter_score: int,
        max_application_risk_meter_score: int,
        min_asset_count: int,
        max_asset_count: int,
        min_vulnerability_count: int,
        max_vulnerability_count: int,
        limit: int):

    api = Kenna(**ctx.obj['kenna']['config'])
    for row in api.iter_applications(
        application_ids=hodgepodge.click.str_to_list_of_int(application_ids),
        application_names=hodgepodge.click.str_to_list_of_str(application_names),
        application_owners=hodgepodge.click.str_to_list_of_str(application_owners),
        application_teams=hodgepodge.click.str_to_list_of_str(application_teams),
        application_business_units=hodgepodge.click.str_to_list_of_str(application_business_units),
        min_application_risk_meter_score=min_application_risk_meter_score,
        max_application_risk_meter_score=max_application_risk_meter_score,
        min_asset_count=min_asset_count,
        max_asset_count=max_asset_count,
        min_vulnerability_count=min_vulnerability_count,
        max_vulnerability_count=max_vulnerability_count,
        limit=limit,
    ):
        hodgepodge.click.echo_as_json(row)


@applications.command()
@click.option('--application-ids')
@click.option('--application-names')
@click.option('--application-owners')
@click.option('--application-teams')
@click.option('--application-business-units')
@click.option('--min-application-risk-meter-score', type=int)
@click.option('--max-application-risk-meter-score', type=int)
@click.option('--min-asset-count', type=int)
@click.option('--max-asset-count', type=int)
@click.option('--min-vulnerability-count', type=int)
@click.option('--max-vulnerability-count', type=int)
@click.option('--limit', type=int)
@click.pass_context
def count_applications(
        ctx: click.Context,
        application_ids: str,
        application_names: str,
        application_owners: str,
        application_teams: str,
        application_business_units: str,
        min_application_risk_meter_score: int,
        max_application_risk_meter_score: int,
        min_asset_count: int,
        max_asset_count: int,
        min_vulnerability_count: int,
        max_vulnerability_count: int,
        limit: int):

    api = Kenna(**ctx.obj['kenna']['config'])
    rows = api.iter_applications(
        application_ids=hodgepodge.click.str_to_list_of_int(application_ids),
        application_names=hodgepodge.click.str_to_list_of_str(application_names),
        application_owners=hodgepodge.click.str_to_list_of_str(application_owners),
        application_teams=hodgepodge.click.str_to_list_of_str(application_teams),
        application_business_units=hodgepodge.click.str_to_list_of_str(application_business_units),
        min_application_risk_meter_score=min_application_risk_meter_score,
        max_application_risk_meter_score=max_application_risk_meter_score,
        min_asset_count=min_asset_count,
        max_asset_count=max_asset_count,
        min_vulnerability_count=min_vulnerability_count,
        max_vulnerability_count=max_vulnerability_count,
        limit=limit,
    )
    count = sum(1 for _ in rows)
    click.echo(count)
