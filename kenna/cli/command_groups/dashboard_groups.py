from kenna.api import Kenna

import kenna.cli.click as click
import hodgepodge.types
import hodgepodge.time


@click.group()
@click.pass_context
def dashboard_groups(_):
    pass


@dashboard_groups.command()
@click.option('--dashboard-group-id', type=int, required=True)
@click.pass_context
def get_dashboard_groups(ctx: click.Context, dashboard_group_id: int):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    row = api.get_dashboard_group(dashboard_group_id=dashboard_group_id)
    if row:
        click.echo(row, **ctx.obj['config']['kenna']['cli'])


@dashboard_groups.command()
@click.option('--dashboard-group-ids')
@click.option('--dashboard-group-names')
@click.option('--role-ids')
@click.option('--role-names')
@click.option('--min-dashboard-group-create-time')
@click.option('--max-dashboard-group-create-time')
@click.option('--min-dashboard-group-last-update-time')
@click.option('--max-dashboard-group-last-update-time')
@click.option('--limit', type=int)
@click.pass_context
def get_dashboard_groups(
        ctx: click.Context,
        dashboard_group_ids: str,
        dashboard_group_names: str,
        role_ids: str,
        role_names: str,
        min_dashboard_group_create_time: str,
        max_dashboard_group_create_time: str,
        min_dashboard_group_last_update_time: str,
        max_dashboard_group_last_update_time: str,
        limit: int):

    api = Kenna(**ctx.obj['config']['kenna']['api'])
    for row in api.iter_dashboard_groups(
        dashboard_group_ids=dashboard_group_ids,
        dashboard_group_names=dashboard_group_names,
        role_ids=role_ids,
        role_names=role_names,
        min_dashboard_group_create_time=hodgepodge.time.to_datetime(min_dashboard_group_create_time),
        max_dashboard_group_create_time=hodgepodge.time.to_datetime(max_dashboard_group_create_time),
        min_dashboard_group_last_update_time=hodgepodge.time.to_datetime(min_dashboard_group_last_update_time),
        max_dashboard_group_last_update_time=hodgepodge.time.to_datetime(max_dashboard_group_last_update_time),
        limit=limit,
    ):
        click.echo(row, **ctx.obj['config']['kenna']['cli'])


@dashboard_groups.command()
@click.option('--dashboard-group-ids')
@click.option('--dashboard-group-names')
@click.option('--role-ids')
@click.option('--role-names')
@click.option('--min-dashboard-group-create-time')
@click.option('--max-dashboard-group-create-time')
@click.option('--min-dashboard-group-last-update-time')
@click.option('--max-dashboard-group-last-update-time')
@click.pass_context
def count_dashboard_groups(
        ctx: click.Context,
        dashboard_group_ids: str,
        dashboard_group_names: str,
        role_ids: str,
        role_names: str,
        min_dashboard_group_create_time: str,
        max_dashboard_group_create_time: str,
        min_dashboard_group_last_update_time: str,
        max_dashboard_group_last_update_time: str):

    api = Kenna(**ctx.obj['config']['kenna']['api'])
    n = api.count_dashboard_groups(
        dashboard_group_ids=dashboard_group_ids,
        dashboard_group_names=dashboard_group_names,
        role_ids=role_ids,
        role_names=role_names,
        min_dashboard_group_create_time=hodgepodge.time.to_datetime(min_dashboard_group_create_time),
        max_dashboard_group_create_time=hodgepodge.time.to_datetime(max_dashboard_group_create_time),
        min_dashboard_group_last_update_time=hodgepodge.time.to_datetime(min_dashboard_group_last_update_time),
        max_dashboard_group_last_update_time=hodgepodge.time.to_datetime(max_dashboard_group_last_update_time),
    )
    click.echo(n)
