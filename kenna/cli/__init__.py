from kenna.authentication import DEFAULT_API_KEY
from kenna.cli.command_groups.applications import applications
from kenna.cli.command_groups.assets import assets
from kenna.cli.command_groups.asset_groups import asset_groups
from kenna.cli.command_groups.connectors import connectors
from kenna.cli.command_groups.dashboard_groups import dashboard_groups
from kenna.cli.command_groups.data_exports import data_exports
from kenna.cli.command_groups.fixes import fixes
from kenna.cli.command_groups.users import users
from kenna.cli.command_groups.roles import roles
from kenna.cli.command_groups.teams import teams
from kenna.cli.command_groups.vulnerabilities import vulnerabilities
from kenna.cli.constants import HIDE_RISK_METER_SCORES_BY_DEFAULT, HIDE_COUNTS_BY_DEFAULT, HIDE_EMPTY_VALUES_BY_DEFAULT
from kenna.region import DEFAULT_REGION

import click


@click.group()
@click.option('--api-key', default=DEFAULT_API_KEY)
@click.option('--region', default=DEFAULT_REGION)
@click.option('--hide-risk-meter-scores', default=HIDE_RISK_METER_SCORES_BY_DEFAULT)
@click.option('--hide-counts', default=HIDE_COUNTS_BY_DEFAULT)
@click.option('--hide-empty-values', default=HIDE_EMPTY_VALUES_BY_DEFAULT)
@click.pass_context
def cli(ctx: click.Context, api_key: str, region: str, hide_counts: bool, hide_risk_meter_scores: bool, hide_empty_values: bool):
    ctx.ensure_object(dict)
    ctx.obj.update({
        'config': {
            'kenna': {
                'api': {
                    'api_key': api_key,
                    'region': region,
                },
                'cli': {
                    'hide_empty_values': hide_empty_values,
                    'hide_counts': hide_counts,
                    'hide_risk_meter_scores': hide_risk_meter_scores,
                }
            }
        }
    })


COMMAND_GROUPS = [
    applications,
    assets,
    asset_groups,
    connectors,
    data_exports,
    dashboard_groups,
    fixes,
    users,
    roles,
    vulnerabilities,
    teams,
]
for command_group in COMMAND_GROUPS:
    cli.add_command(command_group)
