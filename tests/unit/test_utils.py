import tempfile
from pathlib import Path

from delfino_core.config import CorePluginConfig
from delfino_core.utils import ensure_reports_dir


class TestEnsureReportsDir:
    @staticmethod
    def test_should_create_folder_if_missing():
        # GIVEN temporary folder is created
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_config = CorePluginConfig(reports_directory=tmpdir)

        # AND subsequently removed
        # WHEN this function is called
        ensure_reports_dir(plugin_config)

        # THEN the folder is created
        assert Path(tmpdir).is_dir()

    @staticmethod
    def test_should_ignore_exiting_folder_if_exists():
        # GIVEN temporary folder exists
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_config = CorePluginConfig(reports_directory=tmpdir)

            # WHEN this function is called
            # THEN it doesn't fail
            ensure_reports_dir(plugin_config)
