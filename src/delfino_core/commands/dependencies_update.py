from __future__ import annotations

import os
import re
import webbrowser
from datetime import datetime, timedelta
from subprocess import PIPE, CompletedProcess

import click
from click import secho
from delfino.constants import ENTRY_POINT, PackageManager
from delfino.decorators import pass_app_context
from delfino.execution import OnError, run
from delfino.models import AppContext
from delfino.terminal_output import print_header
from delfino.validation import assert_package_manager_is_known, assert_pip_package_installed

from delfino_core.commands.verify import run_group_verify
from delfino_core.config import CorePluginConfig
from delfino_core.spinner import Spinner
from delfino_core.utils import ask

try:
    from git import Repo
except ImportError:
    pass


def _run(args: str, spinner: Spinner | None = None) -> CompletedProcess:
    """Print the command before execution."""
    if spinner is None:
        return run(args, on_error=OnError.EXIT, stdout=PIPE, stderr=PIPE)

    result = run(args, on_error=OnError.PASS, running_hook=spinner, stdout=PIPE, stderr=PIPE)
    spinner.print_results(result, error_cls=click.exceptions.Exit)
    return result


class Updater:
    _FILENAME: str = ""

    @staticmethod
    def _git_root():
        return (
            run(["git", "rev-parse", "--show-toplevel"], stdout=PIPE, stderr=PIPE, on_error=OnError.EXIT)
            .stdout.decode()
            .strip()
        )

    def __init__(self, stash: bool):
        assert_pip_package_installed("gitpython")

        self._repo = Repo(self._git_root())
        self._stash = stash
        now = datetime.utcnow()
        self._start_of_week = now - timedelta(now.isoweekday() - 1)

    def commit_and_push(self):
        commit_message = f"Dependencies rollup: {self._start_of_week.strftime('%Y-%m-%d')}"
        can_update = self._repo.commit("HEAD").message.strip() == commit_message

        if do_commit := ask("Do you want to commit changes now?"):
            if can_update:  # update existing commit
                if self._repo.is_dirty():
                    _run("git pull")
                _run("git commit -a --amend -C HEAD")
            else:
                _run("git add .")
                _run(f"git commit -a -m '{commit_message}'")

        if do_commit and ask("Do you want to push changes now?"):
            if can_update:
                _run("git push --force-with-lease")
            else:
                _run("git push -u origin HEAD")

            url = self._link_to_open_a_pull_request()
            if url:
                if ask("Do you want to open a new pull request now in a web browser?"):
                    webbrowser.open(url)
                else:
                    secho(f"\nOpen a new pull request by visiting:\n\n\t{url}\n", fg="green")

    def _link_to_open_a_pull_request(self) -> str | None:
        url = self._repo.remote().url

        if not (match := re.match("git@github.com:(.*)\\.git", url)):
            match = re.match("https://github.com/(.*)\\.git", url)

        return f"https://github.com/{match.group(1)}/pull/new/{self._repo.active_branch}" if match else None

    def _read_dependency_file(self) -> str:
        with open(self._FILENAME, encoding="utf-8") as file:
            return file.read()

    def print_outdated_packages_and_lock_if_changed(self) -> bool:
        raise NotImplementedError

    def get_branch_name(self) -> str:
        email = self._repo.config_reader().get_value("user", "email")
        assert (
            email
        ), "Git config has not a commit email set. Please set it with:\n\tgit config --global user.email 'YOUR_EMAIL'"
        assert isinstance(email, str)

        user_name = re.sub("@.*", "", email)
        assert user_name, f"No user name could be parsed from git commit email '{email}' after removing '@.*'."
        assert isinstance(user_name, str)
        user_name = re.sub("[^a-zA-Z0-9._-]", "_", user_name)

        return f"{user_name}/dependencies_rollup_{self._start_of_week.strftime('%Y_%m_%d')}"

    @classmethod
    def _lock_and_sync(cls):
        pass

    def _show_edit_prompt_and_wait(self, *, available_updates: str):
        print("\n" + available_updates)
        input(
            f"\033[1;33mEdit {self._FILENAME} file to update any of the dependencies above ^^^\n\n"
            f"Then continue by pressing ENTER ...\033[0m"
        )

    def checkout_branch(self, branch: str):
        if str(self._repo.active_branch) == branch:
            secho(f"Branch '{branch}' already exists and active.", fg="green")
        elif branch in self._repo.branches:  # type: ignore[operator]
            secho(f"Branch '{branch}' already exists.", fg="yellow")
            _run(f"git checkout {branch}")
        else:
            if self._stash:
                secho("Stashing existing changes.", fg="yellow")
                _run("git stash")

            if self._repo.active_branch != "main":
                secho("Checking out 'main'.", fg="yellow")
                _run("git checkout main")

            secho("Pulling latest changes.", fg="yellow")
            _run("git pull")

            secho(f"Creating a new branch '{branch}'.", fg="yellow")
            _run(f"git checkout -b {branch}")
            self._lock_and_sync()

    def update(self, retry: bool):
        branch_name = self.get_branch_name()
        self.checkout_branch(branch_name)

        if not retry:
            while True:
                if not self.print_outdated_packages_and_lock_if_changed():
                    break

            secho("Running all tests to check the updated dependencies ... ", fg="yellow")


