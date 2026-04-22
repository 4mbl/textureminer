# [textureminer](https://4mbl.link/gh/textureminer)

> Library and CLI program to extract and scale Minecraft item and block textures.

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Supported Versions](#supported-versions)

## Getting Started

### Prerequisites

To use `textureminer`, you need to have Python installed on your system.

1. Install [Python](https://www.python.org/downloads/), the latest version is generally recommended. See [supported versions](#supported-versions) for more information.
2. Install/update Python's `pip` package manager.

   ```sh
   python3 -m pip install --upgrade pip
   ```

Optionally, if are looking to get Bedrock edition textures, you need to install Git: <https://git-scm.com/install/>

### Installation

Use pip to install the [`textureminer`](https://pypi.org/project/textureminer) package.

```sh
python3 -m pip install --upgrade textureminer
```

After installing the package, `textureminer` will be available as a command line tool.

## Usage

The base syntax for the `textureminer` command is `textureminer [version] [flags]`. If version is omitted, the latest version of Minecraft will be used. If no edition flags are specified, the Java edition will be used.

To download and scale textures for the most recent Java version, run the following command.

```sh
textureminer
```

You can alternatively run `textureminer` through the Python CLI. The following command is equivalent to the above and you can use the the `python3 -m` prefix to run any commands listed below.

```sh
python3 -m textureminer
```

Add `--bedrock` or `-b` to use the Bedrock edition.

```sh
textureminer --bedrock
```

You can also pick a specific update of Minecraft to download textures for.

```sh
textureminer 1.17.1                 # a java stable release
textureminer 22w14a                 # a java snapshot
textureminer v1.20.0.1              # a bedrock release
textureminer v1.20.50.22-preview    # a bedrock preview
```

The `textureminer` command also supports update channels, which are moving targets that always point to the latest version in that channel. This can be useful for automation.

```sh
textureminer stable                 # stable version (defaults to java)
textureminer experimental           # snapshot/preview version (defaults to java)

textureminer snapshot               # java snapshot
textureminer preview                # bedrock preview
```

There is also some options to customize how textureminer works, use the help flag to get more information.

```sh
textureminer --help
```

## Supported Versions

Currently releases of `textureminer` are tested against the following versions of Minecraft.

| Update Name             | Java    | Bedrock     |
| ----------------------- | ------- | ----------- |
| Nether Update           | 1.16    | N/A         |
| Caves & Cliffs: Part I  | 1.17    | N/A         |
| Caves & Cliffs: Part II | 1.18    | N/A         |
| The Wild Update         | 1.19    | N/A         |
| Trails & Tales          | 1.20    | v1.20.0.1   |
| Bats and Pots           | 1.20.3  | v1.20.50.3  |
| Armored Paws            | 1.20.5  | v1.20.80.5  |
| Tricky Trials           | 1.21    | v1.21.0.3   |
| Bundles of Bravery      | 1.21.2  | v1.21.40.3  |
| Garden Awakens          | 1.21.4  | v1.21.50.7  |
| Spring to Life          | 1.21.5  | v1.21.70.3  |
| Chase the Skies         | 1.21.6  | v1.21.90.3  |
| Copper Age              | 1.21.9  | v1.21.110.2 |
| Mounts of Mayhem        | 1.21.11 | v1.21.130.3 |

Other versions are likely to work, but are not tested against every release of `textureminer`. If you find a version that doesn't work, please open an issue on the [GitHub repository](https://github.com/4mbl/textureminer/issues).

Currently Python versions 3.12, 3.13, and 3.14 are supported by `textureminer`.
