# [textureminer](https://4mbl.link/gh/textureminer)

> Library and CLI program to extract and scale Minecraft item and block textures.

## Table of Contents

* [Table of Contents](#table-of-contents)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)

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
textureminer 1.17.1 # a java stable release
textureminer 22w14a # a java snapshot
textureminer v1.20.0.1 # a bedrock release
textureminer v1.20.50.22-preview # a bedrock preview

# update channels, gets latest version from channel
# by default using java edition if no edition is specified

textureminer stable # stable version
textureminer experimental # snapshot/preview version depending on edition
textureminer snapshot # java snapshot
textureminer preview # bedrock preview, no need to specify edition

```

There is also some options to customize how textureminer works, use the help flag to get more information.

```sh
textureminer --help
```
