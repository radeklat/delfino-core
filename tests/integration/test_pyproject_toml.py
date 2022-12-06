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
        assert poetry.name.replace("-", "_") == entry_point.split(".")[0]

    @staticmethod
    def should_have_the_plugin_entry_point_matching_pointed_to_existing_folder(poetry, project_root):
        assert poetry.plugins
        entry_point: str = poetry.plugins[CommandRegistry.TYPE_OF_PLUGIN][poetry.name]
        assert (project_root / "src" / entry_point.replace(".", "/")).exists()

    @staticmethod
    def should_have_all_extras_listed_in_dependencies(poetry):
        matching_dependencies = {
            dep
            for dep, dep_attrs in poetry.dependencies.items()
            if isinstance(dep_attrs, dict) and dep_attrs["optional"]
        }

        for extra_key, extras in poetry.extras.items():
            missing_dependencies = set(extras) - matching_dependencies
            assert not missing_dependencies, (
                f"Extra '{extra_key}' contains dependencies not listed in 'tool.poetry.dependencies': "
                f"{', '.join(sorted(missing_dependencies))}"
            )

    @staticmethod
    def should_have_the_all_extras_covering_all_the_other_extras(poetry):
        all_extras = set()
        other_extras = set()

        for extra_key, extras in poetry.extras.items():
            if extra_key == "all":
                all_extras = set(extras)
            else:
                other_extras.update(extras)

        missing_dependencies = other_extras - all_extras
        assert not missing_dependencies, (
            f"Some extra dependencies not listed in 'tool.poetry.extras.all': "
            f"{', '.join(sorted(missing_dependencies))}"
        )
