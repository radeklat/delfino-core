from types import ModuleType

import pytest
from delfino.click_utils.command import CommandRegistry
from delfino.models.pyproject_toml import PluginConfig

from delfino_core.commands.dependencies_update import dependencies_update
from delfino_core.commands.format import run_format
from delfino_core.commands.lint import lint, lint_pycodestyle, lint_pydocstyle, lint_pylint
from delfino_core.commands.pre_commit import pre_commit
from delfino_core.commands.switch_python_version import switch_python_version
from delfino_core.commands.test import coverage_open, coverage_report, test, test_all, test_integration, test_unit
from delfino_core.commands.typecheck import typecheck
from delfino_core.commands.verify_all import verify_all


@pytest.fixture(scope="session")
def plugin_config(poetry):
    return {poetry.name: PluginConfig.empty()}


@pytest.mark.usefixtures("build_and_install_plugin")
class TestPlugin:
    @staticmethod
    def should_be_discoverable_by_delfino(poetry, plugin_config):
        command_packages = CommandRegistry._discover_command_packages(plugin_config)
        assert len(command_packages) == 1
        plugin_names = {command_package.plugin_name for command_package in command_packages}
        assert poetry.name in plugin_names

        plugin_package = next(
            filter(lambda command_package: command_package.plugin_name == poetry.name, command_packages), None
        )
        assert plugin_package
        assert isinstance(plugin_package.package, ModuleType)
        assert isinstance(plugin_package.package.__package__, str)
        assert poetry.name.replace("-", "_") in plugin_package.package.__package__

    @staticmethod
    def should_be_visible_in_delfino(plugin_config):
        commands = [
            coverage_open,
            coverage_report,
            dependencies_update,
            lint,
            lint_pycodestyle,
            lint_pydocstyle,
            lint_pylint,
            pre_commit,
            run_format,
            switch_python_version,
            test,
            test_all,
            test_integration,
            test_unit,
            typecheck,
            verify_all,
        ]
        command_registry = CommandRegistry(plugin_config, CommandRegistry._discover_command_packages(plugin_config))
        expected_command_names = {command.name for command in commands}
        assert {command.name for command in command_registry.visible_commands} == expected_command_names
