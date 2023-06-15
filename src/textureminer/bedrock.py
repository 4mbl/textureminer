from enum import Enum
import os
import re
from shutil import rmtree
import stat
import subprocess
from colorama import Fore
from textureminer.common import VersionType, filter_unwanted, print_stylized, scale_textures, DEFAULT_OUTPUT_DIR, TEMP_PATH

REPO_URL = 'https://github.com/Mojang/bedrock-samples'


class EditionType(Enum):
    """Enum class representing different editions of Minecraft
    """

    BEDROCK = 'bedrock'
    """Bedrock Edition
    """
    JAVA = 'java'
    """Java Edition
    """


def on_rm_error(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)


def rm_if_exists(path: str):
    if os.path.exists(path):
        rmtree(path, onerror=on_rm_error)


def validate_version(version_type: VersionType, version: str):
    """Validates a version string based on the version type using regex.

    Args:
        version_type (VersionType):
        version (str):

    Returns:
        bool: whether the version is valid
    """

    REGEX_STABLE = r'^v1\.[0-9]{2}\.[0-9]{1,2}\.[0-9]{1,2}$'
    REGEX_PREVIEW = r'^v1\.[0-9]{2}\.[0-9]{1,2}\.[0-9]{1,2}-preview$'

    if version_type == VersionType.EXPERIMENTAL:
        return re.match(REGEX_PREVIEW, version)
    if version_type == VersionType.RELEASE:
        return re.match(REGEX_STABLE, version)


def get_latest_version(version_type: VersionType, repo_dir) -> str:
    """Gets the latest version of a certain type.

    Args:
        version_type (VersionType): type of version to get

    Raises:
        Exception: if the version number is invalid

    Returns:
        str: latest version as a string
    """

    subprocess.run(
        'git fetch --tags',
        check=False,
        cwd=repo_dir,
    )

    out = subprocess.run('git tag --list',
                         check=False,
                         cwd=repo_dir,
                         capture_output=True)

    tags = out.stdout.decode('utf-8').splitlines()

    for tag in reversed(tags):
        if validate_version(version_type, tag):
            return tag


def clone_repo(version_type: VersionType = VersionType.RELEASE) -> str:

    print_stylized("Downloading assets...")

    repo_dir = f'{TEMP_PATH}/bedrock-samples/'

    rm_if_exists(repo_dir)

    clone_command = ['git', 'clone', REPO_URL, repo_dir]

    try:
        subprocess.run(clone_command,
                       check=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        print(
            f"The command failed with return code {err.returncode}: {err.stderr}"
        )

    version = get_latest_version(version_type, repo_dir)

    try:
        subprocess.run(f'git checkout tags/v{version}',
                       check=False,
                       cwd=repo_dir,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        print(
            f"The command failed with return code {err.returncode}: {err.stderr}"
        )
    return (repo_dir, version)


def get_textures(version_type: VersionType = VersionType.RELEASE,
                 output_dir=DEFAULT_OUTPUT_DIR,
                 scale_factor=1,
                 do_merge=True):
    """Easily extract, filter, and scale item and block textures.

    Args:
        version (string): a Minecraft version number, for example "1.11" or "22w11a"
        output_dir (str, optional): directory that the final textures will go. Defaults to "".
        scale_factor (int, optional): factor that will be used to scale the textures. Defaults to 1.

    Returns:
        string: path of the final textures
    """

    print(f'\n{Fore.CYAN}TEXTURE MINER{Fore.RESET}')
    (asset_dir, version) = clone_repo(version_type)
    filtered = filter_unwanted(asset_dir,
                               f'{output_dir}/{version}',
                               edition=EditionType.BEDROCK)
    scale_textures(filtered, scale_factor, do_merge)

    output_dir = os.path.abspath(filtered).replace('\\', '/')
    print(
        f"{Fore.GREEN}Completed. You can find the textures on:\n{output_dir}{Fore.RESET}\n"
    )
    return output_dir


def main():
    get_textures()


if __name__ == '__main__':
    main()
