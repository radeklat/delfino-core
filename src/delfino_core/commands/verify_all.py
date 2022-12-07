from typing import Dict, cast

import click
from delfino.click_utils.command import get_root_command
from delfino.models import AppContext

from delfino_core.commands.format import run_format
from delfino_core.commands.lint import lint
from delfino_core.commands.test import test_all
from delfino_core.commands.typecheck import typecheck
from delfino_core.config import CorePluginConfig, pass_plugin_app_context

_COMMANDS = [run_format, lint, typecheck, test_all]


@click.command(help="Runs all verification commands. Configured by the ``verify_commands`` setting.")
@pass_plugin_app_context
@click.pass_context
def verify_all(click_context: click.Context, app_context: AppContext[CorePluginConfig]):
    plugin_config = app_context.plugin_config

    root = get_root_command(click_context)
    commands: Dict[str, click.Command] = {
        command: cast(click.Command, root.get_command(click_context, command))
        for command in root.list_commands(click_context)
    }

    target_commands = [
        commands[target_name]
        for target_name in plugin_config.verify_commands
        if target_name in commands and target_name not in plugin_config.disable_commands
    ]

    for command in target_commands:
        click_context.forward(command)
