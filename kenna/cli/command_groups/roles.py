from kenna.api import Kenna

import kenna.cli.click as click
import hodgepodge.types
import hodgepodge.time


@click.group()
@click.pass_context
def roles(_):
    pass


@roles.command()
@click.option('--role-name', required=True)
@click.option('--access-level', required=True, help="One of [read|write]")
@click.pass_context
def create_role(ctx: click.Context, role_name: str, access_level: str):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    role_id = api.create_role(
        role_name=role_name,
        access_level=access_level,
    )
    click.echo(role_id)


@roles.command()
@click.option('--role-id', type=int, required=True)
@click.pass_context
def get_role(ctx: click.Context, role_id: int):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    row = api.get_role(role_id=role_id)
    if row:
        click.echo(row, **ctx.obj['config']['kenna']['cli'])


@roles.command()
@click.option('--role-ids')
@click.option('--role-names')
@click.option('--role-types')
@click.option('--role-access-levels')
@click.option('--role-custom-permissions')
@click.option('--user-ids')
@click.option('--user-email-addresses')
@click.option('--user-names')
@click.option('--min-role-create-time')
@click.option('--max-role-create-time')
@click.option('--min-role-last-update-time')
@click.option('--max-role-last-update-time')
@click.option('--hide-active-roles/--show-active-roles', default=False)
@click.option('--hide-inactive-roles/--show-inactive-roles', default=False)
@click.option('--limit', type=int)
@click.pass_context
def get_roles(
        ctx: click.Context,
        role_ids: str,
        role_names: str,
        role_types: str,
        role_access_levels: str,
        role_custom_permissions: str,
        user_ids: str,
        user_email_addresses: str,
        user_names: str,
        min_role_create_time: str,
        max_role_create_time: str,
        min_role_last_update_time: str,
        max_role_last_update_time: str,
        hide_active_roles: bool,
        hide_inactive_roles: bool,
        limit: int):

    api = Kenna(**ctx.obj['config']['kenna']['api'])
    rows = api.iter_roles(
        role_ids=click.str_to_ints(role_ids),
        role_names=click.str_to_strs(role_names),
        role_types=click.str_to_strs(role_types),
        role_access_levels=click.str_to_strs(role_access_levels),
        role_custom_permissions=click.str_to_strs(role_custom_permissions),
        user_ids=click.str_to_ints(user_ids),
        user_email_addresses=click.str_to_strs(user_email_addresses),
        user_names=click.str_to_strs(user_names),
        min_role_create_time=hodgepodge.time.to_datetime(min_role_create_time),
        max_role_create_time=hodgepodge.time.to_datetime(max_role_create_time),
        min_role_last_update_time=hodgepodge.time.to_datetime(min_role_last_update_time),
        max_role_last_update_time=hodgepodge.time.to_datetime(max_role_last_update_time),
        hide_active_roles=hide_active_roles,
        hide_inactive_roles=hide_inactive_roles,
        limit=limit,
    )
    for row in rows:
        click.echo(row, **ctx.obj['config']['kenna']['cli'])


@roles.command()
@click.option('--role-ids')
@click.option('--role-names')
@click.option('--role-types')
@click.option('--role-access-levels')
@click.option('--role-custom-permissions')
@click.option('--user-ids')
@click.option('--user-email-addresses')
@click.option('--user-names')
@click.option('--min-role-create-time')
@click.option('--max-role-create-time')
@click.option('--min-role-last-update-time')
@click.option('--max-role-last-update-time')
@click.option('--hide-active-roles/--show-active-roles', default=False)
@click.option('--hide-inactive-roles/--show-inactive-roles', default=False)
@click.pass_context
def count_roles(
        ctx: click.Context,
        role_ids: str,
        role_names: str,
        role_types: str,
        role_access_levels: str,
        role_custom_permissions: str,
        user_ids: str,
        user_email_addresses: str,
        user_names: str,
        min_role_create_time: str,
        max_role_create_time: str,
        min_role_last_update_time: str,
        max_role_last_update_time: str,
        hide_active_roles: bool,
        hide_inactive_roles: bool):

    api = Kenna(**ctx.obj['config']['kenna']['api'])
    n = api.count_roles(
        role_ids=click.str_to_ints(role_ids),
        role_names=click.str_to_strs(role_names),
        role_types=click.str_to_strs(role_types),
        role_access_levels=click.str_to_strs(role_access_levels),
        role_custom_permissions=click.str_to_strs(role_custom_permissions),
        user_ids=click.str_to_ints(user_ids),
        user_email_addresses=click.str_to_strs(user_email_addresses),
        user_names=click.str_to_strs(user_names),
        min_role_create_time=hodgepodge.time.to_datetime(min_role_create_time),
        max_role_create_time=hodgepodge.time.to_datetime(max_role_create_time),
        min_role_last_update_time=hodgepodge.time.to_datetime(min_role_last_update_time),
        max_role_last_update_time=hodgepodge.time.to_datetime(max_role_last_update_time),
        hide_active_roles=hide_active_roles,
        hide_inactive_roles=hide_inactive_roles,
    )
    click.echo(n)


@roles.command()
@click.option('--role-ids')
@click.pass_context
def delete_roles(ctx: click.Context, role_ids: str):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    api.delete_roles(role_ids=click.str_to_ints(role_ids))
