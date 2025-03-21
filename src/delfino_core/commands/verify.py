import click
from delfino.models import AppContext

from delfino_core.commands.pre_commit import run_ensure_pre_commit
from delfino_core.commands.ruff import run_ruff
from delfino_core.commands.test import run_group_test
from delfino_core.commands.typecheck import run_mypy
from delfino_core.config import CorePluginConfig, pass_plugin_app_context
from delfino_core.utils import commands_group_help, execute_commands_group

_COMMANDS = [run_ensure_pre_commit, run_ruff, run_mypy, run_group_test]


@click.command("verify", help=commands_group_help("verify"))
@pass_plugin_app_context
@click.pass_context
def run_group_verify(click_context: click.Context, app_context: AppContext[CorePluginConfig]):
    execute_commands_group(click_context, app_context.plugin_config)
