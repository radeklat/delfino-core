import logging
import re
from subprocess import PIPE
from typing import List, Tuple

import click
from delfino.decorators import pass_args
from delfino.execution import OnError, run

from delfino_core.utils import ask, assert_executable_installed

_LOGGER = logging.getLogger(__name__)
_INVALID_BRANCH_NAME_CHARS = re.compile(r"[^a-zA-Z0-9_-]+")


def _consume_args_until_next_option(passed_args: List[str]) -> Tuple[str, List[str]]:
    for index, arg in enumerate(passed_args):
        if arg.startswith("-"):
            return " ".join(passed_args[:index]), passed_args[index:]
    return " ".join(passed_args), []


def _sanitize_branch_name(branch_name: str) -> str:
    return _INVALID_BRANCH_NAME_CHARS.sub("_", branch_name.lower()).rstrip("_")


def _get_sanitized_used_name() -> str:
    # Get the current username from git config
    username = run(["git", "config", "user.email"], stdout=PIPE, on_error=OnError.ABORT).stdout.decode().strip()

    if not username:  # If not available, use the system username
        _LOGGER.warning("No git user.email found, using system username.")
        assert_executable_installed("whoami", required_by="gh")
        username = run(["whoami"], stdout=PIPE, on_error=OnError.ABORT).stdout.decode().strip()
    elif "@" in username:  # Strip the domain from the email address
        username = username.split("@")[0]

    # Sanitize the username
    return _sanitize_branch_name(username)


def _get_new_branch_name_or_switch_to_branch(title: str) -> Tuple[str, bool]:
    branch_prefix = f"{_get_sanitized_used_name()}/"
    branch_name = branch_prefix + _sanitize_branch_name(title)

    # Check if not already on the branch
    branch_exists = (
        run(["git", "branch", "--list", branch_name], stdout=PIPE, on_error=OnError.PASS).stdout.decode().strip()
    )

    if branch_exists:
        if branch_exists.startswith("* "):
            _LOGGER.warning(f"Already on branch '{branch_name}'.")
        else:
            _LOGGER.warning(f"Branch '{branch_name}' already exists, switching to it.")
            run(["git", "checkout", branch_name], on_error=OnError.ABORT)
    else:
        # Ask user if they want to use the branch name or let them choose a different one
        while not ask(f"Use branch name '{branch_name}'?"):
            new_branch_name = input(f"Enter a branch name: {branch_prefix}")
            sanitized_new_branch_name = _sanitize_branch_name(new_branch_name)
            if sanitized_new_branch_name == new_branch_name:  # not sanitized, use it
                branch_name = branch_prefix + new_branch_name
                break

    return branch_name, not branch_exists


@click.group("gh")
def run_gh():
    """Extends `gh` or passes through.

    If a `gh` sub-command is not extended, it will be passed through to the original `gh` command.

    See the help of the sub-commands for more details. See also https://cli.github.com/manual/ or `gh --help`.
    """
    assert_executable_installed("git", required_by="gh")
    assert_executable_installed("gh", required_by="gh")


@run_gh.group("pr")
def run_gh_pr():
    """Extends `gh pr` with additional functions and defaults.

    See the help of the sub-commands for more details.
    """


@run_gh_pr.command("create")
@pass_args
def run_gh_pr_create(passed_args: Tuple[str, ...]):
    """Extends `gh pr create` with additional functions and defaults.

    Defaults to `--assignee @me --base main --draft` and adds the title if provided.
    Title doesn't need to be quoted. Any word after the command that doesn't start with
    `-` is assumed to be the title.
    """
    title = None
    args = list(passed_args)
    if args and not args[0].startswith("-"):
        # First arg is not an option, assume it's the PR title
        title, args = _consume_args_until_next_option(args)

    run(
        [
            "gh",
            "pr",
            "create",
            "--assignee",
            "@me",
            "--base",
            "main",
            "--draft",
            "--body",
            "",
            *(["--title", title] if title else []),
            *args,
        ],
        on_error=OnError.ABORT,
    )


@run_gh_pr.command("start")
@pass_args
@click.pass_context
def run_gh_pr_start(click_context: click.Context, passed_args: Tuple[str, ...]):
    """Like `gh pr create`, but with additional functionality.

    - Asks for a title if not provided.
    - Stashes any uncommitted changes.
    - Switches to `main` first and pulls the latest changes.
    - Creates a new branch using git/system username and the title.
    - Creates an empty commit to be able to create a PR.
    - Push the branch and the commit to remote.
    - Pops the stash.
    """
    args = list(passed_args)
    title, args = _consume_args_until_next_option(args)
    while not title:
        title = input("Enter a title for the PR: ")

    branch_name, create_branch = _get_new_branch_name_or_switch_to_branch(title)

    if create_branch:
        run(["git", "stash"], on_error=OnError.ABORT)
        run(["git", "checkout", "main"], on_error=OnError.ABORT)
        run(["git", "pull"], on_error=OnError.ABORT)
        run(["git", "checkout", "-b", branch_name], on_error=OnError.ABORT)

        # Check if last commit messages is not title
        last_commit_message = run(
            ["git", "log", "-1", "--pretty=%B"], stdout=PIPE, on_error=OnError.ABORT
        ).stdout.decode()
        if not last_commit_message.startswith(title):
            # Create and empty commit to be able to create a PR
            run(["git", "commit", "--allow-empty", "-m", title], on_error=OnError.ABORT)

        run(["git", "push", "--set-upstream", "origin", branch_name], on_error=OnError.ABORT)
        run(["git", "stash", "pop"], on_error=OnError.ABORT)

    # Create the PR using gh
    click_context.forward(run_gh_pr_create, passed_args=["--title", title, *args])


@run_gh_pr.command("view")
@pass_args
def run_gh_pr_view(passed_args: Tuple[str, ...]):
    """Extends `gh pr view` with additional functions and defaults.

    Defaults to `--web`.
    """
    run(["gh", "pr", "view", "--web", *passed_args], on_error=OnError.ABORT)
