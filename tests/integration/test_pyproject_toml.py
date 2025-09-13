from typing import Any

import pytest
from delfino.click_utils.command import CommandRegistry


@pytest.fixture(scope="module")
def entry_points(pyproject_toml) -> dict[str, Any]:
    return pyproject_toml.project.model_extra.get("entry-points", {})


class TestPyprojectTomlFile:
    """See https://python-poetry.org/docs/pyproject/#plugins."""

    @staticmethod
    def test_should_have_project_name_matching_repository_name(pyproject_toml, project_root):
        assert pyproject_toml.project.name == project_root.name

    @staticmethod
    def test_should_have_the_type_of_plugin_matching_a_value_expected_by_delfino(entry_points):
        assert entry_points
        assert CommandRegistry.TYPE_OF_PLUGIN in entry_points

    @staticmethod
    def test_should_have_the_name_plugin_matching_the_name_of_the_project(entry_points, pyproject_toml):
        assert entry_points
        assert pyproject_toml.project.name in entry_points[CommandRegistry.TYPE_OF_PLUGIN]

    @staticmethod
    def test_should_have_the_plugin_entry_point_matching_the_project_name(entry_points, pyproject_toml):
        assert entry_points
        entry_point: str = entry_points[CommandRegistry.TYPE_OF_PLUGIN][pyproject_toml.project.name]
        assert pyproject_toml.project.name.replace("-", "_") == entry_point.split(".")[0]

    @staticmethod
    def test_should_have_the_plugin_entry_point_matching_pointed_to_existing_folder(
        entry_points, pyproject_toml, project_root
    ):
        assert entry_points
        entry_point: str = entry_points[CommandRegistry.TYPE_OF_PLUGIN][pyproject_toml.project.name]
        assert (project_root / "src" / entry_point.replace(".", "/")).exists()

    @staticmethod
    def test_should_have_the_all_extras_covering_all_the_other_extras(pyproject_toml):
        all_extras = set()
        other_extras = set()

        for extra_key, extras in pyproject_toml.project.model_extra["optional-dependencies"].items():
            if extra_key == "all":
                all_extras = set(extras)
            else:
                other_extras.update(extras)

        missing_dependencies = other_extras - all_extras
        assert not missing_dependencies, (
            f"Some extra dependencies not listed in "
            f"'project.optional-dependencies.all': {', '.join(sorted(missing_dependencies))}"
        )
