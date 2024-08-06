# [textureminer](https://4mbl.link/gh/textureminer)

A Python package that allows you to extract and scale Minecraft's item and block textures automatically.

## Table of Contents

* [Table of Contents](#table-of-contents)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)

## Getting Started

### Prerequisites

**Only Windows is supported at the moment.**

Install Git if you plan on using the Bedrock edition.

You can install Git using your system's package manager, or by downloading the [installer](https://git-scm.com/download/) from the official website.

```sh
winget install Git.Git
```

Install Python 3.11 or higher.

<https://www.python.org/downloads/>

Install/update the [pip](https://pip.pypa.io/en/stable/) package manager.

```sh
python3 -m pip install --upgrade pip
```

It's also recommended to use a [virtual environment](https://docs.python.org/3/library/venv.html).

```bash
python3 -m venv my-venv
my-venv/Scripts/activate
```

### Installation

Use pip to install [`textureminer`](https://pypi.org/project/textureminer) package.

```shell
pip install --upgrade textureminer
```

After installing the package, `textureminer` will be available as a command line tool.

## Usage

The base syntax for `textureminer` is `textureminer [version] [flags]`. If version is omitted, the latest version of Minecraft will be used. If no edition flags are specified, the Java edition will be used.

To download and scale textures for the most recent Java version, run the following command.

```shell
textureminer
```

Add `--bedrock` or `-b` to use the Bedrock edition.

```shell
textureminer --bedrock
```

You can also pick a specific update or update channel of Minecraft to download textures for.

```shell
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

```shell
textureminer --help
```
