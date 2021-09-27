import click

import hodgepodge.click
import hodgepodge.types


@click.group()
@click.option('--user-ids')
@click.option('--user-names')
@click.option('--user-email-addresses')
@click.option('--min-user-create-time')
@click.option('--max-user-create-time')
@click.option('--min-user-last-sign-in-time')
@click.option('--max-user-last-sign-in-time')
@click.option('--min-user-last-update-time')
@click.option('--max-user-last-update-time')
@click.pass_context
def users(
        ctx: click.Context,
        user_ids: str,
        user_names: str,
        user_email_addresses: str,
        min_user_create_time: str,
        max_user_create_time: str,
        min_user_last_update_time: str,
        max_user_last_update_time: str,
        min_user_last_sign_in_time: str,
        max_user_last_sign_in_time: str):

    ctx.obj['kwargs'] = {
        'user_ids': hodgepodge.click.str_to_list_of_int(user_ids),
        'user_names': hodgepodge.click.str_to_list_of_str(user_names),
        'user_email_addresses': hodgepodge.click.str_to_list_of_str(user_email_addresses),
        'min_user_create_time': min_user_create_time,
        'max_user_create_time': max_user_create_time,
        'min_user_last_update_time': min_user_last_update_time,
        'max_user_last_update_time': max_user_last_update_time,
        'min_user_last_sign_in_time': min_user_last_sign_in_time,
        'max_user_last_sign_in_time': max_user_last_sign_in_time,
    }


@users.command()
@click.option('--limit', type=int)
@click.pass_context
def get_users(ctx: click.Context, limit: int):
    rows = ctx.obj['kenna_api'].iter_users(**ctx.obj['kwargs'], limit=limit)
    hodgepodge.click.echo_as_jsonl(rows)
