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

[Unreleased]: https://github.com/radeklat/delfino-core/compare/6.1.0...HEAD
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
