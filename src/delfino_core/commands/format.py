from pathlib import Path
from subprocess import PIPE, CompletedProcess
from typing import List, Optional, Tuple

import click
from delfino.decorators import files_folders_option, pass_args
from delfino.execution import OnError, run
from delfino.models import AppContext
from delfino.terminal_output import print_header, run_command_example
from delfino.validation import assert_pip_package_installed
from packaging.specifiers import SpecifierSet

from delfino_core.config import CorePluginConfig, pass_plugin_app_context
from delfino_core.utils import commands_group_help, execute_commands_group


def _check_result(
    app_context: AppContext[CorePluginConfig],
    result: CompletedProcess,
    check: bool,
    msg: str,
):
    if result.returncode == 1 and check:
        msg_lines = [
            f"{msg} before commit. Try following:",
            f" * Run formatter manually with `{run_command_example(run_group_format, app_context)}` "
            f"before committing code.",
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


def _default_files_folders(app_context: AppContext[CorePluginConfig]) -> Tuple[Path, ...]:
    return (
        app_context.plugin_config.sources_directory,
        app_context.plugin_config.tests_directory,
        *[folder for folder in app_context.pyproject_toml.tool.delfino.local_command_folders if folder.exists()],
    )


@click.command("pyupgrade")
@files_folders_option
@pass_args
@pass_plugin_app_context
def run_pyupgrade(
    app_context: AppContext[CorePluginConfig], passed_args: Tuple[str, ...], files_folders: Tuple[Path, ...], **kwargs
):
    """Runs pyupgrade with automatic version discovery.

    The Python version comes from the `pyproject.toml` file.
    """
    assert_pip_package_installed("pyupgrade")
    args = list(passed_args)

    if kwargs.get("check", False):
        args.append("--exit-zero-even-if-changed")

    python_version = app_context.pyproject_toml.tool.poetry.dependencies.get("python", "3")
    # see `pypgrade -h` for range of supported versions
    min_python_version = _find_min_minor_version(python_version, 3, 6, 11)
    args.append(f"--py3{min_python_version}-plus")

    print_header(
        f"Upgrading code to Python 3{'.' + min_python_version if min_python_version else ''}",
        icon="⬆️",
    )

    _check_result(
        app_context,
        run(
            [
                "pyupgrade",
                *_all_python_files(files_folders or _default_files_folders(app_context)),
                *args,
            ],
            on_error=OnError.PASS,
        ),
        bool("--exit-zero-even-if-changed" in args),
        "Code was not formatted",
    )


@click.command("black")
@files_folders_option
@pass_args
@pass_plugin_app_context
def run_black(
    app_context: AppContext[CorePluginConfig], passed_args: Tuple[str, ...], files_folders: Tuple[Path, ...], **kwargs
):
    """Runs black."""
    assert_pip_package_installed("black")
    args = list(passed_args)

    print_header("Formatting code", icon="🖤")

    if kwargs.get("check", False):
        args.append("--check")

    if kwargs.get("quiet", False):
        args.append("--quiet")

    _check_result(
        app_context,
        run(
            [
                "black",
                *args,
                *(files_folders or _default_files_folders(app_context)),
            ],
            on_error=OnError.PASS,
        ),
        bool("--check" in args),
        "Code was not formatted",
    )


@click.command("isort")
@files_folders_option
@pass_args
@pass_plugin_app_context
def run_isort(
    app_context: AppContext[CorePluginConfig], passed_args: Tuple[str, ...], files_folders: Tuple[Path, ...], **kwargs
):
    """Runs isort."""
    assert_pip_package_installed("isort")
    args = list(passed_args)

    print_header("Sorting imports", icon="ℹ")

    if kwargs.get("check", False):
        args.append("--check")

    if kwargs.get("quiet", False):
        args.append("--quiet")

    _check_result(
        app_context,
        run(
            [
                "isort",
                *args,
                *(files_folders or _default_files_folders(app_context)),
            ],
            on_error=OnError.PASS,
        ),
        bool("--check" in args),
        "Imports were not sorted",
    )


@click.command("ensure-pre-commit")
@pass_plugin_app_context
def run_ensure_pre_commit(app_context: AppContext[CorePluginConfig], **kwargs):
    """Ensures pre-commit is installed and enabled."""
    del kwargs  # not used, needed for extra kwargs from the command group
    if not app_context.plugin_config.disable_pre_commit:
        assert_pip_package_installed("pre-commit")
        # ensure pre-commit is installed
        run("pre-commit install", stdout=PIPE, on_error=OnError.EXIT)


@click.command("format", help=commands_group_help("format"))
@click.option("--check", is_flag=True, help="Only check formatting, don't reformat the code.")
@click.option("--quiet", is_flag=True, help="Don't show progress. Only errors.")
@files_folders_option
@pass_plugin_app_context
@click.pass_context
def run_group_format(
    click_context: click.Context,
    app_context: AppContext[CorePluginConfig],
    files_folders: Tuple[Path, ...],
    check: bool,
    quiet: bool,
):
    execute_commands_group(
        click_context,
        app_context.plugin_config,
        files_folders=files_folders,
        check=check,
        quiet=quiet,
    )
