from collections import ChainMap
from logging import getLogger
from typing import Dict, cast

import click
from delfino.click_utils.command import get_root_command
from delfino.decorators.files_folders import FILES_FOLDERS_OPTION_CALLBACK
from delfino.decorators.pass_args import PASS_ARGS_CALLBACK

from delfino_core.config import CorePluginConfig

_LOG = getLogger(__name__)


def ensure_reports_dir(config: CorePluginConfig) -> None:
    """Ensures that the reports directory exists."""
    config.reports_directory.mkdir(parents=True, exist_ok=True)


def execute_commands_group(name: str, click_context: click.Context, plugin_config: CorePluginConfig, **kwargs):
    root = get_root_command(click_context)
    option_name = f"{name}_commands"

    commands: Dict[str, click.Command] = {
        command: cast(click.Command, root.get_command(click_context, command))
        for command in root.list_commands(click_context)
    }

    for target_name in getattr(plugin_config, option_name):
        if target_name not in commands:
            _LOG.warning(
                f"Command '{target_name}' used as part of the '{option_name}' option does not exist. Skipping."
            )
            continue

        if target_name in plugin_config.disable_commands:
            _LOG.debug(f"Skipping disabled command '{target_name}'.")
            continue

        command = commands[target_name]

        parameter_from_config = ChainMap(
            *(
                callback.parameter_from_config_in_group(click_context, command)
                for callback in [PASS_ARGS_CALLBACK, FILES_FOLDERS_OPTION_CALLBACK]
            )
        )

        click_context.forward(command, **kwargs, **parameter_from_config)
