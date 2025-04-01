# [textureminer](https://4mbl.link/gh/textureminer)

> Library and CLI program to extract and scale Minecraft item and block textures.

## Table of Contents

* [Table of Contents](#table-of-contents)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [Supported Versions](#supported-versions)

## Getting Started

### Prerequisites

You need to have Git installed if you plan on using the Bedrock edition.

Git can be installed using your system's package manager, or by downloading the [installer](https://git-scm.com/download/) from the official website.

Install if you plan on using the Bedrock edition.
Either download the [installer](https://git-scm.com/download/) from the official website or use a package manager like [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/#install-winget).

```sh
winget install Git.Git
```

Install Python, the latest version is recommended.

<https://www.python.org/downloads/>

Install/update the [pip](https://pip.pypa.io/en/stable/) package manager.

```sh
python3 -m pip install --upgrade pip
```

### Installation

Use pip to install [`textureminer`](https://pypi.org/project/textureminer) package.

```sh
pip install --upgrade textureminer
```

After installing the package, `textureminer` will be available as a command line tool.

## Usage

The base syntax for `textureminer` is `textureminer [version] [flags]`. If version is omitted, the latest version of Minecraft will be used. If no edition flags are specified, the Java edition will be used.

To download and scale textures for the most recent Java version, run the following command.

```sh
textureminer
```

Add `--bedrock` or `-b` to use the Bedrock edition.

```sh
textureminer --bedrock
```

You can also pick a specific update or update channel of Minecraft to download textures for.

```sh
textureminer 1.17.1                 # a java stable release
textureminer 22w14a                 # a java snapshot
textureminer v1.20.0.1              # a bedrock release
textureminer v1.20.50.22-preview    # a bedrock preview

# update channels, gets latest version from channel
# by default using java edition if no edition is specified

textureminer stable                 # stable version
textureminer experimental           # snapshot/preview version depending on edition
textureminer snapshot               # java snapshot
textureminer preview                # bedrock preview, no need to specify edition

```

There is also some options to customize how textureminer works, use the help flag to get more information.

```sh
textureminer --help
```

## Supported Versions

Currently releases of `textureminer` are tested against the following versions of Minecraft:

| Update Name              | Java        | Bedrock        |
|--------------------------|-------------|----------------|
| Nether Update            | 1.16        | -              |
| Caves & Cliffs: Part I   | 1.17        | -              |
| Caves & Cliffs: Part II  | 1.18        | -              |
| The Wild Update          | 1.19        | -              |
| Trails & Tales           | 1.20        | v1.20.0.1      |
| Bats and Pots            | 1.20.3      | v1.20.50.3     |
| Armored Paws             | 1.20.5      | v1.20.80.5     |
| Tricky Trials            | 1.21        | v1.21.0.3      |
| Bundles of Bravery       | 1.21.2      | v1.21.40.3     |
| Garden Awakens           | 1.21.4      | v1.21.50.7     |
| Spring to Life           | 1.21.5      | v1.21.70.3     |

Other versions are likely to work, but are not tested against every release of `textureminer`. If you find a version that doesn't work, please open an issue on the [GitHub repository](https://github.com/4mbl/textureminer/issues).

Currently Python versions 3.12 and 3.13 are supported by `textureminer`.
