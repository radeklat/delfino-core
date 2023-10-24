from collections import ChainMap
from logging import getLogger
from subprocess import PIPE, run
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


def commands_group_help(name: str) -> str:
    command_names = ", ".join(CorePluginConfig.model_fields[f"{name}_commands"].default)
    return f"Runs {command_names}.\n\n" f"Configured by the ``{name}_commands`` settings option."


def execute_commands_group(click_context: click.Context, plugin_config: CorePluginConfig, **kwargs):
    """Executes a group of commands.

    Group default commands are defined in `delfino_core.config.CorePluginConfig.<NAME>_commands`.
    They can be overridden by `<NAME>_commands` option in the `pyproject.toml` config.
    """
    root = get_root_command(click_context)
    if (name := click_context.command.name) is None:
        raise ValueError("group commands must have a name set")

    option_name = f"{name.replace('-', '_')}_commands"

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


def executable_installed(name: str, *flags: str) -> bool:
    """Returns True if the executable is installed."""
    if not flags:
        flags = ("--version",)

    try:
        run([name, *flags], stdout=PIPE, check=True)
    except FileNotFoundError:
        return False
    return True


def assert_executable_installed(name: str, *flags: str, required_by: str = "this command") -> None:
    assert executable_installed(
        name, *flags
    ), f"Optional executable '{name}' is required by {required_by} but not installed."


def ask(question: str) -> bool:
    return not bool(input(f"\033[1;33m{question} [Y/n]: \033[0m").lower() == "n")
