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

Install the required dependencies as listed on [requirements.txt](./requirements.txt).

```shell
pip install -r requirements.txt
```

## Usage

To download and scale textures for the most recent Java version, run the following command.

```shell
python3 -m textureminer
```

You can also specify the version and edition of Minecraft with the following syntax: `python3 -m textureminer <version> <edition>`. The version must be a valid Minecraft version, and the edition must be either `java` or `bedrock`. If no edition is specified, the default is `java`.

```shell
python3 -m textureminer 1.20.00 bedrock
```

At a high level, the script follows the following steps:

1. Download files.
   * If Java edition, download the client `.jar` file for the specified version from Mojang's servers.
   * If Bedrock edition, clone the [Mojang/bedrock-samples](https://github.com/Mojang/bedrock-samples) repository from GitHub.
2. Extract correct files.
   1. If Java edition, extract the textures from the `.jar` file.
   2. If Bedrock edition, change to the specified version tag.
3. Filter files, only leaving item and block textures to the specified output directory (default: `~/Downloads/mc-textures/<edition>/<version>/`).
4. Scale textures by a specified factor (default: 100).
5. Merge block and item textures into a single directory by default.
