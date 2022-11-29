from delfino_core.config import CorePluginConfig


def ensure_reports_dir(config: CorePluginConfig) -> None:
    """Ensures that the reports directory exists."""
    config.reports_directory.mkdir(parents=True, exist_ok=True)
