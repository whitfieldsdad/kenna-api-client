from kenna.api import Kenna

import click

import hodgepodge.click
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
    api = Kenna(**ctx.obj['kenna']['config'])
    row = api.get_dashboard_group(dashboard_group_id=dashboard_group_id)
    if row:
        hodgepodge.click.echo_as_json(row)


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

    api = Kenna(**ctx.obj['kenna']['config'])
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
        hodgepodge.click.echo_as_json(row)


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
def count_dashboard_groups(
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

    api = Kenna(**ctx.obj['kenna']['config'])
    groups = api.iter_dashboard_groups(
        dashboard_group_ids=dashboard_group_ids,
        dashboard_group_names=dashboard_group_names,
        role_ids=role_ids,
        role_names=role_names,
        min_dashboard_group_create_time=hodgepodge.time.to_datetime(min_dashboard_group_create_time),
        max_dashboard_group_create_time=hodgepodge.time.to_datetime(max_dashboard_group_create_time),
        min_dashboard_group_last_update_time=hodgepodge.time.to_datetime(min_dashboard_group_last_update_time),
        max_dashboard_group_last_update_time=hodgepodge.time.to_datetime(max_dashboard_group_last_update_time),
        limit=limit,
    )
    count = sum(1 for _ in groups)
    click.echo(count)
