<h1 align="center" style="border-bottom: none;"> 🔌&nbsp;&nbsp;Delfino Core&nbsp;&nbsp; 🔌</h1>
<h3 align="center">A <a href="https://github.com/radeklat/delfino">Delfino</a> plugin with core functionality.</h3>

<p align="center">
    <a href="https://app.circleci.com/pipelines/github/radeklat/delfino-core?branch=main">
        <img alt="CircleCI" src="https://img.shields.io/circleci/build/github/radeklat/delfino-core">
    </a>
    <a href="https://app.codecov.io/gh/radeklat/delfino-core/">
        <img alt="Codecov" src="https://img.shields.io/codecov/c/github/radeklat/delfino-core">
    </a>
    <a href="https://github.com/radeklat/delfino-core/tags">
        <img alt="GitHub tag (latest SemVer)" src="https://img.shields.io/github/tag/radeklat/delfino-core">
    </a>
    <img alt="Maintenance" src="https://img.shields.io/maintenance/yes/2022">
    <a href="https://github.com/radeklat/delfino-core/commits/main">
        <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/radeklat/delfino-core">
    </a>
    <a href="https://www.python.org/doc/versions/">
        <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/delfino-core">
    </a>
    <a href="https://pypistats.org/packages/delfino-core">
        <img alt="Downloads" src="https://img.shields.io/pypi/dm/delfino-core">
    </a>
</p>

# Installation

- pip: `pip install delfino-core`
- Poetry: `poetry add -D delfino-core`
- Pipenv: `pipenv install -d delfino-core`

## Optional dependencies

Each project may use different sub-set of commands. Therefore, dependencies of all commands are optional and checked only when the command is executed.

Using `[all]` installs all the [optional dependencies](https://setuptools.pypa.io/en/latest/userguide/dependency_management.html#optional-dependencies) used by all the commands. If you want only a sub-set of those dependencies, there are finer-grained groups available:

- For individual commands (matches the command names):
  - `upload_to_pypi`
  - `build_docker`
  - `typecheck`
  - `format`
- For groups of commands:
  - `test` - for testing and coverage commands
  - `lint` - for all the linting commands
- For groups of groups:
  - `verify_all` - same as `[typecheck,format,test,lint]`
  - `all` - all optional packages

## Configuration

Delfino doesn't load any plugins by default. To enable this plugin, add the following config into `pyproject.toml`:

```toml
[tool.delfino.plugins.delfino-core]

```

# Usage

Run `delfino --help`.

# Development

To develop against editable `delfino` sources:

1. Make sure `delfino` sources are next to this plugin:
    ```shell
    cd ..
    git clone https://github.com/radeklat/delfino.git
    ```
2. Install `delfino` as editable package:
    ```shell
    pip install -e ../delfino
    ```
   Note that poetry will reset this to the released package when you install/update anything.
