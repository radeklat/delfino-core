"""Tests on source code."""

import re
import shutil
import webbrowser
from pathlib import Path
from subprocess import PIPE
from typing import List, Optional

import click
from delfino.decorators import pass_args
from delfino.execution import OnError, run
from delfino.models import AppContext
from delfino.terminal_output import print_header, run_command_example
from delfino.validation import assert_pip_package_installed

from delfino_core.config import CorePluginConfig, pass_plugin_app_context
from delfino_core.utils import ensure_reports_dir


def _run_tests(
    app_context: AppContext[CorePluginConfig], name: str, passed_args: List[str], maxfail: int, debug: bool
) -> None:
    """Execute the tests for a given test type."""
    assert_pip_package_installed("pytest")
    assert_pip_package_installed("pytest-cov")
    assert_pip_package_installed("coverage")

    plugin_config = app_context.plugin_config

    if name not in plugin_config.test_types or not plugin_config.tests_directory:
        return

    print_header(f"️Running {name} tests️", icon="🔎🐛")
    ensure_reports_dir(plugin_config)
    args: List[Optional[str]] = [
        "pytest",
        "--cov",
        plugin_config.sources_directory,
        "--cov-report",
        f"xml:{plugin_config.reports_directory / f'coverage-{name}.xml'}",
        "--cov-branch",
        "-vv",
        "--maxfail",
        str(maxfail),
        "-s" if debug else "",
        *passed_args,
        plugin_config.tests_directory / name,
    ]
    run(
        list(filter(None, args)),
        env_update={"COVERAGE_FILE": plugin_config.reports_directory / f"coverage-{name}.dat"},
        on_error=OnError.ABORT,
    )


@click.command(help="Run unit tests.")
@click.option("--maxfail", type=int, default=0)
@click.option("--debug", is_flag=True, help="Disables capture, allowing debuggers like `pdb` to be used.")
@pass_args
@pass_plugin_app_context
def test_unit(app_context: AppContext[CorePluginConfig], passed_args: List[str], maxfail: int, debug: bool):
    _run_tests(app_context, "unit", passed_args, maxfail=maxfail, debug=debug)


@click.command(help="Run integration tests.")
@click.option("--maxfail", type=int, default=0)
@click.option("--debug", is_flag=True, help="Disables capture, allowing debuggers like `pdb` to be used.")
@pass_args
@pass_plugin_app_context
def test_integration(app_context: AppContext[CorePluginConfig], passed_args: List[str], maxfail: int, debug: bool):
    # TODO(Radek): Replace with alias?
    _run_tests(app_context, "integration", passed_args, maxfail=maxfail, debug=debug)


def _get_total_coverage(coverage_dat: Path) -> str:
    """Return coverage percentage, as captured in coverage dat file; e.g., returns "100%"."""
    output = run(
        "coverage report", stdout=PIPE, env_update={"COVERAGE_FILE": coverage_dat}, on_error=OnError.EXIT
    ).stdout.decode()
    match = re.search(r"TOTAL.*?([\d.]+%)", output)
    if match is None:
        raise RuntimeError(f"Regex failed on output: {output}")
    return match.group(1)


@click.command()
@pass_plugin_app_context
def coverage_report(app_context: AppContext[CorePluginConfig]):
    """Analyse coverage and generate a term/HTML report.

    Combines all test types.
    """
    assert_pip_package_installed("coverage")

    print_header("Generating coverage report", icon="📃")
    plugin_config = app_context.plugin_config
    ensure_reports_dir(plugin_config)

    coverage_dat_combined = plugin_config.reports_directory / "coverage.dat"
    coverage_html = plugin_config.reports_directory / "coverage-report/"
    coverage_files = []  # we'll make a copy because `combine` will erase them

    for test_type in plugin_config.test_types:
        coverage_dat = plugin_config.reports_directory / f"coverage-{test_type}.dat"

        if not coverage_dat.exists():
            click.secho(
                f"Could not find coverage dat file for {test_type} tests: {coverage_dat}",
                fg="yellow",
            )
        else:
            print(f"{test_type.title()} test coverage: {_get_total_coverage(coverage_dat)}")

            temp_copy = coverage_dat.with_name(coverage_dat.name.replace(".dat", "-copy.dat"))
            shutil.copy(coverage_dat, temp_copy)
            coverage_files.append(temp_copy)

    env = {"COVERAGE_FILE": coverage_dat_combined}
    run(["coverage", "combine", *coverage_files], env_update=env, stdout=PIPE, on_error=OnError.EXIT)
    run(["coverage", "html", "-d", coverage_html], env_update=env, stdout=PIPE, on_error=OnError.EXIT)

    print(f"Total coverage: {_get_total_coverage(coverage_dat_combined)}\n")
    print(
        f"Refer to coverage report for full analysis in '{coverage_html}/index.html'\n"
        f"Or open the report in your default browser with:\n"
        f"  {run_command_example(coverage_open, app_context)}"
    )


@click.command(help="Run all tests, and generate coverage report.")
@click.pass_context
def test_all(click_context: click.Context):
    print_header("Run all tests, and generate coverage report.", icon="🔎🐛📃")
    click_context.forward(test_unit)
    click_context.forward(test_integration)
    click_context.forward(coverage_report)


@click.command(help="Open coverage results in default browser.")
@pass_plugin_app_context
def coverage_open(app_context: AppContext[CorePluginConfig]):
    report_index = app_context.plugin_config.reports_directory / "coverage-report" / "index.html"
    if not report_index.exists():
        click.secho(
            f"Could not find coverage report '{report_index}'. Ensure that the report has been built.\n"
            "Try one of the following:\n"
            f"  {run_command_example(coverage_report, app_context)}\n"
            f"or\n"
            f"  {run_command_example(test_all, app_context)}",
            fg="red",
        )

        raise click.exceptions.Exit(code=1)
    webbrowser.open(f"file:///{report_index.absolute()}")
