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
    <img alt="Maintenance" src="https://img.shields.io/maintenance/yes/2024">
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

# Commands
  
| Command               | Description                                                            |
|-----------------------|------------------------------------------------------------------------|
| black                 | Runs black.                                                            |
| coverage-open         | Open coverage results in default browser.                              |
| coverage-report       | Analyse coverage and generate a term/HTML report.                      |
| dependencies-update   | Manages the process of updating dependencies.                          |
| ensure-pre-commit     | Ensures pre-commit is installed and enabled.                           |
| format                | Runs ensure-pre-commit, pyupgrade, isort, black.                       |
| gh                    | Extends `gh` or passes through.                                        |
| glab                  | Extends `glab` or passes through.                                      |
| isort                 | Runs isort.                                                            |
| lint                  | Runs ruff, pylint, pycodestyle, pydocstyle.                            |
| mypy                  | Run type checking on source code.                                      |
| pre-commit            | Run all pre-commit stages in the current project...                    |
| pycodestyle           | Run PEP8 checking on code.                                             |
| pydocstyle            | Run docstring linting on source code.                                  |
| pylint                | Run pylint on code.                                                    |
| pytest                | Runs pytest for individual test suites.                                |
| pytest-integration    | Run integration tests.                                                 |
| pytest-unit           | Run unit tests.                                                        |
| pyupgrade             | Runs pyupgrade with automatic version discovery.                       |
| ruff                  | Run ruff.                                                              |
| switch-python-version | Switches Python venv to a different Python version.                    |
| test                  | Runs pytest, coverage-report.                                          |
| vcs                   | Alias for `gh`/`glab` with auto-detection.                             |
| verify                | Runs format, lint, mypy, test.                                         |

# Installation

- pip: `pip install delfino-core`
- Poetry: `poetry add -D delfino-core`
- Pipenv: `pipenv install -d delfino-core`

## Optional dependencies

Each project may use different sub-set of [commands](#commands). Therefore, dependencies of all commands are optional and checked only when the command is executed.

Using `[all]` installs all the [optional dependencies](https://setuptools.pypa.io/en/latest/userguide/dependency_management.html#optional-dependencies) used by all the commands. If you want only a sub-set of those dependencies, there are finer-grained groups available:

- For individual commands (matches the command names):
  - `mypy`
  - `format`
  - `dependencies-update`
  - `pre-commit`
- For groups of commands:
  - `test` - for testing and coverage commands
  - `lint` - for all the linting commands
- For groups of groups:
  - `verify` - same as `[mypy,format,test,lint]`
  - `all` - all optional packages

# Configuration

Delfino doesn't load any plugins by default. To enable this plugin, add the following config into `pyproject.toml`:

```toml
[tool.delfino.plugins.delfino-core]

```

## Plugin configuration

This plugin has several options. All the values are optional and defaults are shown below: 

```toml
[tool.delfino.plugins.delfino-core]
# Source files - may have different rules than tests (usually stricter)
sources_directory = "src"

# Test files
tests_directory = "tests"

# Where to store reports generated by various tools
reports_directory = "reports"

# Types of tests you have nested under the `tests_directory`. Will be executed in given order.
test_types = ["unit", "integration"]

# One or more module to wrap `pytest` in, executing it as `python -m <MODULE> pytest ...`
pytest_modules = []

# Coommand groups and commands to run as a quality gate in given order.
verify_commands = ["format", "lint", "mypy", "test"]
format_commands = ["ensure-pre-commit", "pyupgrade", "isort", "black"]
lint_commands = ["ruff", "pylint", "pycodestyle", "pydocstyle"]
test_commands = ["pytest", "coverage-report"]

# Do not install pre-commit if this is set to true.
disable_pre_commit = false

# Enable to manually specify the branch prefix. By default it is set to git username.
# branch_prefix = ""
```

## Commands configuration

Several commands have their own configuration as well:

```toml
[tool.delfino.plugins.delfino-core.mypy]
# One or more directories where type hint will be required. By default they are optional.
strict_directories = []  
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
