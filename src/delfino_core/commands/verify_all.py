from typing import Dict, cast

import click
from delfino.click_utils.command import get_root_command
from delfino.contexts import AppContext

from delfino_core.commands.format import run_format
from delfino_core.commands.lint import lint
from delfino_core.commands.test import test_all
from delfino_core.commands.typecheck import typecheck
from delfino_core.config import pass_plugin_app_context

_COMMANDS = [run_format, lint, typecheck, test_all]


@click.command(help="Runs all verification commands. Configured by the ``verify_commands`` setting.")
@click.pass_context
@pass_plugin_app_context
def verify_all(app_context: AppContext, click_context: click.Context):
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
