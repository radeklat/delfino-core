"""Linting checks on source code."""

from pathlib import Path
from subprocess import PIPE
from typing import List, Optional, Tuple

import click
from delfino.decorators import files_folders_option, pass_args
from delfino.execution import OnError, run
from delfino.models import AppContext
from delfino.validation import assert_pip_package_installed
from delfino_core.config import CorePluginConfig, pass_plugin_app_context
from delfino_core.spinner import Spinner
from delfino_core.utils import commands_group_help, execute_commands_group


@click.command("ruff")
@pass_args
@files_folders_option
@pass_plugin_app_context
def run_ruff(app_context: AppContext[CorePluginConfig], passed_args: Tuple[str, ...], files_folders: Tuple[str]):
    """Run ruff."""
    assert_pip_package_installed("ruff")

    dirs = build_target_paths(app_context, files_folders)

    if passed_args:
        spinner = Spinner("ruff", f"{passed_args[0]}ing code")
        results = run(
            ["ruff", *passed_args, *dirs], stdout=PIPE, stderr=PIPE, on_error=OnError.PASS, running_hook=spinner
        )
        spinner.print_results(results)
    else:
        for action, spinner_action in ("check", "checking"), ("format", "formatting"):
            spinner = Spinner("ruff", f"{spinner_action} code")
            results = run(
                ["ruff", action, *dirs], stdout=PIPE, stderr=PIPE, on_error=OnError.PASS, running_hook=spinner
            )
            spinner.print_results(results)


def build_target_paths(
    app_context: AppContext[CorePluginConfig],
    files_folders: Optional[Tuple[str]] = None,
    include_tests: bool = True,
    include_commands: bool = True,
) -> List[Path]:
    if files_folders:
        return [Path(path) for path in files_folders]
    plugin_config = app_context.plugin_config
    target_paths: List[Path] = [plugin_config.sources_directory]

    if include_tests and plugin_config.tests_directory.exists():
        target_paths.append(plugin_config.tests_directory)
    if include_commands:
        target_paths.extend(
            folder for folder in app_context.pyproject_toml.tool.delfino.local_command_folders if folder.exists()
        )
    return target_paths


@click.command("lint", help=commands_group_help("lint"))
@files_folders_option
@pass_plugin_app_context
@click.pass_context
def run_group_lint(
    click_context: click.Context,
    app_context: AppContext[CorePluginConfig],
    **kwargs,
):
    del kwargs  # passed to downstream commands
    execute_commands_group(click_context, app_context.plugin_config)
