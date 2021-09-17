from kenna.api import Kenna

import click
import hodgepodge.types
import hodgepodge.click
import json


@click.group()
@click.option('--dashboard-group-ids')
@click.option('--dashboard-group-names')
@click.pass_context
def dashboard_groups(ctx, dashboard_group_ids: str, dashboard_group_names: str):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    ctx.obj.update({
        'dashboard_group_ids': hodgepodge.click.str_to_list_of_int(dashboard_group_ids),
        'dashboard_group_names': hodgepodge.click.str_to_list_of_str(dashboard_group_names),
    })


@dashboard_groups.command()
@click.pass_context
def count_dashboard_groups(ctx):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_dashboard_groups(
        dashboard_group_ids=ctx.obj['dashboard_group_ids'],
        dashboard_group_names=ctx.obj['dashboard_group_names'],
    )
    n = sum(1 for _ in rows)
    click.echo(n)


@dashboard_groups.command()
@click.option('--limit', type=int)
@click.pass_context
def get_dashboard_groups(ctx, limit):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_dashboard_groups(
        dashboard_group_ids=ctx.obj['dashboard_group_ids'],
        dashboard_group_names=ctx.obj['dashboard_group_names'],
        limit=limit,
    )
    for row in rows:
        row = hodgepodge.types.dict_to_json(row)
        click.echo(row)
