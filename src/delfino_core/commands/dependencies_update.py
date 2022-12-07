import os
import re
import shlex
import subprocess
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Optional

import click
from click import secho
from delfino.constants import PackageManager
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


_SKIP_PATTERN = (
    "Skipped Update of Package (?P<package>[^:]+): (?P<installed>[^ ]+) installed.* (?P<available>[^ ]+) available.*"
)
_OUTDATED_PATTEN = (
    "Package '(?P<package>[^']+)' out-of-date: '(?P<installed>[^']+)' installed.* '(?P<available>[^']+)' available.*"
)
_VERSION_CONSTRAINT_CHARS = "=~<>"


@lru_cache(maxsize=1)
def _git_root():
    return (
        run(["git", "rev-parse", "--show-toplevel"], capture_output=True, on_error=OnError.EXIT).stdout.decode().strip()
    )


def _trace(args: str) -> subprocess.CompletedProcess:
    """Print the command before execution."""
    _args: ArgsType = shlex.split(args)
    print(shlex_join(_args))
    return run(_args, on_error=OnError.EXIT, capture_output=True)


def _get_branch_name(repo: "Repo", start_of_week: datetime) -> str:
    email = repo.config_reader().get_value("user", "email")
    assert email, (
        "Git config has not a commit email set. Please set it with:" "\n\tgit config --global user.email 'YOUR_EMAIL'"
    )
    assert isinstance(email, str)

    user_name = re.sub("@.*", "", email)
    assert user_name, f"No user name could be parsed from git commit email '{email}' after removing '@.*'."
    assert isinstance(user_name, str)
    user_name = re.sub("[^a-zA-Z0-9._-]", "_", user_name)

    return f"{user_name}/dependencies_rollup_{start_of_week.strftime('%Y_%m_%d')}"


def _checkout_branch(repo: "Repo", branch: str):
    if str(repo.active_branch) == branch:
        secho(f"Branch '{branch}' already exists and active.", fg="green")
    elif branch in repo.branches:  # type: ignore[operator]
        secho(f"Branch '{branch}' already exists.", fg="yellow")
        _trace(f"git checkout {branch}")
    else:
        _trace("git stash")
        if repo.active_branch != "main":
            _trace("git checkout main")
        _trace("git pull")
        _trace(f"git checkout -b {branch}")
        _trace("pipenv lock")
        _trace("pipenv sync -d")


def _print_outdated_packages_and_lock_if_changed() -> bool:
    secho("Updating packages based on version pinning. This will take a while ...", fg="yellow")
    _trace("pipenv update -d")

    secho("Checking outdated packages. This will take a while ...", fg="yellow")
    result = _trace("pipenv update --outdated")

    with open("Pipfile", encoding="utf-8") as file:
        pipfile = file.read()

    available_updates = []

    for line in result.stdout.decode().split(os.linesep) + result.stderr.decode().split(os.linesep):
        match = re.match(_SKIP_PATTERN, line) or re.match(_OUTDATED_PATTEN, line)
        if not match:
            continue

        package = match.group("package")
        installed = match.group("installed").lstrip(_VERSION_CONSTRAINT_CHARS)
        available = match.group("available").lstrip(_VERSION_CONSTRAINT_CHARS)

        # Keep only packages defined in Pipfile with a different version available
        if installed != available and re.search(f'\n"?{package}"? ', pipfile):
            available_updates.append(f"{package}: {installed} -> {available}")

    if not available_updates:
        return False

    print("\n" + "\n".join(sorted(available_updates)) + "\n")
    input(
        "\033[1;33mEdit Pipfile.lock file to update any of the dependencies above ^^^\n\n"
        "Then continue by pressing ENTER ...\033[0m"
    )

    with open("Pipfile", encoding="utf-8") as file:
        return file.read() != pipfile


def _commit_and_push(repo: "Repo", commit_message: str):
    can_update = repo.commit("HEAD").message.strip() == commit_message

    if input("\033[1;33mDo you want to commit changes now? [Y/n]: \033[0m").lower() == "y":
        if can_update:  # update existing commit
            if repo.is_dirty():
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

        url = _link_to_open_a_pull_request(repo)
        if url:
            secho(f"\nOpen a new pull request by visiting:\n\n\t{url}\n", fg="green")


def _link_to_open_a_pull_request(repo: "Repo") -> Optional[str]:
    url = repo.remote().url
    match = re.match("git@github.com:(.*)\\.git", url)
    if not match:
        match = re.match("https://github.com/(.*)\\.git", url)

    return f"https://github.com/{match.group(1)}/pull/new/{repo.active_branch}" if match else None


@click.command()
@click.option("--retry", default=False, show_default=True, is_flag=True, help=" Retry an update after failed tests.")
@pass_app_context(CorePluginConfig)
@click.pass_context
def dependencies_update(click_context: click.Context, app_context: AppContext, retry):
    """Manages the process of updating dependencies."""
    print_header("Updating dependencies", icon="🔄")

    assert_package_manager_is_known(app_context.package_manager)
    assert (
        app_context.package_manager == PackageManager.PIPENV
    ), f"Only the '{PackageManager.PIPENV.value}' package manager is supported by this command."
    assert_pip_package_installed("gitpython")

    now = datetime.utcnow()
    start_of_week = now - timedelta(days=now.isoweekday() - 1)
    repo = Repo(_git_root())

    branch_name = _get_branch_name(repo, start_of_week)
    _checkout_branch(repo, branch_name)

    if not retry:
        while True:
            if not _print_outdated_packages_and_lock_if_changed():
                break

        secho("Running all tests to check the updated dependencies ... ", fg="yellow")

    try:
        click_context.invoke(verify_all)
    except Exception:
        secho(
            "\nOne or more checks have failed. Fix any issues above and then run:\n\n\t"
            "inv dependencies-update --retry\n",
            fg="red",
        )
        raise

    commit_message = f"Dependencies rollup: {start_of_week.strftime('%Y-%m-%d')}"
    _commit_and_push(repo, commit_message)
