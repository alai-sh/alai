# Changelog

All notable changes to alai are listed here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and alai
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- A project can keep alai's configuration in a `[tool.alai]` table in its
  `pyproject.toml` instead of an `alai.toml`. A `pyproject.toml` with that
  table marks the project root, and `alai add` and `alai remove` edit it.
  When both files are in one directory, alai reads `alai.toml` and warns that
  it ignores `[tool.alai]`.

## [0.1.0] - 2026-11-05

The first release.

[Unreleased]: https://github.com/alai-sh/alai/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/alai-sh/alai/releases/tag/v0.1.0
