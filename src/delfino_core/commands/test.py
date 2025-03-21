"""Tests on source code."""

import re
import shutil
import webbrowser
from contextlib import suppress
from itertools import chain
from pathlib import Path
from subprocess import PIPE
from typing import Optional

import click
from delfino.decorators import files_folders_option, pass_args
from delfino.execution import OnError, run
from delfino.models import AppContext
from delfino.terminal_output import print_header, run_command_example
from delfino.validation import assert_pip_package_installed

from delfino_core.config import CorePluginConfig, pass_plugin_app_context
from delfino_core.utils import commands_group_help, ensure_reports_dir, execute_commands_group


def _delete_coverage_dat_files(reports_directory: Path, test_types: list[str]):
    for test_type in [f"-{_}" for _ in test_types] + [""]:
        with suppress(FileNotFoundError):  # Use `missing_ok=True` from Python 3.8
            (reports_directory / f"coverage{test_type}.dat").unlink()


def _run_pytest(
    app_context: AppContext[CorePluginConfig],
    passed_args: tuple[str, ...],
    files_folders: tuple[str, ...],
    name: str = "",
) -> None:
    """Execute the tests for a given pytest type."""
    assert_pip_package_installed("pytest")
    assert_pip_package_installed("pytest-cov")
    assert_pip_package_installed("coverage")

    plugin_config = app_context.plugin_config

    if not files_folders:
        files_folders = (plugin_config.tests_directory / name,)
    elif name and (name not in plugin_config.test_types or not plugin_config.tests_directory):
        return

    header_name = f"{name} " if name else ""
    coverage_name = f"-{name}" if name else ""

    print_header(f"️Running {header_name}tests", icon="🔎🐛")
    ensure_reports_dir(plugin_config)

    args: list[Optional[str]] = [
        "pytest",
        "--cov",
        plugin_config.sources_directory,
        "--cov-report",
        f"xml:{plugin_config.reports_directory / f'coverage{coverage_name}.xml'}",
        "--cov-branch",
        "-vv",
        *passed_args,
        *files_folders,
    ]

    if plugin_config.pytest_modules:
        args = (
            ["python"]
            + list(chain.from_iterable(("-m", module) for module in plugin_config.pytest_modules))
            + ["--module"]
            + args
        )

    run(
        list(filter(None, args)),
        on_error=OnError.ABORT,
        env_update={"COVERAGE_FILE": plugin_config.reports_directory / f"coverage{coverage_name}.dat"},
        env_update_path={"PYTHONPATH": app_context.plugin_config.sources_directory},
    )


@click.command("pytest-unit", help="Run unit tests.")
@files_folders_option
@pass_args
@pass_plugin_app_context
def run_pytest_unit(
    app_context: AppContext[CorePluginConfig], passed_args: tuple[str, ...], files_folders: tuple[str, ...]
):
    _delete_coverage_dat_files(app_context.plugin_config.reports_directory, app_context.plugin_config.test_types)
    _run_pytest(app_context, passed_args, files_folders, "unit")


@click.command("pytest-integration", help="Run integration tests.")
@files_folders_option
@pass_args
@pass_plugin_app_context
def run_pytest_integration(
    app_context: AppContext[CorePluginConfig], passed_args: tuple[str, ...], files_folders: tuple[str, ...]
):
    # TODO(Radek): Replace with alias?
    _delete_coverage_dat_files(app_context.plugin_config.reports_directory, app_context.plugin_config.test_types)
    _run_pytest(app_context, passed_args, files_folders, "integration")


def _get_total_coverage(coverage_dat: Path) -> str:
    """Return coverage percentage, as captured in coverage dat file; e.g., returns "100%"."""
    output = run(
        "coverage report", stdout=PIPE, env_update={"COVERAGE_FILE": coverage_dat}, on_error=OnError.EXIT
    ).stdout.decode()

    if (match := re.search(r"TOTAL.*?([\d.]+%)", output)) is None:
        raise RuntimeError(f"Regex failed on output: {output}")
    return match.group(1)


