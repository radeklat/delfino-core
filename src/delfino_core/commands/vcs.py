from __future__ import annotations

from subprocess import PIPE
from typing import Literal

import click
from delfino import run
from delfino.decorators import pass_args
from delfino.execution import OnError
from delfino.models import AppContext

from delfino_core.config import CorePluginConfig, pass_plugin_app_context
from delfino_core.utils import assert_executable_installed
from delfino_core.vcs_tools import (
    consume_args_until_next_option,
    get_new_branch_name_or_switch_to_branch,
    get_trunk_branch,
    get_vcs_cli_tool,
)


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
def run_gh_pr_create(passed_args: tuple[str, ...]):
    """Extends `gh pr create` with additional functions and defaults.

    Defaults to `--assignee @me --base main --draft` and adds the title if provided.
    Title doesn't need to be quoted. Any word after the command that doesn't start with
    `-` is assumed to be the title.
    """
    title = None
    args = list(passed_args)
    if args and not args[0].startswith("-"):
        # First arg is not an option, assume it's the PR title
        title, args = consume_args_until_next_option(args)

    run(
        [
            "gh",
            "pr",
            "create",
            "--assignee",
            "@me",
            "--base",
            get_trunk_branch(),
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
@pass_plugin_app_context
@click.pass_context
def run_gh_pr_start(
    click_context: click.Context,
    app_context: AppContext[CorePluginConfig],
    passed_args: tuple[str, ...],
):
    """Like `gh pr create`, but with additional functionality.

    - Asks for a title if not provided.
    - Stashes any uncommitted changes.
    - Switches to `main` first and pulls the latest changes.
    - Creates a new branch using git/system username and the title.
    - Creates an empty commit to be able to create a PR.
    - Push the branch and the commit to remote.
    - Pops the stash.
    """
    _run_vcs_start(app_context, click_context, passed_args, "gh")


@run_gh_pr.command("view")
@pass_args
def run_gh_pr_view(passed_args: tuple[str, ...]):
    """Extends `gh pr view` with additional functions and defaults.

    Defaults to `--web`.
    """
    run(["gh", "pr", "view", "--web", *passed_args], on_error=OnError.ABORT)


@click.group("glab")
def run_glab():
    """Extends `glab` or passes through.

    If a `glab` sub-command is not extended, it will be passed through to the original `glab` command.

    See the help of the sub-commands for more details. See also https://gitlab.com/gitlab-org/cli or `glab --help`.
    """
    assert_executable_installed("git", required_by="gh")
    assert_executable_installed("glab", required_by="gh")


@run_glab.group("mr")
def run_glab_mr():
    """Extends `glab mr` with additional functions and defaults.

    See the help of the sub-commands for more details.
    """


@run_glab_mr.command("create")
@pass_args
def run_glab_mr_create(passed_args: tuple[str, ...]):
    """Extends `glab mr create` with additional functions and defaults.

    Defaults to `--assignee @me --create-source-branch --target-branch <TRUNK> --draft` and adds the title if provided.
    Title doesn't need to be quoted. Any word after the command that doesn't start with
    `-` is assumed to be the title.
    """
    title = None
    args = list(passed_args)
    if args and not args[0].startswith("-"):
        # First arg is not an option, assume it's the PR title
        title, args = consume_args_until_next_option(args)

    run(
        [
            "glab",
            "mr",
            "create",
            "--create-source-branch",
            "--assignee",
            "@me",
            "--target-branch",
            get_trunk_branch(),
            "--draft",
            *(["--title", title] if title else []),
            *args,
        ],
        on_error=OnError.ABORT,
    )


@run_glab_mr.command("view")
@pass_args
def run_glab_mr_view(passed_args: tuple[str, ...]):
    """Extends `glab mr view` with additional functions and defaults.

    Defaults to `--web`.
    """
    run(["gh", "mr", "view", "--web", *passed_args], on_error=OnError.ABORT)


@run_glab_mr.command("start")
@pass_args
@pass_plugin_app_context
@click.pass_context
def run_glab_mr_start(
    click_context: click.Context,
    app_context: AppContext[CorePluginConfig],
    passed_args: tuple[str, ...],
):
    """Like `glab mr create`, but with additional functionality.

    - Asks for a title if not provided.
    - Stashes any uncommitted changes.
    - Switches to `main` first and pulls the latest changes.
    - Creates a new branch using git/system username and the title.
    - Creates an empty commit to be able to create a PR.
    - Push the branch and the commit to remote.
    - Pops the stash.
    """
    _run_vcs_start(app_context, click_context, passed_args, "glab")


@click.group("vcs")
def run_vcs():
    """Alias for `gh`/`glab` with auto-detection.

    See the `gh` and `glab` commands for help.
    """
    assert_executable_installed("git", required_by="vcs")

    vcs_cli_tool = get_vcs_cli_tool()
    assert_executable_installed(vcs_cli_tool, required_by="vcs")


@run_vcs.group("mr")
def run_vcs_mr():
    """Alias for `gitlab mr` or `gh pr`, selecting the appropriate one based on the git remote."""


@run_vcs.group("pr")
def run_vcs_pr():
    """Alias for `gitlab mr` or `gh pr`, selecting the appropriate one based on the git remote."""


@run_vcs_pr.command("start")
@pass_args
@pass_plugin_app_context
@click.pass_context
def run_vcs_pr_start(
    click_context: click.Context,
    app_context: AppContext[CorePluginConfig],
    passed_args: tuple[str, ...],
):
    """Alias for `gh pr start`."""
    _run_vcs_start(app_context, click_context, passed_args)


@run_vcs_mr.command("start")
@pass_args
@pass_plugin_app_context
@click.pass_context
def run_vcs_mr_start(
    click_context: click.Context,
    app_context: AppContext[CorePluginConfig],
    passed_args: tuple[str, ...],
):
    """Alias for `glab mr start`."""
    _run_vcs_start(app_context, click_context, passed_args)


def _run_vcs_start(
    app_context: AppContext[CorePluginConfig],
    click_context: click.Context,
    passed_args: tuple[str, ...],
    vcs_cli_tool: Literal["gh", "glab"] | None = None,
):
    args = list(passed_args)
    title, args = consume_args_until_next_option(args)
    if not vcs_cli_tool:
        vcs_cli_tool = get_vcs_cli_tool()
    while not title:
        title = input(f"Enter a title for the {'PR' if vcs_cli_tool == 'gh' else 'MR'}: ")

    branch_name, create_branch = get_new_branch_name_or_switch_to_branch(app_context.plugin_config.branch_prefix, title)

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
    func = run_gh_pr_create if vcs_cli_tool == "gh" else run_glab_mr_create
    click_context.forward(func, passed_args=["--title", title, *args])
