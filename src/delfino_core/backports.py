from contextlib import suppress
from pathlib import Path


def path_is_relative_to(path1: Path, path2: Path) -> bool:
    """Backport of ``PurePath.is_relative_to`` for Python 3.7 and 3.8."""
    with suppress(ValueError):
        path1.relative_to(path2)
        return True
    return False
