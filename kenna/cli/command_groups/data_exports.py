from kenna.api import Kenna

import kenna.cli.click as click
import logging


logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def data_exports(_):
    pass


@data_exports.command()
@click.option('--search-id', type=int)
@click.pass_context
def get_status(ctx: click.Context, search_id: int):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    reply = api.get_data_export_status(search_id)
    if reply:
        click.echo(reply)


@data_exports.command()
@click.option('--search-ids')
@click.pass_context
def wait(ctx: click.Context, search_ids: str):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    api.wait_for_data_exports(search_ids=click.str_to_ints(search_ids))
