import click

import hodgepodge.click
import hodgepodge.types


@click.group()
@click.option('--dashboard-group-ids')
@click.option('--dashboard-group-names')
@click.option('--role-ids')
@click.option('--role-names')
@click.option('--min-dashboard-group-create-time')
@click.option('--max-dashboard-group-create-time')
@click.option('--min-dashboard-group-last-update-time')
@click.option('--max-dashboard-group-last-update-time')
@click.pass_context
def dashboard_groups(
        ctx: click.Context,
        dashboard_group_ids: str,
        dashboard_group_names: str,
        role_ids: str,
        role_names: str,
        min_dashboard_group_create_time: str,
        max_dashboard_group_create_time: str,
        min_dashboard_group_last_update_time: str,
        max_dashboard_group_last_update_time: str):

    ctx.obj['kwargs'] = {
        'dashboard_group_ids': hodgepodge.click.str_to_list_of_int(dashboard_group_ids),
        'dashboard_group_names': hodgepodge.click.str_to_list_of_int(dashboard_group_names),
        'role_ids': hodgepodge.click.str_to_list_of_int(role_ids),
        'role_names': hodgepodge.click.str_to_list_of_str(role_names),
        'min_dashboard_group_create_time': min_dashboard_group_create_time,
        'max_dashboard_group_create_time': max_dashboard_group_create_time,
        'min_dashboard_group_last_update_time': min_dashboard_group_last_update_time,
        'max_dashboard_group_last_update_time': max_dashboard_group_last_update_time,
    }


@dashboard_groups.command()
@click.option('--limit', type=int)
@click.pass_context
def get_dashboard_groups(ctx: click.Context, limit: int):
    rows = ctx.obj['kenna_api'].iter_dashboard_groups(**ctx.obj['kwargs'], limit=limit)
    hodgepodge.click.echo_as_jsonl(rows)