class PipenvUpdater(Updater):
    _FILENAME = "Pipfile"

    _SKIP_PATTERN = (
        "Skipped Update of Package (?P<package>[^:]+): (?P<installed>[^ ]+) "
        "installed.* (?P<available>[^ ]+) available.*"
    )
    _OUTDATED_PATTEN = (
        "Package '(?P<package>[^']+)' out-of-date: '(?P<installed>[^']+)' "
        "installed.* '(?P<available>[^']+)' available.*"
    )
    _VERSION_CONSTRAINT_CHARS = "=~<>"

    @classmethod
    def _lock_and_sync(cls):
        _run("pipenv lock")
        _run("pipenv sync -d")

    def print_outdated_packages_and_lock_if_changed(self) -> bool:
        spinner = Spinner("pipenv", "updating packages based on version pinning")
        _run("pipenv update -d", spinner)

        spinner = Spinner("pipenv", "checking outdated packages")
        result = _run("pipenv update --outdated", spinner)

        pipfile = self._read_dependency_file()

        available_updates = []

        for line in result.stdout.decode().split(os.linesep) + result.stderr.decode().split(os.linesep):
            if not (match := re.match(self._SKIP_PATTERN, line) or re.match(self._OUTDATED_PATTEN, line)):
                continue

            package = match.group("package")
            installed = match.group("installed").lstrip(self._VERSION_CONSTRAINT_CHARS)
            available = match.group("available").lstrip(self._VERSION_CONSTRAINT_CHARS)

            # Keep only packages defined in Pipfile with a different version available
            if installed != available and re.search(f'\n"?{package}"? ', pipfile):
                available_updates.append(f"{package}: {installed} -> {available}")

        if not available_updates:
            return False

        self._show_edit_prompt_and_wait(available_updates="\n".join(sorted(available_updates)) + "\n")

        return self._read_dependency_file() != pipfile


class PoetryUpdater(Updater):
    _FILENAME = "pyproject.toml"

    def print_outdated_packages_and_lock_if_changed(self) -> bool:
        spinner = Spinner("poetry", "updating packages based on version pinning")
        _run("poetry update", spinner)

        spinner = Spinner("poetry", "checking outdated packages")
        if not (result := _run("poetry show --outdated --why --ansi", spinner)).stdout:
            return False

        pyproject_toml = self._read_dependency_file()

        self._show_edit_prompt_and_wait(available_updates=result.stdout.decode())

        return self._read_dependency_file() != pyproject_toml


@click.command("dependencies-update")
@click.option("--retry", default=False, show_default=True, is_flag=True, help="Retry an update after failed tests.")
@click.option(
    "--stash/--no-stash",
    default=True,
    show_default=True,
    help=(
        "Don't stash existing changes. Useful when there are some existing manual changes "
        "that should be also part of the upgrade."
    ),
)
@pass_app_context(CorePluginConfig)
@click.pass_context
def run_dependencies_update(click_context: click.Context, app_context: AppContext, retry: bool, stash: bool):
    """Manages the process of updating dependencies."""
    print_header("Updating dependencies", icon="🔄")

    assert_package_manager_is_known(app_context.package_manager)
    updater: Updater

    if app_context.package_manager == PackageManager.PIPENV:
        updater = PipenvUpdater(stash)
    elif app_context.package_manager == PackageManager.POETRY:
        updater = PoetryUpdater(stash)
    else:
        raise AssertionError(
            f"The '{app_context.package_manager.value}' package manager is not supported by this command."
        )

    updater.update(retry)

    try:
        click_context.invoke(run_group_verify)
    except Exception:
        secho(
            f"\nOne or more checks have failed. Fix any issues above and then run:\n\n\t"
            f"{ENTRY_POINT} {click_context.info_name} --retry\n",
            fg="red",
        )
        raise

    updater.commit_and_push()
