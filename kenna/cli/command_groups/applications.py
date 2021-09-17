from kenna.api import Kenna

import click
import hodgepodge.types
import hodgepodge.click


@click.group()
@click.option('--application-ids')
@click.option('--application-names')
@click.pass_context
def applications(ctx, application_ids: str, application_names: str):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    ctx.obj.update({
        'application_ids': hodgepodge.click.str_to_list_of_int(application_ids),
        'application_names': hodgepodge.click.str_to_list_of_str(application_names),
    })


@applications.command()
@click.pass_context
def count_applications(ctx):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_applications(
        application_ids=ctx.obj['application_ids'],
        application_names=ctx.obj['application_names'],
    )
    n = sum(1 for _ in rows)
    click.echo(n)


@applications.command()
@click.option('--limit', type=int)
@click.pass_context
def get_applications(ctx, limit):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_applications(
        application_ids=ctx.obj['application_ids'],
        application_names=ctx.obj['application_names'],
        limit=limit,
    )
    for row in rows:
        row = hodgepodge.types.dict_to_json(row)
        click.echo(row)
