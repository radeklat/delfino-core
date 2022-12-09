"""Type checking on source code."""

from itertools import groupby
from pathlib import Path
from typing import List, Tuple

import click
from delfino.decorators import files_folders_option, pass_args
from delfino.execution import OnError, run
from delfino.models import AppContext
from delfino.terminal_output import print_header
from delfino.utils import ArgsList
from delfino.validation import assert_pip_package_installed

from delfino_core.config import CorePluginConfig, pass_plugin_app_context
from delfino_core.utils import ensure_reports_dir


def _run_typecheck(
    paths: List[Path],
    strict: bool,
    reports_file: Path,
    summary_only: bool,
    mypypath: Path,
    print_second_level_headers: bool,
    passed_args: Tuple[str, ...],
):
    args: ArgsList = [
        "mypy",
        "--show-column-numbers",
        "--show-error-codes",
        "--color-output",
        "--warn-unused-config",
        "--warn-unused-ignores",
        "--color-output",
        "--allow-untyped-decorators",
        "--follow-imports",
        "silent",
        "--junit-xml",
        reports_file,
        *passed_args,
    ]

    if strict:
        args.append("--strict")

    args.extend(paths)

    if summary_only:
        args.extend(["|", "tail", "-n", "1"])

    if print_second_level_headers:
        print_header(f"{'Strict' if strict else 'Optional'} types", level=2, icon="⚠️" if strict else "ℹ️")

    run(args, env_update_path={"MYPYPATH": mypypath}, on_error=OnError.ABORT)


def is_path_relative_to_paths(path: Path, paths: List[Path]) -> bool:
    for _path in paths:
        try:
            path.relative_to(_path)
            return True
        except ValueError:
            continue
    return False


@click.command()
@click.option("--summary-only", is_flag=True, help="Suppress error messages and show only summary error count.")
@files_folders_option
@pass_args
@pass_plugin_app_context
def typecheck(
    app_context: AppContext[CorePluginConfig],
    passed_args: Tuple[str, ...],
    summary_only: bool,
    files_folders: Tuple[str, ...],
):
    """Run type checking on source code.

    A non-zero return code from this task indicates invalid types were discovered.
    """
    assert_pip_package_installed("mypy")

    print_header("RUNNING TYPE CHECKER", icon="🔠")

    plugin_config = app_context.plugin_config
    ensure_reports_dir(plugin_config)

    if files_folders:
        target_paths = [Path(path) for path in files_folders]
    else:
        target_paths = [plugin_config.sources_directory, plugin_config.tests_directory]
        if app_context.pyproject_toml.tool.delfino.local_commands_directory.exists():
            target_paths.append(app_context.pyproject_toml.tool.delfino.local_commands_directory)

    strict_paths = plugin_config.typecheck.strict_directories
    grouped_paths = groupby(target_paths, lambda current_path: is_path_relative_to_paths(current_path, strict_paths))

    for force_typing, group in grouped_paths:
        report_filepath = (
            plugin_config.reports_directory / "typecheck" / f"junit-{'strict' if force_typing else 'nonstrict'}.xml"
        )
        _run_typecheck(
            list(group),
            force_typing,
            report_filepath,
            summary_only,
            plugin_config.sources_directory,
            bool(strict_paths),
            passed_args,
        )
