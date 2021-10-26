from kenna.api import Kenna

import kenna.cli.click as click


@click.group()
@click.pass_context
def connectors(_):
    pass


@connectors.command()
@click.option('--connector-id', type=int, required=True)
@click.pass_context
def get_connector(ctx: click.Context, connector_id: int):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    row = api.get_connector(connector_id=connector_id)
    if row:
        click.echo(row, **ctx.obj['config']['kenna']['cli'])


@connectors.command()
@click.option('--connector-ids')
@click.option('--connector-names')
@click.option('--limit', type=int)
@click.pass_context
def get_connectors(ctx: click.Context, connector_ids: str, connector_names: str, limit: int):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    for row in api.iter_connectors(connector_ids=connector_ids, connector_names=connector_names, limit=limit):
        click.echo(row, **ctx.obj['config']['kenna']['cli'])


@connectors.command()
@click.option('--connector-ids')
@click.option('--connector-names')
@click.option('--connector-run-ids')
@click.pass_context
def get_connector_runs(ctx: click.Context, connector_ids: str, connector_names: str, connector_run_ids: str):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    runs = api.get_connector_runs_by_connector_id(
        connector_ids=click.str_to_ints(connector_ids),
        connector_names=click.str_to_strs(connector_names),
        connector_run_ids=click.str_to_ints(connector_run_ids),
    )
    click.echo(runs)


@connectors.command()
@click.option('--connector-ids')
@click.option('--connector-names')
@click.pass_context
def count_connectors(ctx: click.Context, connector_ids: str, connector_names: str):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    n = api.count_connectors(connector_ids=connector_ids, connector_names=connector_names)
    click.echo(n)


@connectors.command()
@click.option('--connector-ids')
@click.option('--connector-names')
@click.option('--connector-run-ids')
@click.pass_context
def count_connector_runs(ctx: click.Context, connector_ids: str, connector_names: str, connector_run_ids: str):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    n = api.count_connector_runs(
        connector_ids=click.str_to_ints(connector_ids),
        connector_names=click.str_to_strs(connector_names),
        connector_run_ids=click.str_to_ints(connector_run_ids),
    )
    click.echo(n)
