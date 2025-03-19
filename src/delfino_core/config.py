import logging
import os
from pathlib import Path
from typing import Annotated, Optional

from delfino.decorators import pass_app_context
from delfino.models.pyproject_toml import PluginConfig
from pydantic import BaseModel, Field

_LOG = logging.getLogger(__name__)


class MypyConfig(BaseModel):
    strict_directories: list[Path] = []


class IssueTrackingConfig(BaseModel):
    _DEFAULT_API_KEY_ENV_VAR = "DELFINO_CORE_ISSUE_TRACKING_API_KEY"
    _DEFAULT_USERNAME_ENV_VAR = "DELFINO_CORE_ISSUE_TRACKING_USERNAME"

    issue_prefix: str = Field(
        "",
        description="Prefix for issue numbers, including a trailing hyphen if used. "
        "If not set, just the issue numbers will be used.",
    )
    tracker_url: str = Field(
        "",
        description="URL for the issue tracker. If not set, issue tracker integration will be disabled."
        "Implemented trackers: Jira.",
    )
    username_env_var: str = Field(
        _DEFAULT_USERNAME_ENV_VAR,
        description=f"Environment variable name for the issue tracking username. "
        f"If not set, '{_DEFAULT_USERNAME_ENV_VAR}' will be used by default.",
    )
    api_key_env_var: str = Field(
        _DEFAULT_API_KEY_ENV_VAR,
        description=f"Environment variable name for the issue tracking API key. "
        f"If not set, '{_DEFAULT_API_KEY_ENV_VAR}' will be used by default.",
    )

    @staticmethod
    def _get_env_var(name: str, purpose: str) -> Optional[str]:
        if (value := os.getenv(name)) is None:
            _LOG.warning(f"{purpose} environment variable '{name}' is not set.")

        return value

    @property
    def api_key(self) -> Optional[str]:
        return self._get_env_var(self.api_key_env_var, "Issue tracking API key")

    @property
    def username(self) -> Optional[str]:
        return self._get_env_var(self.username_env_var, "Issue tracking username")


class VCSConfig(BaseModel):
    branch_prefix: Optional[str] = Field(
        None, description="Prefix for branch names. If not set, git username will be used."
    )
    issue_tracking: Annotated[IssueTrackingConfig, Field(default_factory=IssueTrackingConfig)]


class CorePluginConfig(PluginConfig):
    sources_directory: Path = Path("src")
    tests_directory: Path = Path("tests")
    pytest_modules: list[str] = Field(default_factory=list)
    reports_directory: Path = Path("reports")
    test_types: list[str] = ["unit", "integration"]
    verify_commands: tuple[str, ...] = ("ensure-pre-commit", "ruff", "mypy", "test")
    test_commands: tuple[str, ...] = ("pytest", "coverage-report")
    disable_pre_commit: bool = False
    mypy: Annotated[MypyConfig, Field(default_factory=MypyConfig)]
    vcs: Annotated[VCSConfig, Field(default_factory=VCSConfig)]


pass_plugin_app_context = pass_app_context(plugin_config_type=CorePluginConfig)
