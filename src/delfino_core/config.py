from pathlib import Path
from typing import List, Optional, Tuple

from delfino.decorators import pass_app_context
from delfino.models.pyproject_toml import PluginConfig
from pydantic import BaseModel, Field


class Dockerhub(BaseModel):
    build_for_platforms: List[str] = Field(["linux/amd64", "linux/arm64", "linux/arm/v7"], min_items=1)
    username: str


class Typecheck(BaseModel):
    strict_directories: List[Path] = []


class CorePluginConfig(PluginConfig):
    sources_directory: Path = Path("src")
    tests_directory: Path = Path("tests")
    pytest_modules: List[str] = Field(default_factory=list)
    reports_directory: Path = Path("reports")
    test_types: List[str] = ["unit", "integration"]
    verify_commands: Tuple[str, ...] = ("format", "lint", "typecheck", "test-all")
    lint_commands: Tuple[str, ...] = ("lint-pylint", "lint-pycodestyle", "lint-pydocstyle")
    disable_pre_commit: bool = False
    dockerhub: Optional[Dockerhub] = None
    typecheck: Typecheck = Field(default_factory=Typecheck)


pass_plugin_app_context = pass_app_context(plugin_config_type=CorePluginConfig)
