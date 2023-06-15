import os
import re
import subprocess
from textureminer.common import REGEX_BEDROCK_PREVIEW, REGEX_BEDROCK_RELEASE, EditionType, VersionType, filter_unwanted, rm_if_exists, tabbed_print, scale_textures, DEFAULT_OUTPUT_DIR, TEMP_PATH, validate_version
from textureminer import texts

REPO_URL = 'https://github.com/Mojang/bedrock-samples'


def get_version_type(version: str) -> VersionType:
    """Gets the type of a version based on regex.

    Args:
        version (str): version to get the type of

    Returns:
        VersionType: type of version
    """
    if version[0] != 'v':
        version = f'v{version}'
    if re.match(REGEX_BEDROCK_RELEASE, version):
        return VersionType.RELEASE
    if re.match(REGEX_BEDROCK_PREVIEW, version):
        return VersionType.EXPERIMENTAL


def get_latest_version(version_type: VersionType, repo_dir) -> str:
    """Gets the latest version of a certain type.

    Args:
        version_type (VersionType): type of version to get
        repo_dir (str): directory of the repository

    Returns:
        str: latest version as a string
    """

    update_tags(repo_dir)

    out = subprocess.run('git tag --list',
                         check=False,
                         cwd=repo_dir,
                         capture_output=True)

    tags = out.stdout.decode('utf-8').splitlines()

    tag = None

    for tag in reversed(tags):
        if validate_version(tag, version_type, edition=EditionType.BEDROCK):
            break

    tabbed_print(
        texts.VERSION_LATEST_IS.format(version_type=version_type.value,
                                       latest_version="" + tag))
    return tag


def clone_repo() -> str:
    """Clones the mojang/bedrock-samples repository.

    Returns:
        str: path of the repository
    """

    tabbed_print(texts.FILE_DOWNLOADING)

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
            texts.ERROR_COMMAND_FAILED.format(error_code=err.returncode,
                                              error_msg=err.stderr))

    return repo_dir


def update_tags(repo_dir: str):
    """Updates the tags of the repository.

    Args:
        repo_dir (str): directory of the repository
    """
    subprocess.run(
        'git fetch --tags',
        check=False,
        cwd=repo_dir,
    )


def change_repo_version(repo_dir: str, version: str, fetch_tags: bool = True):
    """Changes the version of the repository.

    Args:
        repo_dir (str): directory of the repository
        version (str): version to change to
        fetch_tags (bool, optional): whether to fetch tags from the repository. Defaults to True.

    Raises:
        Exception: if the command fails
    """
    if fetch_tags:
        update_tags(repo_dir)
    try:
        subprocess.run(f'git checkout tags/v{version}',
                       check=False,
                       cwd=repo_dir,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        print(
            texts.ERROR_COMMAND_FAILED.format(error_code=err.returncode,
                                              error_msg=err.stderr))


def get_textures(version_or_type: VersionType | str = VersionType.RELEASE,
                 output_dir=DEFAULT_OUTPUT_DIR,
                 scale_factor=1,
                 do_merge=True) -> str:
    """Easily extract, filter, and scale item and block textures.

    Args:
        version_or_type (string): a Minecraft Bedrock version, for example "v1.20.0.1" or "v1.20.10.21-preview"
        output_dir (str, optional): directory that the final textures will go. Defaults to `DEFAULT_OUTPUT_DIR`.
        scale_factor (int, optional): factor that will be used to scale the textures. Defaults to 1.
        do_merge (bool, optional): whether to merge the block and item textures into a single directory. Defaults to True.

    Returns:
        string: path of the final textures
    """

    if isinstance(version_or_type, str) and not validate_version(
            version_or_type, edition=EditionType.BEDROCK):
        print(texts.VERSION_INVALID.format(version=version_or_type))
        return None

    version_type = version_or_type if isinstance(version_or_type,
                                                 VersionType) else None
    version = None
    asset_dir = clone_repo()
    if isinstance(version_or_type, str):
        version = version_or_type
    else:
        version = get_latest_version(version_type, asset_dir)

    change_repo_version(asset_dir, version)

    filtered = filter_unwanted(asset_dir,
                               f'{output_dir}/bedrock/{version[1:]}',
                               edition=EditionType.BEDROCK)
    scale_textures(filtered, scale_factor, do_merge)

    output_dir = os.path.abspath(filtered).replace('\\', '/')
    print(texts.COMPLETED.format(output_dir=output_dir))
    return output_dir


def main():
    get_textures(VersionType.RELEASE, scale_factor=100)
    get_textures(VersionType.EXPERIMENTAL, scale_factor=100)


if __name__ == '__main__':
    main()
