from kenna.api import Kenna

import click
import hodgepodge.types
import hodgepodge.click


@click.group()
@click.pass_context
def applications(_):
    pass


@applications.command()
@click.option('--application-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def count_applications(ctx, application_ids: str, limit: int):
    """
    Count matching applications.
    """
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    apps = api.iter_applications(application_ids=hodgepodge.click.str_to_list_of_int(application_ids), limit=limit)
    count = sum(1 for _ in apps)
    click.echo(count)


@applications.command()
@click.option('--application-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_applications(ctx, application_ids: str, limit: int):
    """
    Lookup one or more applications.
    """
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    for app in api.iter_applications(application_ids=hodgepodge.click.str_to_list_of_int(application_ids), limit=limit):
        app = hodgepodge.types.dict_to_json(app)
        click.echo(app)


@applications.command()
@click.option('--application-id', required=True, type=int)
@click.pass_context
def get_application(ctx, application_id: int):
    """
    Lookup a single application.
    """
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    app = api.get_application(application_id=application_id)
    if app:
        app = hodgepodge.types.dict_to_json(app)
        click.echo(app)
