from kenna.api import Kenna

import click
import hodgepodge.types
import hodgepodge.click


@click.group()
@click.option('--connector-ids')
@click.option('--connector-names')
@click.option('--connector-run-ids')
@click.pass_context
def connector_runs(ctx, connector_ids: str, connector_names: str, connector_run_ids: str):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    ctx.obj.update({
        'connector_ids': hodgepodge.click.str_to_list_of_int(connector_ids),
        'connector_names': hodgepodge.click.str_to_list_of_str(connector_names),
        'connector_run_ids': hodgepodge.click.str_to_list_of_str(connector_run_ids),
    })


@connector_runs.command()
@click.pass_context
def count_connector_runs(ctx):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_connector_runs(
        connector_ids=ctx.obj['connector_ids'],
        connector_names=ctx.obj['connector_names'],
        connector_run_ids=ctx.obj['connector_run_ids'],
    )
    n = sum(1 for _ in rows)
    click.echo(n)


@connector_runs.command()
@click.option('--limit', type=int)
@click.pass_context
def get_connector_runs(ctx, limit):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_connector_runs(
        connector_ids=ctx.obj['connector_ids'],
        connector_names=ctx.obj['connector_names'],
        connector_run_ids=ctx.obj['connector_run_ids'],
        limit=limit,
    )
    for row in rows:
        row = hodgepodge.types.dict_to_json(row)
        click.echo(row)
