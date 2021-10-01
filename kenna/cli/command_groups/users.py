from kenna.api import Kenna

import click

import hodgepodge.click
import hodgepodge.types
import hodgepodge.time


@click.group()
@click.pass_context
def users(_):
    pass


@users.command()
@click.option('--user-id', type=int, required=True)
@click.pass_context
def get_user(ctx: click.Context, user_id: int):
    api = Kenna(**ctx.obj['kenna']['config'])
    row = api.get_user(user_id=user_id)
    if row:
        hodgepodge.click.echo_as_json(row)


@users.command()
@click.option('--user-ids')
@click.option('--user-names')
@click.option('--user-email-addresses')
@click.option('--min-user-create-time')
@click.option('--max-user-create-time')
@click.option('--min-user-last-sign-in-time')
@click.option('--max-user-last-sign-in-time')
@click.option('--min-user-last-update-time')
@click.option('--max-user-last-update-time')
@click.option('--limit', type=int)
@click.pass_context
def get_users(
        ctx: click.Context,
        user_ids: str,
        user_names: str,
        user_email_addresses: str,
        min_user_create_time: str,
        max_user_create_time: str,
        min_user_last_update_time: str,
        max_user_last_update_time: str,
        min_user_last_sign_in_time: str,
        max_user_last_sign_in_time: str,
        limit: int):

    api = Kenna(**ctx.obj['kenna']['config'])
    for row in api.iter_users(
        user_ids=hodgepodge.click.str_to_list_of_int(user_ids),
        user_names=hodgepodge.click.str_to_list_of_str(user_names),
        user_email_addresses=hodgepodge.click.str_to_list_of_str(user_email_addresses),
        min_user_create_time=hodgepodge.time.to_datetime(min_user_create_time),
        max_user_create_time=hodgepodge.time.to_datetime(max_user_create_time),
        min_user_last_update_time=hodgepodge.time.to_datetime(min_user_last_update_time),
        max_user_last_update_time=hodgepodge.time.to_datetime(max_user_last_update_time),
        min_user_last_sign_in_time=hodgepodge.time.to_datetime(min_user_last_sign_in_time),
        max_user_last_sign_in_time=hodgepodge.time.to_datetime(max_user_last_sign_in_time),
        limit=limit,
    ):
        hodgepodge.click.echo_as_json(row)


@users.command()
@click.option('--user-ids')
@click.option('--user-names')
@click.option('--user-email-addresses')
@click.option('--min-user-create-time')
@click.option('--max-user-create-time')
@click.option('--min-user-last-sign-in-time')
@click.option('--max-user-last-sign-in-time')
@click.option('--min-user-last-update-time')
@click.option('--max-user-last-update-time')
@click.option('--limit', type=int)
@click.pass_context
def count_users(
        ctx: click.Context,
        user_ids: str,
        user_names: str,
        user_email_addresses: str,
        min_user_create_time: str,
        max_user_create_time: str,
        min_user_last_update_time: str,
        max_user_last_update_time: str,
        min_user_last_sign_in_time: str,
        max_user_last_sign_in_time: str,
        limit: int):

    api = Kenna(**ctx.obj['kenna']['config'])
    rows = api.iter_users(
        user_ids=hodgepodge.click.str_to_list_of_int(user_ids),
        user_names=hodgepodge.click.str_to_list_of_str(user_names),
        user_email_addresses=hodgepodge.click.str_to_list_of_str(user_email_addresses),
        min_user_create_time=hodgepodge.time.to_datetime(min_user_create_time),
        max_user_create_time=hodgepodge.time.to_datetime(max_user_create_time),
        min_user_last_update_time=hodgepodge.time.to_datetime(min_user_last_update_time),
        max_user_last_update_time=hodgepodge.time.to_datetime(max_user_last_update_time),
        min_user_last_sign_in_time=hodgepodge.time.to_datetime(min_user_last_sign_in_time),
        max_user_last_sign_in_time=hodgepodge.time.to_datetime(max_user_last_sign_in_time),
        limit=limit,
    )
    count = sum(1 for _ in rows)
    click.echo(count)
