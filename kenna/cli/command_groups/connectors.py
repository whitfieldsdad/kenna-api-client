from kenna.api import Kenna

import click

import hodgepodge.time
import hodgepodge.click
import hodgepodge.types


@click.group()
@click.pass_context
def connectors(_):
    pass


@connectors.command()
@click.option('--connector-id', type=int, required=True)
@click.pass_context
def get_connector(ctx: click.Context, connector_id: int):
    api = Kenna(**ctx.obj['kenna']['config'])
    row = api.get_connector(connector_id=connector_id)
    hodgepodge.click.echo_as_json(row)


@connectors.command()
@click.option('--connector-id', type=int, required=True)
@click.option('--connector-run-id', type=int, required=True)
@click.pass_context
def get_connector_run(ctx: click.Context, connector_id: int, connector_run_id: int):
    api = Kenna(**ctx.obj['kenna']['config'])
    row = api.get_connector_run(
        connector_id=connector_id,
        connector_run_id=connector_run_id,
    )
    if row:
        hodgepodge.click.echo_as_json(row)


@connectors.command()
@click.option('--connector-ids')
@click.option('--connector-names')
@click.option('--min-connector-run-start-time')
@click.option('--max-connector-run-start-time')
@click.option('--min-connector-run-end-time')
@click.option('--max-connector-run-end-time')
@click.option('--limit', type=int)
@click.pass_context
def get_connectors(
        ctx: click.Context,
        connector_ids: str,
        connector_names: str,
        min_connector_run_start_time: str,
        max_connector_run_start_time: str,
        min_connector_run_end_time: str,
        max_connector_run_end_time: str,
        limit: int):

    api = Kenna(**ctx.obj['kenna']['config'])
    for row in api.iter_connectors(
        connector_ids=connector_ids,
        connector_names=connector_names,
        min_connector_run_start_time=hodgepodge.time.to_datetime(min_connector_run_start_time),
        max_connector_run_start_time=hodgepodge.time.to_datetime(max_connector_run_start_time),
        min_connector_run_end_time=hodgepodge.time.to_datetime(min_connector_run_end_time),
        max_connector_run_end_time=hodgepodge.time.to_datetime(max_connector_run_end_time),
        limit=limit,
    ):
        hodgepodge.click.echo_as_json(row)


@connectors.command()
@click.option('--connector-ids')
@click.option('--connector-names')
@click.option('--connector-run-ids')
@click.option('--min-connector-run-start-time')
@click.option('--max-connector-run-start-time')
@click.option('--min-connector-run-end-time')
@click.option('--max-connector-run-end-time')
@click.option('--limit', type=int)
@click.pass_context
def get_connector_runs(
        ctx: click.Context,
        connector_ids: str,
        connector_names: str,
        connector_run_ids: str,
        min_connector_run_start_time: str,
        max_connector_run_start_time: str,
        min_connector_run_end_time: str,
        max_connector_run_end_time: str,
        limit: int):

    api = Kenna(**ctx.obj['kenna']['config'])
    runs = api.get_connector_runs_by_connector_id(
        connector_ids=hodgepodge.click.str_to_list_of_int(connector_ids),
        connector_names=hodgepodge.click.str_to_list_of_str(connector_names),
        connector_run_ids=hodgepodge.click.str_to_list_of_int(connector_run_ids),
        min_connector_run_start_time=hodgepodge.time.to_datetime(min_connector_run_start_time),
        max_connector_run_start_time=hodgepodge.time.to_datetime(max_connector_run_start_time),
        min_connector_run_end_time=hodgepodge.time.to_datetime(min_connector_run_end_time),
        max_connector_run_end_time=hodgepodge.time.to_datetime(max_connector_run_end_time),
        limit=limit,
    )
    hodgepodge.click.echo_as_json(runs)


@connectors.command()
@click.option('--connector-ids')
@click.option('--connector-names')
@click.option('--min-connector-run-start-time')
@click.option('--max-connector-run-start-time')
@click.option('--min-connector-run-end-time')
@click.option('--max-connector-run-end-time')
@click.option('--limit', type=int)
@click.pass_context
def count_connectors(
        ctx: click.Context,
        connector_ids: str,
        connector_names: str,
        min_connector_run_start_time: str,
        max_connector_run_start_time: str,
        min_connector_run_end_time: str,
        max_connector_run_end_time: str,
        limit: int):

    api = Kenna(**ctx.obj['kenna']['config'])
    rows = api.iter_connectors(
        connector_ids=connector_ids,
        connector_names=connector_names,
        min_connector_run_start_time=hodgepodge.time.to_datetime(min_connector_run_start_time),
        max_connector_run_start_time=hodgepodge.time.to_datetime(max_connector_run_start_time),
        min_connector_run_end_time=hodgepodge.time.to_datetime(min_connector_run_end_time),
        max_connector_run_end_time=hodgepodge.time.to_datetime(max_connector_run_end_time),
        limit=limit,
    )
    count = sum(1 for _ in rows)
    hodgepodge.click.echo_as_json(count)


@connectors.command()
@click.option('--connector-ids')
@click.option('--connector-names')
@click.option('--connector-run-ids')
@click.option('--min-connector-run-start-time')
@click.option('--max-connector-run-start-time')
@click.option('--min-connector-run-end-time')
@click.option('--max-connector-run-end-time')
@click.option('--limit', type=int)
@click.pass_context
def count_connector_runs(
        ctx: click.Context,
        connector_ids: str,
        connector_names: str,
        connector_run_ids: str,
        min_connector_run_start_time: str,
        max_connector_run_start_time: str,
        min_connector_run_end_time: str,
        max_connector_run_end_time: str,
        limit: int):

    api = Kenna(**ctx.obj['kenna']['config'])
    runs = api.get_connector_runs_by_connector_id(
        connector_ids=hodgepodge.click.str_to_list_of_int(connector_ids),
        connector_names=hodgepodge.click.str_to_list_of_str(connector_names),
        connector_run_ids=hodgepodge.click.str_to_list_of_int(connector_run_ids),
        min_connector_run_start_time=hodgepodge.time.to_datetime(min_connector_run_start_time),
        max_connector_run_start_time=hodgepodge.time.to_datetime(max_connector_run_start_time),
        min_connector_run_end_time=hodgepodge.time.to_datetime(min_connector_run_end_time),
        max_connector_run_end_time=hodgepodge.time.to_datetime(max_connector_run_end_time),
        limit=limit,
    )
    count = sum(1 for _ in runs)
    click.echo(count)
