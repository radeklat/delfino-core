import os
import re
import shlex
import subprocess
from datetime import datetime, timedelta
from typing import Optional

import click
from click import secho
from delfino.constants import ENTRY_POINT, PackageManager
from delfino.decorators import pass_app_context
from delfino.execution import OnError, run
from delfino.models import AppContext
from delfino.terminal_output import print_header
from delfino.utils import ArgsType
from delfino.validation import assert_package_manager_is_known, assert_pip_package_installed

from delfino_core.backports import shlex_join
from delfino_core.commands.verify_all import verify_all
from delfino_core.config import CorePluginConfig

try:
    from git import Repo
except ImportError:
    pass


def _trace(args: str) -> subprocess.CompletedProcess:
    """Print the command before execution."""
    _args: ArgsType = shlex.split(args)
    secho(shlex_join(_args), fg="white")
    return run(_args, on_error=OnError.EXIT, capture_output=True)


class Updater:
    _FILENAME: str = ""

    @staticmethod
    def _git_root():
        return (
            run(["git", "rev-parse", "--show-toplevel"], capture_output=True, on_error=OnError.EXIT)
            .stdout.decode()
            .strip()
        )

    def __init__(self):
        assert_pip_package_installed("gitpython")

        self._repo = Repo(self._git_root())
        now = datetime.utcnow()
        self._start_of_week = now - timedelta(now.isoweekday() - 1)

    def commit_and_push(self):
        commit_message = f"Dependencies rollup: {self._start_of_week.strftime('%Y-%m-%d')}"
        can_update = self._repo.commit("HEAD").message.strip() == commit_message

        if input("\033[1;33mDo you want to commit changes now? [Y/n]: \033[0m").lower() == "y":
            if can_update:  # update existing commit
                if self._repo.is_dirty():
                    _trace("git pull")
                _trace("git commit -a --amend -C HEAD")
            else:
                _trace("git add .")
                _trace(f"git commit -a -m '{commit_message}'")

        if input("\033[1;33mDo you want to push changes now? [Y/n]: \033[0m").lower() == "y":
            if can_update:
                _trace("git push --force-with-lease")
            else:
                _trace("git push -u origin HEAD")

            url = self._link_to_open_a_pull_request()
            if url:
                secho(f"\nOpen a new pull request by visiting:\n\n\t{url}\n", fg="green")

    def _link_to_open_a_pull_request(self) -> Optional[str]:
        url = self._repo.remote().url
        match = re.match("git@github.com:(.*)\\.git", url)
        if not match:
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
            _trace(f"git checkout {branch}")
        else:
            _trace("git stash")
            if self._repo.active_branch != "main":
                _trace("git checkout main")
            _trace("git pull")
            _trace(f"git checkout -b {branch}")
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
        _trace("pipenv lock")
        _trace("pipenv sync -d")

    def print_outdated_packages_and_lock_if_changed(self) -> bool:
        secho("Updating packages based on version pinning. This will take a while ...", fg="yellow")
        _trace("pipenv update -d")

        secho("Checking outdated packages. This will take a while ...", fg="yellow")
        result = _trace("pipenv update --outdated")

        pipfile = self._read_dependency_file()

        available_updates = []

        for line in result.stdout.decode().split(os.linesep) + result.stderr.decode().split(os.linesep):
            match = re.match(self._SKIP_PATTERN, line) or re.match(self._OUTDATED_PATTEN, line)
            if not match:
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
        secho("Updating packages based on version pinning. This will take a while ...", fg="yellow")
        _trace("poetry update")

        secho("Checking outdated packages. This will take a while ...", fg="yellow")
        result = _trace("poetry show --outdated --why --ansi")

        if not result.stdout:
            return False

        pyproject_toml = self._read_dependency_file()

        self._show_edit_prompt_and_wait(available_updates=result.stdout.decode())

        return self._read_dependency_file() != pyproject_toml


@click.command()
@click.option("--retry", default=False, show_default=True, is_flag=True, help=" Retry an update after failed tests.")
@pass_app_context(CorePluginConfig)
@click.pass_context
def dependencies_update(click_context: click.Context, app_context: AppContext, retry):
    """Manages the process of updating dependencies."""
    print_header("Updating dependencies", icon="🔄")

    assert_package_manager_is_known(app_context.package_manager)
    updater: Updater

    if app_context.package_manager == PackageManager.PIPENV:
        updater = PipenvUpdater()
    elif app_context.package_manager == PackageManager.POETRY:
        updater = PoetryUpdater()
    else:
        raise AssertionError(
            f"The '{app_context.package_manager.value}' package manager is not supported by this command."
        )

    updater.update(retry)

    try:
        click_context.invoke(verify_all)
    except Exception:
        secho(
            f"\nOne or more checks have failed. Fix any issues above and then run:\n\n\t"
            f"{ENTRY_POINT} {click_context.info_name} --retry\n",
            fg="red",
        )
        raise

    updater.commit_and_push()
