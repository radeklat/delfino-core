from pathlib import Path
from subprocess import PIPE, CompletedProcess
from typing import List, Optional, Tuple

import click
from delfino.decorators import files_folders_option
from delfino.execution import OnError, run
from delfino.models import AppContext
from delfino.terminal_output import print_header, run_command_example
from delfino.validation import assert_pip_package_installed
from packaging.specifiers import SpecifierSet

from delfino_core.config import CorePluginConfig, pass_plugin_app_context


def _check_result(
    app_context: AppContext[CorePluginConfig],
    result: CompletedProcess,
    check: bool,
    msg: str,
):
    if result.returncode == 1 and check:
        msg_lines = [
            f"{msg} before commit. Try following:",
            f" * Run formatter manually with `{run_command_example(run_format, app_context)}` before committing code.",
        ]
        if not app_context.plugin_config.disable_pre_commit:
            msg_lines.insert(
                1,
                " * Enable pre-commit hook by running `pre-commit install` in the repository.",
            )

        click.secho(
            "\n".join(msg_lines),
            fg="red",
            err=True,
        )
        raise click.Abort()

    if result.returncode > 1:
        raise click.Abort()


def _major_minor_only(version_number: str) -> str:
    return ".".join(version_number.split(".")[:2])


def _find_min_minor_version(version_spec: str, major: int, minor_min: int, minor_max: int) -> Optional[str]:
    version_spec = version_spec.replace("^", ">=")

    # Drop patch and lower version number parts because they are not relevant.
    # For example, "3.8" does not fit "^3.8.1" and "3.9" would be mistakenly used.
    version_spec = ",".join(_major_minor_only(spec_part) for spec_part in version_spec.split(","))

    for minor in range(minor_min, minor_max + 1):
        version = f"{major}.{minor}"
        if SpecifierSet(version_spec).contains(version):
            return str(minor)

    return ""


def _all_python_files(files_folders: Tuple[Path, ...]) -> List[Path]:
    files = []

    for file_folder in files_folders:
        if file_folder.is_file() and file_folder.suffix == ".py":
            files.append(file_folder)
        elif file_folder.is_dir():
            files.extend(list(file_folder.glob("**/*.py")))
            files.extend(list(file_folder.glob("**/*.pyi")))

    return files


@click.command("format")
@click.option("--check", is_flag=True, help="Only check formatting, don't reformat the code.")
@click.option("--quiet", is_flag=True, help="Don't show progress. Only errors.")
@files_folders_option
@pass_plugin_app_context
def run_format(
    app_context: AppContext[CorePluginConfig],
    files_folders: Tuple[Path, ...],
    check: bool,
    quiet: bool,
):
    """Runs black code formatter and isort on source code."""
    plugin_config = app_context.plugin_config

    assert_pip_package_installed("isort")
    assert_pip_package_installed("black")
    assert_pip_package_installed("pyupgrade")

    if not plugin_config.disable_pre_commit:
        assert_pip_package_installed("pre-commit")
        # ensure pre-commit is installed
        run("pre-commit install", stdout=PIPE, on_error=OnError.EXIT)

    if not files_folders:
        files_folders = (
            plugin_config.sources_directory,
            plugin_config.tests_directory,
            *[folder for folder in app_context.pyproject_toml.tool.delfino.local_command_folders if folder.exists()],
        )

    python_version = app_context.pyproject_toml.tool.poetry.dependencies.get("python", "3")
    # see `pypgrade -h` for range of supported versions
    min_python_version = _find_min_minor_version(python_version, 3, 6, 11)
    flags = [f"--py3{min_python_version}-plus"]
    if not check:
        flags.append("--exit-zero-even-if-changed")

    print_header(
        f"Upgrading code to Python 3{'.' + min_python_version if min_python_version else ''}",
        icon="⬆️",
    )

    _check_result(
        app_context,
        run(
            ["pyupgrade", *_all_python_files(files_folders), *flags],
            on_error=OnError.PASS,
        ),
        check,
        "Code was not formatted",
    )

    flags = []

    if check:
        flags.append("--check")

    print_header("Sorting imports", icon="ℹ")

    _check_result(
        app_context,
        run(["isort", *files_folders, *flags], on_error=OnError.PASS),
        check,
        "Import were not sorted",
    )

    print_header("Formatting code", icon="🖤")

    if quiet:
        flags.append("--quiet")

    _check_result(
        app_context,
        run(["black", *files_folders, *flags], on_error=OnError.PASS),
        check,
        "Code was not formatted",
    )