def _combined_coverage_reports(reports_directory: Path, test_types: list[str]) -> Path:
    coverage_dat_combined = reports_directory / "coverage.dat"

    coverage_files = []  # we'll make a copy because `combine` will erase them

    for test_type in test_types:
        if not (coverage_dat := reports_directory / f"coverage-{test_type}.dat").exists():
            click.secho(
                f"Could not find coverage dat file for {test_type} tests: {coverage_dat}",
                fg="yellow",
            )
        else:
            print(f"{test_type.title()} test coverage: {_get_total_coverage(coverage_dat)}")

            temp_copy = coverage_dat.with_name(coverage_dat.name.replace(".dat", "-copy.dat"))
            shutil.copy(coverage_dat, temp_copy)
            coverage_files.append(temp_copy)

    if not coverage_files and coverage_dat_combined.exists():
        click.secho(
            "Could not find coverage dat files for individual tests but combined file exists. Using this file only.",
            fg="yellow",
        )
        return coverage_dat_combined

    run(
        ["coverage", "combine", *coverage_files],
        env_update={"COVERAGE_FILE": coverage_dat_combined},
        stdout=PIPE,
        on_error=OnError.EXIT,
    )

    return coverage_dat_combined


@click.command("coverage-report")
@pass_plugin_app_context
def run_coverage_report(app_context: AppContext[CorePluginConfig], **kwargs):
    """Analyse coverage and generate a term/HTML report.

    Combines all test types.
    """
    del kwargs  # additional unused arguments passed via `click.invoke` from other commands
    assert_pip_package_installed("coverage")

    print_header("Generating coverage report", icon="📃")
    plugin_config = app_context.plugin_config
    ensure_reports_dir(plugin_config)

    coverage_dat_combined = _combined_coverage_reports(plugin_config.reports_directory, plugin_config.test_types)
    coverage_html = plugin_config.reports_directory / "coverage-report/"

    run(
        ["coverage", "html", "-d", coverage_html],
        env_update={"COVERAGE_FILE": coverage_dat_combined},
        stdout=PIPE,
        on_error=OnError.EXIT,
    )

    print(f"Total coverage: {_get_total_coverage(coverage_dat_combined)}\n")
    print(
        f"Refer to coverage report for full analysis in '{coverage_html}/index.html'\n"
        f"Or open the report in your default browser with:\n"
        f"  {run_command_example(run_coverage_open, app_context)}"
    )


@click.command("pytest")
@files_folders_option
@pass_plugin_app_context
@pass_args
def run_pytest(app_context: AppContext[CorePluginConfig], passed_args: tuple[str, ...], files_folders: tuple[str, ...]):
    """Runs pytest for individual test suites.

    Configration in the `pyproject.toml` file under `tool.delfino.plugins.delfino-core`:

      - `tests_directory`: the location of your tests.

      - `test_types`: the types of tests you have. This needs to match folders
    nested under the `tests_directory`.

      - `reports_directory`: test coverage information is gathered and stored here.
    """
    _delete_coverage_dat_files(app_context.plugin_config.reports_directory, app_context.plugin_config.test_types)
    for name in [""] if files_folders else app_context.plugin_config.test_types:
        _run_pytest(app_context, passed_args, files_folders, name)


@click.command("test", help=commands_group_help("test"))
@files_folders_option
@pass_plugin_app_context
@click.pass_context
def run_group_test(
    click_context: click.Context,
    app_context: AppContext[CorePluginConfig],
    files_folders: tuple[Path, ...],
):
    execute_commands_group(click_context, app_context.plugin_config, files_folders=files_folders)


@click.command("coverage-open")
@pass_plugin_app_context
def run_coverage_open(app_context: AppContext[CorePluginConfig]):
    """Open coverage results in default browser."""
    report_index = app_context.plugin_config.reports_directory / "coverage-report" / "index.html"
    if not report_index.exists():
        click.secho(
            f"Could not find coverage report '{report_index}'. Ensure that the report has been built.\n"
            "Try one of the following:\n"
            f"  {run_command_example(run_coverage_report, app_context)}\n"
            f"or\n"
            f"  {run_command_example(run_group_test, app_context)}",
            fg="red",
        )

        raise click.exceptions.Exit(code=1)
    webbrowser.open(f"file:///{report_index.absolute()}")
