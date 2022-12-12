import click
from delfino.models import AppContext

from delfino_core.commands.format import run_format
from delfino_core.commands.lint import lint
from delfino_core.commands.test import test_all
from delfino_core.commands.typecheck import typecheck
from delfino_core.config import CorePluginConfig, pass_plugin_app_context
from delfino_core.utils import execute_commands_group

_COMMANDS = [run_format, lint, typecheck, test_all]


@click.command(help="Runs all verification commands. Configured by the ``verify_commands`` setting.")
@pass_plugin_app_context
@click.pass_context
def verify_all(click_context: click.Context, app_context: AppContext[CorePluginConfig]):
    execute_commands_group("verify", click_context, app_context.plugin_config)
