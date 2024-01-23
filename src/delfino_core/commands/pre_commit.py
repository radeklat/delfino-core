from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import click
from click import Abort
from delfino.decorators import files_folders_option, pass_args
from delfino.execution import OnError, run
from delfino.terminal_output import print_header
from delfino.validation import assert_pip_package_installed

try:
    import yaml
except ImportError:
    pass


def _selected_stages_and_hook(passed_args: List[str]) -> Tuple[List[str], Optional[str]]:
    pre_commit_file = Path(".pre-commit-config.yaml")
    if not pre_commit_file.is_file():
        raise Abort(f"Pre-commit config file '{pre_commit_file}' not found.")

    pre_commit_config = yaml.safe_load(pre_commit_file.read_bytes())

    default_stages = pre_commit_config.get("default_stages", [])
    all_stages: Set[str] = set(default_stages)
    hooks_to_stages: Dict[str, List[str]] = {}

    for repo in pre_commit_config["repos"]:
        for hook in repo["hooks"]:
            all_stages.update(hook.get("stages", []))
            hooks_to_stages[hook.get("name", hook["id"])] = hook.get("stages", default_stages)

    if len(passed_args) >= 1:
        hook_name = passed_args[0]
        if stages := hooks_to_stages.get(hook_name):
            # User selected a single tool
            return [stages[0]], hook_name

    return sorted(all_stages), None


@click.command("pre-commit")
@pass_args
@files_folders_option
@click.option(
    "--add",
    "-a",
    "stage_all_files",
    is_flag=True,
    default=False,
    help="Stage all files before running pre-commit hooks.",
)
def run_pre_commit(stage_all_files: bool, files_folders: List[Path], passed_args: List[str]):
    """Run all pre-commit stages in the current project (alias for `pre-commit run ...`).

    To run a single hook, add the name of the hook at the end, as if you were running
    `pre-commit run <HOOK NAME>`.
    """
    assert_pip_package_installed("PyYAML")

    if stage_all_files:
        run(["git", "add", "."], on_error=OnError.PASS)

    files = ["--files", *files_folders] if files_folders else []

    stages, hook = _selected_stages_and_hook(passed_args)

    if hook is None:
        msg = "all pre-commit stages" if len(stages) > 1 else "pre-commit"
        print_header(f"Running {msg}")

    for stage in stages:
        if len(stages) > 1:
            print_header(f"{stage} / {hook}" if hook else stage, level=2)

        run(
            [
                "pre-commit",
                "run",
                "--hook-stage",
                stage,
                *([hook] if hook else []),
                *passed_args,
                *files,
            ],
            on_error=OnError.PASS,
        )
