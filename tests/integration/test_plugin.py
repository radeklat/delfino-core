from types import ModuleType

import pytest
from delfino.click_utils.command import CommandRegistry
from delfino.models.pyproject_toml import PluginConfig

from delfino_core.commands.dependencies_update import run_dependencies_update
from delfino_core.commands.pre_commit import run_ensure_pre_commit, run_pre_commit
from delfino_core.commands.ruff import run_ruff
from delfino_core.commands.switch_python_version import run_switch_python_version
from delfino_core.commands.test import (
    run_coverage_open,
    run_coverage_report,
    run_group_test,
    run_pytest,
    run_pytest_integration,
    run_pytest_unit,
)
from delfino_core.commands.typecheck import run_mypy
from delfino_core.commands.vcs import run_gh, run_glab, run_vcs
from delfino_core.commands.verify import run_group_verify


@pytest.fixture(scope="session")
def plugin_config(pyproject_toml):
    return {pyproject_toml.project_name: PluginConfig.empty()}


@pytest.mark.usefixtures("build_and_install_plugin")
class TestPlugin:
    @staticmethod
    def test_should_be_discoverable_by_delfino(pyproject_toml, plugin_config):
        command_packages = CommandRegistry._discover_command_packages(plugin_config)
        assert len(command_packages) == 1
        plugin_names = {command_package.plugin_name for command_package in command_packages}
        assert pyproject_toml.project_name in plugin_names

        plugin_package = next(
            filter(
                lambda command_package: command_package.plugin_name == pyproject_toml.project_name, command_packages
            ),
            None,
        )
        assert plugin_package
        assert isinstance(plugin_package.package, ModuleType)
        assert isinstance(plugin_package.package.__package__, str)
        assert pyproject_toml.project_name.replace("-", "_") in plugin_package.package.__package__

    @staticmethod
    def test_should_be_visible_in_delfino(plugin_config):
        commands = [
            run_coverage_open,
            run_coverage_report,
            run_dependencies_update,
            run_ensure_pre_commit,
            run_mypy,
            run_pre_commit,
            run_switch_python_version,
            run_pytest,
            run_group_test,
            run_pytest_integration,
            run_pytest_unit,
            run_ruff,
            run_group_verify,
            run_gh,
            run_glab,
            run_vcs,
        ]
        command_registry = CommandRegistry(plugin_config, CommandRegistry._discover_command_packages(plugin_config))
        expected_command_names = {command.name for command in commands}
        assert {command.name for command in command_registry.visible_commands} == expected_command_names
