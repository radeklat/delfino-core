<h1 align="center" style="border-bottom: none;"> 🔌&nbsp;&nbsp;Delfino Core&nbsp;&nbsp; 🔌</h1>
<h3 align="center">A [Delfino](https://github.com/radeklat/delfino) plugin with core functionality.</h3>

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

## Configuration

Delfino doesn't load any plugins by default. To enable this plugin, add the following config into `pyproject.toml`:

```toml
[tool.delfino.plugins.delfino-core]

```

# Usage

Run `delfino --help`.
