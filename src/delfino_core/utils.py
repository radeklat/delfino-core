from typing import Dict, cast

import click
from delfino.click_utils.command import get_root_command

from delfino_core.config import CorePluginConfig


def ensure_reports_dir(config: CorePluginConfig) -> None:
    """Ensures that the reports directory exists."""
    config.reports_directory.mkdir(parents=True, exist_ok=True)


def execute_commands_group(name: str, click_context: click.Context, plugin_config: CorePluginConfig, **kwargs):
    root = get_root_command(click_context)
    commands: Dict[str, click.Command] = {
        command: cast(click.Command, root.get_command(click_context, command))
        for command in root.list_commands(click_context)
    }

    target_commands = [
        commands[target_name]
        for target_name in getattr(plugin_config, f"{name}_commands")
        if target_name in commands and target_name not in plugin_config.disable_commands
    ]

    for command in target_commands:
        click_context.forward(command, **kwargs)
