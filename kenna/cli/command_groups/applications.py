from kenna.api import Kenna

import kenna.cli.click as click


@click.group()
@click.pass_context
def applications(_):
    pass


@applications.command()
@click.option('--application-id', type=int, required=True)
@click.pass_context
def get_application(ctx: click.Context, application_id: int):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    row = api.get_application(application_id=application_id)
    if row:
        click.echo(row, **ctx.obj['config']['kenna']['cli'])


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

    api = Kenna(**ctx.obj['config']['kenna']['api'])
    for row in api.iter_applications(
        application_ids=click.str_to_ints(application_ids),
        application_names=click.str_to_strs(application_names),
        application_owners=click.str_to_strs(application_owners),
        application_teams=click.str_to_strs(application_teams),
        application_business_units=click.str_to_strs(application_business_units),
        min_application_risk_meter_score=min_application_risk_meter_score,
        max_application_risk_meter_score=max_application_risk_meter_score,
        min_asset_count=min_asset_count,
        max_asset_count=max_asset_count,
        min_vulnerability_count=min_vulnerability_count,
        max_vulnerability_count=max_vulnerability_count,
        limit=limit,
    ):
        click.echo(row, **ctx.obj['config']['kenna']['cli'])


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
        max_vulnerability_count: int):

    api = Kenna(**ctx.obj['config']['kenna']['api'])
    n = api.count_applications(
        application_ids=click.str_to_ints(application_ids),
        application_names=click.str_to_strs(application_names),
        application_owners=click.str_to_strs(application_owners),
        application_teams=click.str_to_strs(application_teams),
        application_business_units=click.str_to_strs(application_business_units),
        min_application_risk_meter_score=min_application_risk_meter_score,
        max_application_risk_meter_score=max_application_risk_meter_score,
        min_asset_count=min_asset_count,
        max_asset_count=max_asset_count,
        min_vulnerability_count=min_vulnerability_count,
        max_vulnerability_count=max_vulnerability_count,
    )
    click.echo(n)


@applications.command()
@click.option('--application-ids', required=True)
@click.pass_context
def delete_applications(ctx: click.Context, application_ids: str):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    application_ids = [row['id'] for row in api.iter_applications(application_ids=click.str_to_ints(application_ids))]
    if application_ids:
        api.delete_applications(application_ids)
