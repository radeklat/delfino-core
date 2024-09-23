from __future__ import annotations

import logging
import re
from functools import lru_cache
from subprocess import PIPE
from typing import Literal

from delfino import run
from delfino.execution import OnError
from delfino.validation import assert_pip_package_installed

from delfino_core.commands.issue_tracker import JiraClient
from delfino_core.config import VCSConfig
from delfino_core.utils import ask, assert_executable_installed


@lru_cache(maxsize=1)
def get_trunk_branch():
    """To dynamically figure out if it's `main`, `master` or something else."""
    ref = run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], stdout=PIPE, on_error=OnError.PASS)

    # The ref is expected to be like 'refs/remotes/origin/main'
    return ref.stdout.decode().strip().split("/")[-1]


_LOGGER = logging.getLogger(__name__)
_INVALID_BRANCH_NAME_CHARS = re.compile(r"[^a-zA-Z0-9_/-]+")


def consume_args_until_next_option(passed_args: list[str]) -> tuple[str, list[str]]:
    for index, arg in enumerate(passed_args):
        if arg.startswith("-"):
            return " ".join(passed_args[:index]), passed_args[index:]
    return " ".join(passed_args), []


def _sanitize_branch_name(branch_name: str) -> str:
    return "/".join(_INVALID_BRANCH_NAME_CHARS.sub("_", part).strip("_") for part in branch_name.split("/"))


def _get_user_name() -> str:
    # Get the current username from git config
    username = run(["git", "config", "user.email"], stdout=PIPE, on_error=OnError.ABORT).stdout.decode().strip()

    if not username:  # If not available, use the system username
        _LOGGER.warning("No git user.email found, using system username.")
        assert_executable_installed("whoami", required_by="gh")
        username = run(["whoami"], stdout=PIPE, on_error=OnError.ABORT).stdout.decode().strip()
    elif "@" in username:  # Strip the domain from the email address
        username = username.split("@")[0]

    return username


def get_new_branch_name_or_switch_to_branch(branch_prefix: str | None, title: str) -> tuple[str, bool]:
    if branch_prefix is None:
        branch_prefix = _get_user_name()

    if branch_prefix != "":  # allow for no prefix
        branch_prefix = _sanitize_branch_name(branch_prefix) + "/"

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


@lru_cache(maxsize=1)
def get_vcs_cli_tool() -> Literal["gh", "glab"]:
    """Determine if `gh` or `glab` should be used."""
    remote_url = run(["git", "remote", "-v"], stdout=PIPE, on_error=OnError.PASS).stdout.decode()

    if "github" in remote_url:
        return "gh"

    if "gitlab" in remote_url:
        return "glab"

    raise RuntimeError("No supported VCS found in the git remote.")


def title_and_branch_prefix_from_issue_tracker(
    vcs_cli_tool: str, title: str, command_config: VCSConfig
) -> tuple[str, str | None]:
    branch_prefix = command_config.branch_prefix
    prompt_part = ""

    if command_config.issue_tracking.tracker_url:
        assert_pip_package_installed("httpx")
        prompt_part = " or issue number"

    while not title:
        title = input(f"Enter a title{prompt_part} for the {'PR' if vcs_cli_tool == 'gh' else 'MR'}: ").strip()

    if not command_config.issue_tracking.tracker_url:
        return title.lower(), branch_prefix

    issue_number = None
    try:
        issue_number = int(title)
    except ValueError:
        pass

    if issue_number is not None:
        issue_title = JiraClient(command_config.issue_tracking).get_issue_title(issue_number).lower()
        title = f"{command_config.issue_tracking.issue_prefix}{issue_number}/{issue_title}"
        branch_prefix = ""  # allow completely custom branch name

    return title, branch_prefix
