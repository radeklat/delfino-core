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

### [2.0.0] - 2022-11-30

### Breaking changes

- `typecheck` no longer accepts an arbitrary list of arguments interpreted as list of files to use. Use `-f`/`--file`/`--folder` instead. This option must be repeated for multiple files/folders.

### [1.2.2] - 2022-11-30

### Fixes

- Plugin entry point to the module with commands.

### [1.2.1] - 2022-11-29

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

[Unreleased]: https://github.com/radeklat/settings-doc/compare/2.0.0...HEAD
[2.0.0]: https://github.com/radeklat/settings-doc/compare/1.2.2...2.0.0
[1.2.2]: https://github.com/radeklat/settings-doc/compare/1.2.1...1.2.2
[1.2.1]: https://github.com/radeklat/settings-doc/compare/1.2.0...1.2.1
[1.2.0]: https://github.com/radeklat/settings-doc/compare/1.1.0...1.2.0
[1.1.0]: https://github.com/radeklat/settings-doc/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/radeklat/settings-doc/compare/initial...1.0.0
