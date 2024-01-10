# [textureminer](https://4mbl.link/gh/textureminer)

A Python script that allows you to extract and scale Minecraft's item and block textures. It automates the process of downloading the necessary files and performing the required operations.

## Table of Contents

* [Table of Contents](#table-of-contents)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)

## Getting Started

### Prerequisites

Install Git if you plan on using the Bedrock edition.

You can install Git using your system's package manager, or by downloading the [installer](https://git-scm.com/download/) from the official website.

* Linux

  ```sh
  sudo apt install git
  ```

* MacOS

  ```sh
    brew install git
    ```

* Windows

    ```sh
    winget install Git.Git
    ```

Install/update the [pip](https://pip.pypa.io/en/stable/) package manager.

  ```sh
  python3 -m pip install --upgrade pip
  ```

It's also recommended to use a [virtual environment](https://docs.python.org/3/library/venv.html).

* Linux / MacOS

    ```bash
    python3 -m venv <venv-name>
    source venv/bin/activate
    ```

* Windows

    ```bash
    python3 -m venv <venv-name>
    <venv-name>/Scripts/activate
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
textureminer --bedrock # or -b
```

You can also pick a specific update or update channel of Minecraft to download textures for.

```shell
textureminer 1.17.1 # a java stable release
textureminer 22w14a # a java snapshot
textureminer v1.20.0.1 # a bedrock release
textureminer v1.20.50.22-preview # a bedrock preview

# update channels, gets latest version from channel, by default using java edition if no edition is specified

textureminer stable # stable version
textureminer experimental # snapshot/preview version depending on edition
textureminer snapshot # java snapshot
textureminer preview # bedrock preview, no need to specify edition

```

There is also options for the scale factor and output directory. Get more information with the `--help` flag.

```shell
textureminer --help
```

At a high level, the script follows the following steps:

1. Download files.
   * If Java edition, download the client `.jar` file for the specified version from Mojang's servers.
   * If Bedrock edition, clone the [Mojang/bedrock-samples](https://github.com/Mojang/bedrock-samples) repository from GitHub.
2. Extract correct files.
   1. If Java edition, extract the textures from the `.jar` file.
   2. If Bedrock edition, change to the specified version tag.
3. Filter files, only leaving item and block textures to the specified output directory (default: `~/Downloads/textureminer/<edition>/<version>/`).
4. Scale textures by a specified factor (default: 100).
5. Merge block and item textures into a single directory by default.
