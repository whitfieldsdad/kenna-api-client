from kenna.api import Kenna

import kenna.cli.click as click
import hodgepodge.pattern_matching
import hodgepodge.files
import hodgepodge.types
import hodgepodge.time
import logging

logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def users(_):
    pass


@users.command()
@click.option('--user-id', type=int)
@click.option('--user-email-address')
@click.pass_context
def get_user(ctx: click.Context, user_id: int, user_email_address: str):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    row = api.get_user(
        user_id=user_id,
        user_email_address=user_email_address,
    )
    if row:
        click.echo(row, **ctx.obj['config']['kenna']['cli'])


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
@click.option('--hide-active-users/--show-active-users', default=False)
@click.option('--hide-inactive-users/--show-inactive-users', default=False)
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
        hide_active_users: bool,
        hide_inactive_users: bool,
        limit: int):

    api = Kenna(**ctx.obj['config']['kenna']['api'])
    for row in api.iter_users(
        user_ids=click.str_to_ints(user_ids),
        user_names=click.str_to_strs(user_names),
        user_email_addresses=click.str_to_strs(user_email_addresses),
        min_user_create_time=hodgepodge.time.to_datetime(min_user_create_time),
        max_user_create_time=hodgepodge.time.to_datetime(max_user_create_time),
        min_user_last_update_time=hodgepodge.time.to_datetime(min_user_last_update_time),
        max_user_last_update_time=hodgepodge.time.to_datetime(max_user_last_update_time),
        min_user_last_sign_in_time=hodgepodge.time.to_datetime(min_user_last_sign_in_time),
        max_user_last_sign_in_time=hodgepodge.time.to_datetime(max_user_last_sign_in_time),
        hide_active_users=hide_active_users,
        hide_inactive_users=hide_inactive_users,
        limit=limit,
    ):
        click.echo(row, **ctx.obj['config']['kenna']['cli'])


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
@click.option('--hide-active-users/--show-active-users', default=False)
@click.option('--hide-inactive-users/--show-inactive-users', default=False)
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
        hide_active_users: bool,
        hide_inactive_users: bool):

    api = Kenna(**ctx.obj['config']['kenna']['api'])
    n = api.count_users(
        user_ids=click.str_to_ints(user_ids),
        user_names=click.str_to_strs(user_names),
        user_email_addresses=click.str_to_strs(user_email_addresses),
        min_user_create_time=hodgepodge.time.to_datetime(min_user_create_time),
        max_user_create_time=hodgepodge.time.to_datetime(max_user_create_time),
        min_user_last_update_time=hodgepodge.time.to_datetime(min_user_last_update_time),
        max_user_last_update_time=hodgepodge.time.to_datetime(max_user_last_update_time),
        min_user_last_sign_in_time=hodgepodge.time.to_datetime(min_user_last_sign_in_time),
        max_user_last_sign_in_time=hodgepodge.time.to_datetime(max_user_last_sign_in_time),
        hide_active_users=hide_active_users,
        hide_inactive_users=hide_inactive_users,
    )
    click.echo(n)
