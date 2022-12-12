"""Linting checks on source code."""
import logging
from functools import lru_cache
from itertools import groupby
from os import getenv
from pathlib import Path
from subprocess import PIPE
from typing import List, Optional, Tuple

import click
from delfino.decorators import files_folders_option, pass_args
from delfino.execution import OnError, run
from delfino.models import AppContext
from delfino.terminal_output import print_header, print_no_issues_found
from delfino.validation import assert_pip_package_installed, pip_package_installed

from delfino_core.backports import path_is_relative_to
from delfino_core.config import CorePluginConfig, pass_plugin_app_context
from delfino_core.utils import execute_commands_group


@click.command()
@pass_args
@files_folders_option
@pass_plugin_app_context
def lint_pydocstyle(app_context: AppContext[CorePluginConfig], passed_args: Tuple[str, ...], files_folders: Tuple[str]):
    """Run docstring linting on source code.

    Docstring linting is done via pydocstyle. The pydocstyle config can be found in the
    `pyproject.toml` file under `[tool.pydocstyle]`. This ensures compliance with PEP 257,
    with a few exceptions. Note that pylint also carries out additional documentation
    style checks.
    """
    assert_pip_package_installed("pydocstyle")

    print_header("documentation style", level=2)
    dirs = build_target_paths(app_context, files_folders, False, False)

    run(
        ["pydocstyle", *passed_args, *dirs],
        stdout=PIPE,
        on_error=OnError.ABORT,
        env_update_path={"PYTHONPATH": app_context.plugin_config.sources_directory},
    )

    print_no_issues_found()


@click.command()
@pass_args
@files_folders_option
@pass_plugin_app_context
def lint_pycodestyle(
    app_context: AppContext[CorePluginConfig], passed_args: Tuple[str, ...], files_folders: Tuple[str]
):
    """Run PEP8 checking on code.

    PEP8 checking is done via pycodestyle.

    Why pycodestyle and pylint? So far, pylint does not check against every convention in PEP8. As pylint's
    functionality grows, we should move all PEP8 checking to pylint and remove pycodestyle.
    """
    assert_pip_package_installed("pycodestyle")

    print_header("code style (PEP8)", level=2)

    dirs = build_target_paths(app_context, files_folders)

    # TODO(Radek): Implement unofficial config support in pyproject.toml by parsing it
    #  and outputting the result into a supported format?
    #  See:
    #    - https://github.com/PyCQA/pycodestyle/issues/813
    #    - https://github.com/PyCQA/pydocstyle/issues/447
    args = [
        "pycodestyle",
        "--ignore",
        "E501,W503,E231,E203,E402",
        "--exclude",
        ".svn,CVS,.bzr,.hg,.git,__pycache__,.tox,*_config_parser.py",
        *passed_args,
        *dirs,
    ]
    run(
        args,
        stdout=PIPE,
        on_error=OnError.ABORT,
        env_update_path={"PYTHONPATH": app_context.plugin_config.sources_directory},
    )
    # Ignores explained:
    # - E501: Line length is checked by PyLint
    # - W503: Disable checking of "Line break before binary operator". PEP8 recently (~2019) switched to
    #         "line break before the operator" style, so we should permit this usage.
    # - E231: "missing whitespace after ','" is a false positive. Handled by black formatter.

    print_no_issues_found()


def run_pylint(
    sources_dir: Path,
    checked_dirs: List[Path],
    pylintrc_folder: Path,
    passed_args: Tuple[str, ...],
):
    print_header(", ".join(map(str, checked_dirs)), level=3)

    run(
        ["pylint", "-j", str(cpu_count()), "--rcfile", pylintrc_folder / ".pylintrc", *passed_args, *checked_dirs],
        stdout=PIPE,
        on_error=OnError.ABORT,
        env_update_path={"PYTHONPATH": sources_dir},
    )

    print_no_issues_found()


@lru_cache(maxsize=1)
def cpu_count():
    if getenv("CI", ""):
        cpu_shares = Path("/sys/fs/cgroup/cpu/cpu.shares")
        if cpu_shares.is_file():
            return int(cpu_shares.read_text(encoding="utf-8").strip()) // 1024

    log = logging.getLogger("cpu_count")
    fallback_msg = "Number of CPUs could not be determined. Falling back to 1."

    if pip_package_installed("psutil"):
        import psutil  # pylint: disable=import-outside-toplevel

        count = psutil.cpu_count(logical=False)
        if not count:
            log.warning(fallback_msg)
            return 1
        return count

    log.warning(f"`psutil` is not installed. {fallback_msg}")
    return 1


def build_target_paths(
    app_context: AppContext[CorePluginConfig],
    files_folders: Optional[Tuple[str]] = None,
    include_tests: bool = True,
    include_commands: bool = True,
) -> List[Path]:
    if files_folders:
        return [Path(path) for path in files_folders]
    local_commands_directory = app_context.pyproject_toml.tool.delfino.local_commands_directory
    plugin_config = app_context.plugin_config
    target_paths: List[Path] = [plugin_config.sources_directory]

    if include_tests and plugin_config.tests_directory.exists():
        target_paths.append(plugin_config.tests_directory)
    if include_commands and local_commands_directory.exists():
        target_paths.append(local_commands_directory)
    return target_paths


@click.command()
@files_folders_option
@pass_args
@pass_plugin_app_context
def lint_pylint(app_context: AppContext[CorePluginConfig], passed_args: Tuple[str, ...], files_folders: Tuple[str]):
    """Run pylint on code.

    The bulk of our code conventions are enforced via pylint. The pylint config can be
    found in the `.pylintrc` file.
    """
    assert_pip_package_installed("pylint")

    print_header("pylint", level=2)
    plugin_config = app_context.plugin_config

    def get_pylintrc_folder(path: Path) -> Path:
        if plugin_config.tests_directory.exists() and path_is_relative_to(path, plugin_config.tests_directory):
            return plugin_config.tests_directory
        return app_context.project_root

    target_paths = build_target_paths(app_context, files_folders)
    grouped_paths = groupby(target_paths, get_pylintrc_folder)
    for pylintrc_folder, paths in grouped_paths:
        run_pylint(app_context.plugin_config.sources_directory, list(paths), pylintrc_folder, passed_args)


@click.command(help="Runs all linting commands. Configured by the ``lint_commands`` setting.")
@files_folders_option
@pass_plugin_app_context
@click.pass_context
def lint(click_context: click.Context, app_context: AppContext[CorePluginConfig], files_folders: Tuple[str]):
    execute_commands_group("lint", click_context, app_context.plugin_config, files_folders=files_folders)
