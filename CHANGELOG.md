# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).
Types of changes are:

- **Breaking changes** for breaking changes.
- **Features** for new features or changes in existing functionality.
- **Fixes** for any bug fixes.
- **Deprecated** for soon-to-be removed features.

## [Unreleased]

## [10.0.0] - 2025-09-13

### Breaking changes

- Drop support for Python 3.9.
- Drop support for `delfino<5.0`.

## [9.0.0] - 2025-03-19

### Breaking changes

#### Drop support for Python 3.8

#### Removed several tools in favour of `ruff` and it's plugins

##### `pydocstyle`

[plugin configuration](https://docs.astral.sh/ruff/settings/#lintpydocstyle), [pydocstyle (D) rules](https://docs.astral.sh/ruff/rules/#pydocstyle-d)

```toml
[tool.ruff.lint.pydocstyle]
convention = "google"
```

##### `pycodestyle`

[plugin configuration](https://docs.astral.sh/ruff/settings/#lintpycodestyle), [pycodestyle (E, W) rules](https://docs.astral.sh/ruff/rules/#pycodestyle-e-w)

##### `pyupgrade`

[plugin configuration](https://docs.astral.sh/ruff/settings/#lintpyupgrade), [pyupgrade (UP) rules](https://docs.astral.sh/ruff/rules/#pyupgrade-up)

##### `isort`

[plugin configuration](https://docs.astral.sh/ruff/settings/#lintisort), [isort (I) rules](https://docs.astral.sh/ruff/rules/#isort-i)

Check which config options can be ported from `tool.isort` to `tool.ruff.lint.isort`.

Consider adopting the [auto-fix](https://docs.astral.sh/ruff/settings/#fix) option:

```toml
[tool.ruff]
fix = true
```

##### `black`

Replaced by `ruff format` ([configuration](https://docs.astral.sh/ruff/settings/#format)). Notably:

- The `line-length` option moves from `tool.black` to `tool.ruff`.

##### `pylint`

[plugin configuration](https://docs.astral.sh/ruff/settings/#lintpylint), [Pylint (PL) rules](https://docs.astral.sh/ruff/rules/#pylint-pl))

All `.pylintrc` files can be removed once any common configuration has been moved to `pyproject.toml` file under the `tool.ruff.lint` and `tool.ruff.lint.pylint` sections.

To mimic the presence of multiple `.pylintrc` files, use the [`per-file-ignores` option](https://docs.astral.sh/ruff/settings/#lint_per-file-ignores) in the `tool.ruff.lint` section, such as:

```toml
[tool.ruff.lint.per-file-ignores]
"tests/**" = [
    "D102",  # missing-documentation-for-public-method
]
```

If you don't want to use the ruff defaults, the following regexp will find all supported configuration options in the `.pylintrc` file that can be overridden:

```regexp
max-(args|bool-expr|branches|locals|nested-blocks|positional-args|public-methods|returns|statements)|allowed-(dunder-method-names|magic-value-types)
```

Additionally:

- `max_complexity` can be set in the `tool.ruff.lint.mccabe` section.

Consider turning on also checks provided by the following plugins as those overlap with some of the `pylint` checks that are no longer present under the pylint Ruff plugin:
- [`pyflakes` (F)](https://docs.astral.sh/ruff/rules/#pyflakes-f)
- [`mccabe` (C90)](https://docs.astral.sh/ruff/rules/#mccabe-c90)
  ```toml
  [tool.ruff.lint.mccabe]
  max-complexity = 7
  ```
- [`pep8-naming` (N)](https://docs.astral.sh/ruff/rules/#pep8-naming-n), with the following config:
  ```toml
  [tool.ruff.lint.pep8-naming]
  # Allow Pydantic's `@validator` decorator to trigger class method treatment.
  classmethod-decorators = ["classmethod", "pydantic.field_validator"]
  ```

The above-mentioned plugins are not enabled by default. You can turn them on by updating your `pyproject.toml` file:

```toml
[tool.ruff.lint]
select = [
    "C90", # mccabe
    "D",   # pydocstyle
    "E",   # pycodestyle, errors
    "F",   # Pyflakes
    "I",   # isort
    "N",   # PEP8-naming
    "PL",  # Pylint
    "UP",  # pyupgrade
    "W",   # pycodestyle, warning
]
ignore = [
   # Code of any previously disabled checks in the tool's configs
]
```

#### `ruff` command

- The `ruff` command runs both `ruff check` and `ruff format` in one go, as suggested by [the `ruff` documentation](https://docs.astral.sh/ruff/formatter/#sorting-imports). If extra arguments are provided after `--`, the `ruff` command will use them as the action to run instead of `check` and `format`.

#### Removed command groups

- `lint` - replaced by `ruff` of `ruff -- check`.
- `format` - replaced by `ruff` of `ruff -- format`.

The following configuration options can be removed:

```toml
[tool.delfino.plugins.delfino-core]
lint_commands = [...]
format_commands = [...]
``` 

If you used the `format` command in `pre-commit` hooks, you can replace `delfino format` with `delfino ruff` (`ruff check` is required to run `isort` and `ruff format` to run `black`).

### Features

- Add support for Python 3.13.

## [8.1.1] - 2024-09-23

### Fixes

- Don't lowercase branch prefix if coming from configuration or issue tracker.

## [8.1.0] - 2024-09-15

### Features

- Command `dependencies-update` will display link to a change log next to each dependency base on the [changelog_urls.yaml](src/delfino_core/changelog_urls.yaml) file distributed with the plugin.

## [8.0.0] - 2024-09-15

### Breaking changes

- Configuration option `tool.delfino.plugins.delfino-core.branch_prefix` has been moved to `tool.delfino.plugins.delfino-core.vcs.branch_prefix`.
- Configuration option `tool.delfino.plugins.delfino-core.typecheck` has been moved to `tool.delfino.plugins.delfino-core.mypy`.

### Features

#### Integration with Jira issue tracker

In the `vcs`/`gh`/`glab` `pr`/`mr` `start` commands, the integration attempts to fetch issue title. The resulting branch name will be set to `<ISSUE_PREFIX>-<ISSUE_NUMBER>/<ISSUE_TITLE>` and the first commit message will be set to `<ISSUE_TITLE>`. Use the issue number in place of the title to trigger it. For example `delfino mr start 123`.

##### New configuration options under `tool.delfino.plugins.delfino-core.issue_tracking`
- `issue_prefix` - The issue prefix (including a trailing dash).
- `tracker_url` - The issue tracker URL. If not set, the integration will be disabled.
- `username_env_var` - The environment variable containing the username for the issue tracker. Defaults to `DELFINO_CORE_ISSUE_TRACKING_USERNAME`.
- `api_key_env_var` - The environment variable containing the API key for the issue tracker. Defaults to `DELFINO_CORE_ISSUE_TRACKING_API_KEY`.

##### New optional install dependencies

- `vcs` - Installs `httpx` used for fetching issue title.

## [7.5.0] - 2024-08-02

### Features

- Improve branch name character sanitization in `vcs`/`gh`/`glab` commands. Now not only trailing special characters are removed but also leading ones and ones around slashes. Example: `!breaking: feature / branch.` becomes `breaking_feature/branch`.


## [7.4.6] - 2024-07-17

### Fixes

- Use `@me` instead of `me` as assignee when creating a Gitlab MR using `vcs`/`glab` `pr`/`mr` `create`/`start` commands.

## [7.4.5] - 2024-07-17

### Fixes

- Finish Merge requests on web when creating a Gitlab MR using `vcs`/`glab` `pr`/`mr` `create`/`start` commands.

## [7.4.4] - 2024-07-16

### Fixes

- Dependencies update.
- `ruff` in version `0.5.0` has removed support for `ruff <path>` syntax and requires `ruff check <path>` instead. The `ruff` command has been updated to reflect this change, however it will allow this to be overridden by supplying a different action as the extra argument after `--`.

## [7.4.3] - 2024-07-16

### Fixes

- Skip all prompts when creating a Gitlab MR using `vcs`/`glab` `pr`/`mr` `create`/`start` commands.

## [7.4.2] - 2024-06-21

### Fixes

- Fix trunk branch hardcoded to `main` in `vcs`/`gh`/`glab` `pr`/`mr` `start` command. 

## [7.4.1] - 2024-06-21

### Fixes

- Allow `/` in branch name for `vcs`/`gh`/`glab` commands.

## [7.4.0] - 2024-06-21

### Features

- New config option to allow specifying the branch name prefix for `vcs` commands. By default, it is set to the git username:
  ```toml
  [tool.delfino.plugins.delfino-core]
  branch_prefix = "your_prefix/"
  ```

## [7.3.0] - 2024-06-20

### Features

- New command `glab` that wraps the `glab` CLI tool. Similar to the existing `gh` command, it has the following subcommands:
  - `glab mr create`
  - `glab mr start`
  - `glab mr view`
- New command `vcs` that auto-selects the correct VCS CLI tool in the current directory based on git remote. Currently, `gh` and `glab` are supported. It has the following subcommands:
  - `vcs pr/mr create`
  - `vcs pr/mr start`
  - `vcs pr/mr view`

## [7.2.4] - 2024-01-23

### Fixes

- Do not require `PyYAML` when the `pre-commit` command is not used.

## [7.2.3] - 2024-01-23

### Fixes

- Missing `ruff` as an optional dependency in the `verify` group.

## [7.2.2] - 2023-10-31

### Fixes

- A crash in `dependencies-update` introduced by update of `delfino`.

## [7.2.1] - 2023-10-31

### Fixes

- `dependencies-update` strips final underscore from the branch name.

## [7.2.0] - 2023-10-24

### Features

- Replace heading and wait messages in output of the `verify` and `dependencies-update` commands with spinners.

## [7.1.0] - 2023-10-14

### Features

- New command `ruff`. It has been also added to the `lint` command group.
- New command `gh` with additional functionality on top of the `gh` CLI tool:
  - `gh pr create` adds sensible defaults for a single developer per branch to ask for almost no input. It also accepts a title of the PR as free text after the commands, as long as it doesn't start with a `-`.
  - `gh pr start` is a new command, which is like `gh pr create`, but also creates a new branch with a name matching the PR title, prefixed with current user's username. This branch is based off latest main and pushed to remote with an empty commit.
  - `gh pr view` default to opening the PR in a web browser.

### Fixes

- Asking questions in `dependencies-updates` now correctly defaults to "Yes" if no answer provided.

## [7.0.0] - 2023-10-14

This version renames several commands and command groups to be more consistent and predictable. The intention is to name commands using the same name as the underlying tool. Several commands were also turned into command groups of individual commands, to allow more flexibility in configuration.

### Breaking changes

#### Renamed commands

| Old name           | New name             |
|--------------------|----------------------|
| `lint-pylint`      | `pylint`             |
| `lint-pydocstyle`  | `pydocstyle`         |
| `lint-pycodestyle` | `pycodestyle`        |
| `typecheck`        | `mypy`               |
| `test`             | `pytest`             |
| `test-unit`        | `pytest-unit`        |
| `test-integration` | `pytest-integration` |

#### Renamed command groups

- The `verify-all` command group is now called `verify`, to match the existing `format` and `lint` command groups. However, the configration option to override the `verify` command group is still `tool.delfino.plugins.delfino-core.verify_commands` as it already matched the new name.

#### Renamed installation extras

Affects [optional dependencies](README.md#optional-dependencies) installed with `delfino-core`. Update your `pyproject.toml` file accordingly.

| Old name    | New name |
|-------------|----------|
| `typecheck` | `mypy`   |
| `verify_all`| `verify` |

#### Renamed group commands options

Affects list of commands visible in given command groups. Update `tool.delfino.plugins.delfino-core.<COMMAND_GROUP_NAME>_commans` in your `pyproject.toml` file accordingly.

| Old name              | New name          |
|-----------------------|-------------------|
| `typecheck`           | `mypy`            |
| `verify_all_commands` | `verify_commands` |

#### Renamed command functions

This is an implementation detail that should not be relied on, but it's listed here for completeness. Command and command group names were changed to match a pattern `run_<COMMAND_NAME>` and `run_group_<COMMAND_GROUP_NAME>`. This is to prevent clashes with the names of the underlying tools and easier discoverability.

| Old name                | New name                    |
|-------------------------|-----------------------------|
| `coverage_open`         | `run_coverage_open`         |
| `coverage_report`       | `run_coverage_report`       |
| `dependencies_update`   | `run_dependencies_update`   |
| `lint`                  | `run_group_lint`            |
| `lint_pycodestyle`      | `run_pycodestyle`           |
| `lint_pydocstyle`       | `run_pydocstyle`            |
| `lint_pylint`           | `run_pylint`                |
| `pre_commit`            | `run_pre_commit`            |
| `run_format`            | `run_group_format`          |
| `switch_python_version` | `run_switch_python_version` |
| `test`                  | `run_group_test`            |
| `test_all`              | `run_pytest`                |
| `test_integration`      | `run_pytest_integration`    |
| `test_unit`             | `run_pytest_unit`           |
| `typecheck`             | `run_mypy`                  |
| `verify_all`            | `run_group_verify`          |

### Features

- Help text for all command groups is now generated, preventing typos and stale information about commands.

#### New commands

- `ensure-pre-commit`
- `pyupgrade`
- `isort`
- `black`

#### New command groups

- The `format` command has been turned into a command group of individual.
  - Contains the following commands: `ensure-pre-commit`, `pyupgrade`, `isort` and `black`.
  - Can be overriden with `tool.delfino.plugins.delfino-core.format_commands` option in the `pyproject.toml` file.
- `test` has been formally changed to a command group (functionally, it was already a group).
  - Contains the following commands: `pytest` and `coverage-report`.
  - Can be overriden with `tool.delfino.plugins.delfino-core.test_commands` option in the `pyproject.toml` file.

## [6.1.0] - 2023-10-13

### Features

- New `pre-commit` command to run all stages of pre-commit or a single hook with the correct stage.

## [6.0.0] - 2023-10-12

### Breaking changes

- Upgrade to `delfino` version `3.x`, which requires `pydantic>=2.0`.

## [5.2.2] - 2023-10-12

### Fixes

- `pyupgrade` incorrectly handling minor version number in `tool.poetry.dependencies.python` of `pyproject.toml` file.
- dependencies update.

## [5.2.1] - 2023-09-15

### Fixes

- Dependencies update
- Don't ask to `git push` if nothing was committed during `dependencies-update`.

## [5.2.0] - 2023-07-03

### Features

- Add `--stash` (default) / `--no-stash` option to `dependencies-update` command to control whether to stash changes before updating dependencies.

## [5.1.1] - 2023-06-25

### Fixes

- Updates deprecated `local_commands_directory` from `delfino`.
- Add walrus operator supported since Python 3.8.

## [5.1.0] - 2023-06-25

### Features

- Adds `pyupgrade` into the `format` command

## [5.0.0] - 2023-06-25

### Breaking changes

- Drops Python 3.7 support.

## [4.0.1] - 2022-12-29

### Features

- Removed optional dependencies `twine` and `packaging`.

## [4.0.0] - 2022-12-29

### Breaking changes

- Removed the `upload-to-pypi` command. No longer needed with Poetry and Packagecloud uses a different upload mechanism.
- Moved the `build-docker` command into a new plugin [`delfino-docker`](https://github.com/radeklat/delfino-docker) as `docker-build`.

#### Migration guide

Have a look in the `pyproject.toml` file. If `upload-to-pypi` or `build-docker` are listed under `tool.delfino.plugins.delfino-core.disable_plugins`, remove them. You don't need to do anything else.

If `tool.delfino.plugins.delfino-core.dockerhub` exists in the `pyproject.toml`:
  - Install `delfino-docker`.
  - In `pyproject.toml`, create a key `tool.delfino.plugins.delfino-docker.docker_build`.
  - Move `tool.delfino.plugins.delfino-core.dockerhub` under this new key.
  - Rename `username` to `dockerhub_username`.

### Features

- Removed `upload_to_pypi` and `build_docker` extra dependency groups. Missing groups will be simply ignored during installation, so this is not a breaking change.
- Removed optional dependencies on `twine` and `packaging` in the `all` group.

## [3.10.0] - 2022-12-29

### Features

- `dependencies-update` command:
  - Logs git operations when the automatically created branch doesn't exist.
  - Opens pull request link in a browser if chosen by the user.

### Fixes

- Dependencies update

## [3.9.0] - 2022-12-16

### Features

- `dependencies-update` no longer prints out executed commands since `delfino>=0.29.0` logs all executed commands in debug level. Use `--log-level debug` to see them.

### Fixes

- Config options incorrectly passed to all commands in a group instead of only those they belonged to.

## [3.8.1] - 2022-12-16

### Fixes

- Dependencies update.

## [3.8.0] - 2022-12-16

### Features

- `format` command takes a list of one or more files/folders to use with the `-f`/`--file`/`--folder` option.

## [3.7.1] - 2022-12-15

### Fixes

- Check if `git-python` is installed after it's use is attempted.

## [3.7.0] - 2022-12-15

### Features

- Add support for `poetry` in the `dependencies-update` command.

### Fixes

- Point to correct file to edit in `dependencies-update` for `pipenv`.

## [3.6.0] - 2022-12-15

### Features

- Commands executed via `utils.execute_commands_group` will receive passed arguments as `passed_args` from config, if they use the `delfino.decorators.pass_args` decorator. Example:
  ```toml
  [tool.delfino.plugins.delfino-core.lint-pylint]
  pass_args = "--fail-under 0.9"
  ```
  will pass `--fail-under 0.9` to `pylint` executed by `lint-pylint`, which is in `lint` group, which itself is in `verify-all` group.

## [3.5.0] - 2022-12-14

### Features

- `utils.execute_commands_group` logs a debug message when a command is not executed because it is disabled.

## [3.4.1] - 2022-12-13

### Fixes

- Wrapping `pytest` with extra modules via the `tool.delfino.plugins.delfino-core.pytest_modules` config.

## [3.4.0] - 2022-12-13

### Features

- Allow wrapping `pytest` with extra modules via `tool.delfino.plugins.delfino-core.pytest_modules` config. Each value in this list will prepend `pytest` with `-m <MODULE NAME>`.

### Fixes

- Warn about using commands in a group that don't exist instead of skipping them silently.

## [3.3.0] - 2022-12-12

### Features

- Commands in the `lint` command group can be overriden with `tool.delfino.plugins.delfino-core.lint_commands` option in the `pyproject.toml` file.

## [3.2.1] - 2022-12-09

### Fixes

- Add missing setting of `PYTHONPATH` environment variable in tests.

## [3.2.0] - 2022-12-09

### Features

- New command `test`, which is the same as `test-all` but without coverage.

## [3.1.0] - 2022-12-09

### Features

- `typecheck` will print additional headings if any folders are in a strict mode.

## [3.0.1] - 2022-12-09

### Fixes

- Dependencies update

## [3.0.0] - 2022-12-08

### Breaking changes

- `test-unit` and `test-integration` no longer support the `--maxfail` and `--debug` flags. Use the passthrough option (any argument after `--`) to pass these flags to pytest directly with `--maxfail` and `-s` respectively.

### Features

- `test-all` command takes a list of one or more files/folders to use with the `-f`/`--file`/`--folder` option.

### Fixes

- Fix type annotations for `passed_args`.

## [2.3.0] - 2022-12-07

### Features

- `lint`, `lint-pylint`, `lint-pydocstyle` and `lint-pycodestyle` commands takes a list of one or more files/folders to use with the `-f`/`--file`/`--folder` option.

## [2.2.0] - 2022-12-07

### Features

- The following commands now take arbitrary arguments after `--`, which are then passed to the underlying tool:
  - `lint-pycodestyle`
  - `lint-pydocstyle`
  - `lint-pylint`
  - `test-integration`
  - `test-unit`
  - `typecheck`

## [2.1.1] - 2022-12-05

### Fixes

- Add missing optional dependencies.

## [2.1.0] - 2022-12-05

### Features

- New command `dependencies-update` and optional dependency group `dependencies_update`.

## [2.0.1] - 2022-12-04

### Fixes

- Workaround for `build-docker` of `cargo` on ARMv7 in emulator.

## [2.0.0] - 2022-11-30

### Breaking changes

- `typecheck` no longer accepts an arbitrary list of arguments interpreted as list of files to use. Use `-f`/`--file`/`--folder` instead. This option must be repeated for multiple files/folders.

## [1.2.2] - 2022-11-30

### Fixes

- Plugin entry point to the module with commands.

## [1.2.1] - 2022-11-29

### Fixes

- Relax version dependency on `delfino` to allow faster initial development.

## [1.2.0] - 2022-11-29

### Features

- Moved in optional dependencies from `delfino`.

## [1.1.0] - 2022-11-29

### Features

- Moved in core commands from `delfino`.

## [1.0.0] - 2022-11-26

### Features

- Initial source code

[Unreleased]: https://github.com/radeklat/delfino-core/compare/10.0.0...HEAD
[10.0.0]: https://github.com/radeklat/delfino-core/compare/9.0.0...10.0.0
[9.0.0]: https://github.com/radeklat/delfino-core/compare/8.1.1...9.0.0
[8.1.1]: https://github.com/radeklat/delfino-core/compare/8.1.0...8.1.1
[8.1.0]: https://github.com/radeklat/delfino-core/compare/8.0.0...8.1.0
[8.0.0]: https://github.com/radeklat/delfino-core/compare/7.5.0...8.0.0
[7.5.0]: https://github.com/radeklat/delfino-core/compare/7.4.6...7.5.0
[7.4.6]: https://github.com/radeklat/delfino-core/compare/7.4.5...7.4.6
[7.4.5]: https://github.com/radeklat/delfino-core/compare/7.4.4...7.4.5
[7.4.4]: https://github.com/radeklat/delfino-core/compare/7.4.3...7.4.4
[7.4.3]: https://github.com/radeklat/delfino-core/compare/7.4.2...7.4.3
[7.4.2]: https://github.com/radeklat/delfino-core/compare/7.4.1...7.4.2
[7.4.1]: https://github.com/radeklat/delfino-core/compare/7.4.0...7.4.1
[7.4.0]: https://github.com/radeklat/delfino-core/compare/7.3.0...7.4.0
[7.3.0]: https://github.com/radeklat/delfino-core/compare/7.2.4...7.3.0
[7.2.4]: https://github.com/radeklat/delfino-core/compare/7.2.3...7.2.4
[7.2.3]: https://github.com/radeklat/delfino-core/compare/7.2.2...7.2.3
[7.2.2]: https://github.com/radeklat/delfino-core/compare/7.2.1...7.2.2
[7.2.1]: https://github.com/radeklat/delfino-core/compare/7.2.0...7.2.1
[7.2.0]: https://github.com/radeklat/delfino-core/compare/7.1.0...7.2.0
[7.1.0]: https://github.com/radeklat/delfino-core/compare/7.0.0...7.1.0
[7.0.0]: https://github.com/radeklat/delfino-core/compare/6.0.0...7.0.0
[6.1.0]: https://github.com/radeklat/delfino-core/compare/6.0.0...6.1.0
[6.0.0]: https://github.com/radeklat/delfino-core/compare/5.2.2...6.0.0
[5.2.2]: https://github.com/radeklat/delfino-core/compare/5.2.1...5.2.2
[5.2.1]: https://github.com/radeklat/delfino-core/compare/5.2.0...5.2.1
[5.2.0]: https://github.com/radeklat/delfino-core/compare/5.1.1...5.2.0
[5.1.1]: https://github.com/radeklat/delfino-core/compare/5.1.0...5.1.1
[5.0.0]: https://github.com/radeklat/delfino-core/compare/4.0.1...5.0.0
[4.0.1]: https://github.com/radeklat/delfino-core/compare/4.0.0...4.0.1
[4.0.0]: https://github.com/radeklat/delfino-core/compare/3.10.0...4.0.0
[3.10.0]: https://github.com/radeklat/delfino-core/compare/3.9.0...3.10.0
[3.9.0]: https://github.com/radeklat/delfino-core/compare/3.8.1...3.9.0
[3.8.1]: https://github.com/radeklat/delfino-core/compare/3.8.0...3.8.1
[3.8.0]: https://github.com/radeklat/delfino-core/compare/3.7.1...3.8.0
[3.7.1]: https://github.com/radeklat/delfino-core/compare/3.7.0...3.7.1
[3.7.0]: https://github.com/radeklat/delfino-core/compare/3.6.0...3.7.0
[3.6.0]: https://github.com/radeklat/delfino-core/compare/3.5.0...3.6.0
[3.5.0]: https://github.com/radeklat/delfino-core/compare/3.4.1...3.5.0
[3.4.1]: https://github.com/radeklat/delfino-core/compare/3.4.0...3.4.1
[3.4.0]: https://github.com/radeklat/delfino-core/compare/3.3.0...3.4.0
[3.3.0]: https://github.com/radeklat/delfino-core/compare/3.2.2...3.3.0
[3.2.1]: https://github.com/radeklat/delfino-core/compare/3.2.1...3.2.1
[3.2.0]: https://github.com/radeklat/delfino-core/compare/3.1.0...3.2.0
[3.1.0]: https://github.com/radeklat/delfino-core/compare/3.0.1...3.1.0
[3.0.1]: https://github.com/radeklat/delfino-core/compare/3.0.0...3.0.1
[3.0.0]: https://github.com/radeklat/delfino-core/compare/2.3.0...3.0.0
[2.3.0]: https://github.com/radeklat/delfino-core/compare/2.2.0...2.3.0
[2.2.0]: https://github.com/radeklat/delfino-core/compare/2.1.1...2.2.0
[2.1.1]: https://github.com/radeklat/delfino-core/compare/2.1.0...2.1.1
[2.1.0]: https://github.com/radeklat/delfino-core/compare/2.0.1...2.1.0
[2.0.1]: https://github.com/radeklat/delfino-core/compare/2.0.0...2.0.1
[2.0.0]: https://github.com/radeklat/delfino-core/compare/1.2.2...2.0.0
[1.2.2]: https://github.com/radeklat/delfino-core/compare/1.2.1...1.2.2
[1.2.1]: https://github.com/radeklat/delfino-core/compare/1.2.0...1.2.1
[1.2.0]: https://github.com/radeklat/delfino-core/compare/1.1.0...1.2.0
[1.1.0]: https://github.com/radeklat/delfino-core/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/radeklat/delfino-core/compare/initial...1.0.0
