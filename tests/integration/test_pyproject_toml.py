from delfino.click_utils.command import CommandRegistry


class TestPyprojectTomlFile:
    """See https://python-poetry.org/docs/pyproject/#plugins."""

    @staticmethod
    def should_have_project_name_matching_repository_name(poetry, project_root):
        assert poetry.name == project_root.name

    @staticmethod
    def should_have_the_type_of_plugin_matching_a_value_expected_by_delfino(poetry):
        assert poetry.plugins
        assert CommandRegistry.TYPE_OF_PLUGIN in poetry.plugins

    @staticmethod
    def should_have_the_name_plugin_matching_the_name_of_the_project(poetry):
        assert poetry.plugins
        assert poetry.name in poetry.plugins[CommandRegistry.TYPE_OF_PLUGIN]

    @staticmethod
    def should_have_the_plugin_entry_point_matching_the_project_name(poetry):
        assert poetry.plugins
        entry_point: str = poetry.plugins[CommandRegistry.TYPE_OF_PLUGIN][poetry.name]
        assert poetry.name.replace("-", "_") == entry_point

    @staticmethod
    def should_have_the_plugin_entry_point_matching_pointed_to_existing_folder(poetry, project_root):
        assert poetry.plugins
        entry_point: str = poetry.plugins[CommandRegistry.TYPE_OF_PLUGIN][poetry.name]
        assert (project_root / "src" / entry_point.replace(".", "/")).exists()
