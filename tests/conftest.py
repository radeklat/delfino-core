import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import toml
from _pytest.fixtures import fixture
from click.testing import CliRunner
from delfino.constants import PYPROJECT_TOML_FILENAME
from delfino.models import AppContext, PluginConfig, PyprojectToml
from delfino.utils import get_package_manager


@fixture(scope="session")
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope="session")
def project_root():
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def pyproject_toml(project_root):
    return PyprojectToml(**toml.load(project_root / PYPROJECT_TOML_FILENAME))


@pytest.fixture(scope="session")
def poetry(pyproject_toml):
    assert pyproject_toml.tool.poetry
    return pyproject_toml.tool.poetry


@pytest.fixture()
def context_obj(project_root, pyproject_toml):
    return AppContext(
        project_root=project_root,
        pyproject_toml=pyproject_toml,
        package_manager=get_package_manager(project_root, pyproject_toml),
        plugin_config=PluginConfig.empty(),
    )


@pytest.fixture(scope="session")
def build_and_install_plugin(pyproject_toml, project_root):
    with tempfile.TemporaryDirectory() as tmpdir:
        sys.path.append(tmpdir)
        try:
            wheel_path = (
                project_root
                / "dist"
                / f"{pyproject_toml.project_name.replace('-', '_')}-{pyproject_toml.project_version}-py3-none-any.whl"
            )
            subprocess.run(f"cd {project_root} && uv build -q", shell=True, check=True)
            subprocess.run(f"pip install {wheel_path} -q --target {tmpdir}", shell=True, check=True)
            shutil.rmtree(project_root / "dist")
            yield
        finally:
            sys.path.remove(tmpdir)
