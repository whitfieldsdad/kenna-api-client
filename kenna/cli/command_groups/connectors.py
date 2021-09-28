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
