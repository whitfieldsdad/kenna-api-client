from kenna.api import Kenna

import click

import hodgepodge.click
import hodgepodge.types
import hodgepodge.time


@click.group()
@click.pass_context
def roles(_):
    pass


@roles.command()
@click.option('--role-id', type=int, required=True)
@click.pass_context
def get_role(ctx: click.Context, role_id: int):
    api = Kenna(**ctx.obj['kenna']['config'])
    row = api.get_role(role_id=role_id)
    if row:
        hodgepodge.click.echo_as_json(row)


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
        limit: int):

    api = Kenna(**ctx.obj['kenna']['config'])
    for row in api.iter_roles(
        role_ids=hodgepodge.click.str_to_list_of_int(role_ids),
        role_names=hodgepodge.click.str_to_list_of_str(role_names),
        role_types=hodgepodge.click.str_to_list_of_str(role_types),
        role_access_levels=hodgepodge.click.str_to_list_of_str(role_access_levels),
        role_custom_permissions=hodgepodge.click.str_to_list_of_str(role_custom_permissions),
        user_ids=hodgepodge.click.str_to_list_of_int(user_ids),
        user_email_addresses=hodgepodge.click.str_to_list_of_str(user_email_addresses),
        user_names=hodgepodge.click.str_to_list_of_str(user_names),
        min_role_create_time=hodgepodge.time.to_datetime(min_role_create_time),
        max_role_create_time=hodgepodge.time.to_datetime(max_role_create_time),
        min_role_last_update_time=hodgepodge.time.to_datetime(min_role_last_update_time),
        max_role_last_update_time=hodgepodge.time.to_datetime(max_role_last_update_time),
        limit=limit,
    ):
        hodgepodge.click.echo_as_json(row)


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
@click.option('--limit', type=int)
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
        limit: int):

    api = Kenna(**ctx.obj['kenna']['config'])
    rows = api.iter_roles(
        role_ids=hodgepodge.click.str_to_list_of_int(role_ids),
        role_names=hodgepodge.click.str_to_list_of_str(role_names),
        role_types=hodgepodge.click.str_to_list_of_str(role_types),
        role_access_levels=hodgepodge.click.str_to_list_of_str(role_access_levels),
        role_custom_permissions=hodgepodge.click.str_to_list_of_str(role_custom_permissions),
        user_ids=hodgepodge.click.str_to_list_of_int(user_ids),
        user_email_addresses=hodgepodge.click.str_to_list_of_str(user_email_addresses),
        user_names=hodgepodge.click.str_to_list_of_str(user_names),
        min_role_create_time=hodgepodge.time.to_datetime(min_role_create_time),
        max_role_create_time=hodgepodge.time.to_datetime(max_role_create_time),
        min_role_last_update_time=hodgepodge.time.to_datetime(min_role_last_update_time),
        max_role_last_update_time=hodgepodge.time.to_datetime(max_role_last_update_time),
        limit=limit,
    )
    count = sum(1 for _ in rows)
    click.echo(count)
