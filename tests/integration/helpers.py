import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


@contextmanager
def tmpdir_in_path(chdir: bool = False) -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as tmpdir:
        cwd = os.getcwd()
        tmpdir_path = Path(tmpdir)

        try:
            if chdir:
                os.chdir(tmpdir)
            sys.path.append(tmpdir)
            yield tmpdir_path
        finally:
            os.chdir(cwd)
            sys.path.remove(tmpdir)
