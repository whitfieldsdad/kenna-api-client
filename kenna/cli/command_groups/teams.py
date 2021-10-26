from kenna.api import Kenna

import kenna.cli.click as click


@click.group()
@click.pass_context
def teams(_):
    pass


@teams.command()
@click.option('--application-ids')
@click.option('--application-names')
@click.pass_context
def get_teams(ctx: click.Context, application_ids: str, application_names: str):
    api = Kenna(**ctx.obj['config']['kenna']['api'])
    for team in api.get_teams(
        application_ids=click.str_to_ints(application_ids),
        application_names=click.str_to_strs(application_names)
    ):
        click.echo(team)

