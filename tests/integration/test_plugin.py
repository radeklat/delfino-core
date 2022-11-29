from types import ModuleType

import pytest
from delfino.click_utils.command import CommandRegistry
from delfino.models.pyproject_toml import PluginConfig

from commands.build_docker import build_docker
from commands.format import run_format
from commands.lint import lint, lint_pycodestyle, lint_pydocstyle, lint_pylint
from commands.switch_python_version import switch_python_version
from commands.test import coverage_open, coverage_report, test_all, test_integration, test_unit
from commands.typecheck import typecheck
from commands.upload_to_pypi import upload_to_pypi
from commands.verify_all import verify_all


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
            build_docker,
            run_format,
            lint_pydocstyle,
            lint_pycodestyle,
            lint_pylint,
            lint,
            switch_python_version,
            test_unit,
            test_integration,
            coverage_report,
            test_all,
            coverage_open,
            typecheck,
            upload_to_pypi,
            verify_all,
        ]
        command_registry = CommandRegistry(plugin_config, CommandRegistry._discover_command_packages(plugin_config))
        expected_command_names = {command.name for command in commands}
        assert {command.name for command in command_registry.visible_commands} == expected_command_names
