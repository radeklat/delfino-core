from pathlib import Path
from typing import List, Tuple

from delfino.decorators import pass_app_context
from delfino.models.pyproject_toml import PluginConfig
from pydantic import BaseModel, Field


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
    typecheck: Typecheck = Field(default_factory=Typecheck)


pass_plugin_app_context = pass_app_context(plugin_config_type=CorePluginConfig)
