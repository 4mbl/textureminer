# Textureminer Changelog

All notable changes to this project will be documented in this file.

---

## Unreleased

### Added

* Add `--crop` flag that crops animated textures like magma and prismarine blocks to be same size as other blocks. This functionality was already present but now you can opt-out of it.
* Add `--partials` flag that creates textures for the following partial blocks: carpets, stairs, and slabs.
* Add `--replicate` flag that copies textures and renames them to match the block's name. Currently only used for glass panes.
* Create texture images for waxed copper variants. Currently you cannot turn this on, but a CLI flag might be added in the future.

### Changed

* Upgraded dependencies to latest versions.
* Each `Edition` instance now has its own temporary directory. This allows multiple `Edition` classes to be used simultaneously.
* Migrated to [ruff](https://github.com/astral-sh/ruff) for linting and formatting.

### Fixed

* Fixed inconsistent cleanup of temporary directories.
* Fixed duplicate logging messages.

### Removed

### Known Issues

## 2.0.2 | 2024-01-24

### Fixed

* Vulnerability in `"pillow` dependency.

## 2.0.1 | 2024-01-10

### Fixed

* Changelog heading for version 2.0.0 was incorrect.

## 2.0.0 | 2024-01-10

### Added

* Add `textureminer` to path when installing with `pip`.
* Change command-line parser to `argparse`. This allows more complex arguments and flags to be added.
* Add `--version` flag to print the current version of `textureminer`.
* Add `--help` flag to print the help message.
* Add `--java`|`-j` and `--bedrock`|`-b` flags to specify the edition of Minecraft to download textures for. Uses Java Edition if neither is specified.
* Add `--scale` flag to customize the scale factor.
* Add `--output` flag to customize the output directory.
* Add `--flatten` flag to flatten the output directory.

### Changed

* Make project naming more consistent.
* Major refactor into class-based structure.
* Changed base syntax to `textureminer [version] [flags]`. If version is omitted, the latest version of Minecraft will be used.
* Default value of `DO_MERGE`, now `False`, meaning that the textures will not be flattened to a single directory.
* Default value of `UPDATE` is now `all`, meaning that the most recent version of Minecraft will be used.
* Default value of `OUTPUT_DIR` is now `~/Downloads/textureminer/`.

### Fixed

* Missing punctuation.
* Python 3.12 compatibility.

### Removed

* Remove positional edition argument. Use `--java`|`-j` and `--bedrock`|`-b` flags instead or omit to use Java Edition.

### Known Issues

* Earliest Bedrock Edition version supported is v1.19.30. This is due to the fact that the `bedrock-samples` repository was not created until then.

---

## 1.1.2 | 2023-07-07

### Changed

* Clone only the required parts of the `bedrock-samples` repository when using Bedrock Edition

### Fixed

* Java Edition being selected even when Bedrock Edition was specified
* Capitalization of edition names

---

## 1.1.0 | 2023-07-07

### Changed

* Crop large textures to 16×16 pixels

---

## 1.0.0 | 2023.06.15

### Added

* Bedrock Edition support
* CLI argument support
* Nice title for CLI entry point

### Changed

* Lots of refactoring
* Improved documentation
* Made text output more consistent and informative

### Fixed

* Clear temporary directory after use
