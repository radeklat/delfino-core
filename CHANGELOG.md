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

[Unreleased]: https://github.com/radeklat/delfino-core/compare/3.2.1...HEAD
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
