import os
import re
from shutil import copytree, rmtree
from zipfile import ZipFile
import urllib.request
import requests
from textureminer import texts
from textureminer.common import DEFAULT_OUTPUT_DIR, DEFAULT_SCALE_FACTOR, REGEX_JAVA_PRE, REGEX_JAVA_RC, REGEX_JAVA_RELEASE, REGEX_JAVA_SNAPSHOT, EditionType, VersionType, filter_unwanted, mk_dir, rm_if_exists, tabbed_print, TEMP_PATH, scale_textures, validate_version

VERSION_MANIFEST = None
VERSION_MANIFEST_URL = 'https://piston-meta.mojang.com/mc/game/version_manifest_v2.json'


def get_version_type(version: str) -> VersionType:
    """Gets the type of a version based on regex.

    Args:
        version (str): version to get the type of

    Returns:
        VersionType: type of version
    """
    if version[0] != 'v':
        version = f'v{version}'
    if re.match(REGEX_JAVA_RELEASE, version):
        return VersionType.RELEASE
    if re.match(REGEX_JAVA_SNAPSHOT, version) or re.match(
            REGEX_JAVA_PRE, version) or re.match(REGEX_JAVA_RC, version):
        return VersionType.EXPERIMENTAL
    return None


def get_version_manifest() -> dict:
    """Fetches the version manifest from Mojang's servers.
    If the manifest has already been fetched, it will return the cached version.

    Returns:
        dict: version manifest
    """
    return requests.get(
        VERSION_MANIFEST_URL,
        timeout=10).json() if VERSION_MANIFEST is None else VERSION_MANIFEST


def get_latest_version(version_type: VersionType) -> str:
    """Gets the latest version of a certain type.

    Args:
        version_type (VersionType): type of version to get

    Raises:
        Exception: if the version number is invalid

    Returns:
        str: latest version as a string
    """
    tabbed_print(
        texts.VERSION_LATEST_FINDING.format(version_type=version_type.value))
    latest_version = get_version_manifest()['latest'][version_type.value]
    if not validate_version(
            latest_version, version_type, edition=EditionType.JAVA):

        raise Exception(
            texts.VERSION_INVALID.format(version="" + latest_version))
    tabbed_print(
        texts.VERSION_LATEST_IS.format(version_type=version_type.value,
                                       latest_version="" + latest_version))
    return latest_version


def download_client_jar(
    version: str,
    download_dir: str = f'{TEMP_PATH}/version-jars',
) -> str:
    """Downloads the client .jar file for a specific version from Mojang's servers.

    Args:
        version (str): version to download
        download_dir (str, optional): directory to download the file to

    Returns:
        str: path of the downloaded file
    """

    for v in get_version_manifest()['versions']:
        if v['id'] == version:
            url = v['url']
            break
        else:
            url = None

    json = requests.get(url, timeout=10).json()
    client_jar_url = json['downloads']['client']['url']

    mk_dir(download_dir)
    tabbed_print(texts.FILE_DOWNLOADING)
    urllib.request.urlretrieve(client_jar_url, f'{download_dir}/{version}.jar')
    return f'{download_dir}/{version}.jar'


def extract_textures(
        input_path: str,
        output_path: str = f'{TEMP_PATH}/extracted-textures') -> str:
    """Extracts textures from .jar file.

    Args:
        input_path (str): path of the .jar file
        output_path (str, optional): path of the output directory

    Returns:
        str: path of the output directory
    """

    with ZipFile(input_path, 'r') as zip_object:
        file_amount = len(zip_object.namelist())
        tabbed_print(texts.FILES_EXTRACTING.format(file_amount=file_amount))
        zip_object.extractall(f'{TEMP_PATH}/extracted-files/')
    rmtree(f'{TEMP_PATH}/version-jars/')

    if os.path.isdir(output_path):
        rmtree(output_path)

    copytree(f'{TEMP_PATH}/extracted-files/assets/minecraft/textures',
             output_path)
    rmtree(f'{TEMP_PATH}/extracted-files/')

    return output_path


def get_textures(version_or_type: VersionType | str = VersionType.RELEASE,
                 output_dir=DEFAULT_OUTPUT_DIR,
                 scale_factor=DEFAULT_SCALE_FACTOR,
                 do_merge=True) -> str:
    """Easily extract, filter, and scale item and block textures.

    Args:
        version_or_type (string): a Minecraft Java version, for example "1.11" or "22w11a"
        output_dir (str, optional): directory that the final textures will go. Defaults to `DEFAULT_OUTPUT_DIR`.
        scale_factor (int, optional): factor that will be used to scale the textures. Defaults to `DEFAULT_SCALE_FACTOR`.
        do_merge (bool, optional): whether to merge the block and item textures into a single directory. Defaults to True.

    Returns:
        string: path of the final textures
    """

    if isinstance(version_or_type, str) and not validate_version(
            version_or_type, edition=EditionType.JAVA):
        print(texts.VERSION_INVALID.format(version=version_or_type))
        return None

    version_type = version_or_type if isinstance(version_or_type,
                                                 VersionType) else None

    version = None
    if isinstance(version_or_type, str):
        version = version_or_type
    else:
        version = get_latest_version(version_type)

    tabbed_print(texts.VERSION_USING_X.format(version=version))
    assets = download_client_jar(version)
    extracted = extract_textures(assets)
    filtered = filter_unwanted(extracted,
                               f'{output_dir}/java/{version}',
                               edition=EditionType.JAVA)
    scale_textures(filtered, scale_factor, do_merge)

    tabbed_print(texts.CLEARING_TEMP)
    rm_if_exists(TEMP_PATH)

    output_dir = os.path.abspath(filtered).replace('\\', '/')
    print(texts.COMPLETED.format(output_dir=output_dir))
    return output_dir


def main():
    get_textures(VersionType.RELEASE, scale_factor=100)
    get_textures(VersionType.EXPERIMENTAL, scale_factor=100)


if __name__ == '__main__':
    main()
