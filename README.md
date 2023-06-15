# [texture_miner](https://4mbl.link/gh/texture-miner)

`textureminer` is a Python script that allows you to extract and scale Minecraft's item and block textures. It automates the process of downloading the necessary files and performing the required operations.

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

Use pip to install `texture_miner`.

```sh
python3 -m pip install --upgrade textureminer
```

Install the required dependencies as listed on [requirements.txt](./requirements.txt).

```shell
python3 -m pip install -r requirements.txt
```

## Usage

To download and scale textures for the most recent stable Java release do the following.

```python
python3 -m textureminer
```

You can also specify the version and edition.

```python
python3 -m textureminer <version> <edition>

# for example
python3 -m textureminer 1.20 java
```


At a high level, the script follows the following steps.
1. Download the client `.jar` file for the specified version from Mojang's servers.
2. Extract the textures from the `.jar` file.
3. Filter the extracted files, only leaving item and block textures to the specified output directory (default: `~/Downloads/mc-textures`).
4. Scale the textures by a specified factor (default: 100).
5. Merge the block and item textures into a single directory by default.