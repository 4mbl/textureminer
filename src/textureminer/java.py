import os
import re
from shutil import copytree, rmtree
from zipfile import ZipFile
import urllib.request
import requests
from textureminer import texts
from textureminer.common import DEFAULT_OUTPUT_DIR, EditionType, VersionType, filter_unwanted, make_dir, print_stylized, TEMP_PATH, scale_textures

VERSION_MANIFEST = None


def validate_version(version_type: VersionType, version: str):
    """Validates a version string based on the version type using regex.

    Args:
        version_type (VersionType):
        version (str):

    Returns:
        bool: whether the version is valid
    """
    REGEX_SNAPSHOT = r'^[0-9]{2}w[0-9]{2}[a-z]$'
    REGEX_PRE = r'^[0-9]\.[0-9]+\.?[0-9]+-pre[0-9]?$'
    REGEX_RC = r'^[0-9]\.[0-9]+\.?[0-9]+-rc[0-9]?$'
    REGEX_RELEASE = r'^[0-9]\.[0-9]+\.?[0-9]+?$'

    if version_type == VersionType.EXPERIMENTAL:
        return re.match(REGEX_SNAPSHOT, version) or re.match(
            REGEX_PRE, version) or re.match(REGEX_RC, version)
    if version_type == VersionType.RELEASE:
        return re.match(REGEX_RELEASE, version)


def get_version_manifest() -> dict:
    """Fetches the version manifest from Mojang's servers.
    If the manifest has already been fetched, it will return the cached version.

    Returns:
        dict: version manifest
    """
    return requests.get(
        'https://piston-meta.mojang.com/mc/game/version_manifest_v2.json',
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
    print_stylized(texts.VERSION_LATEST_FINDING.format(version_type.value))
    latest_version = get_version_manifest()['latest'][version_type.value]
    if not validate_version(version_type, latest_version):

        raise Exception(texts.VERSION_INVALID.format(latest_version))
    print_stylized(texts.VERSION_LATEST_IS.format(version_type, latest_version))
    return latest_version


def download_client_jar(
    version: str,
    download_dir: str = f'{TEMP_PATH}/version-jars',
) -> str:
    """Downloads the client .jar file for a specific version from Mojang's servers.

    Args:
        version (str): version to download
        download_path (str, optional): directory to download the file to

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

    make_dir(download_dir)
    print_stylized(texts.FILE_DOWNLOADING)
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
        print_stylized(texts.FILES_EXTRACTING.format(file_amount))
        zip_object.extractall(f'{TEMP_PATH}/extracted-files/')
    rmtree(f'{TEMP_PATH}/version-jars/')

    if os.path.isdir(output_path):
        rmtree(output_path)

    copytree(f'{TEMP_PATH}/extracted-files/assets/minecraft/textures',
             output_path)
    rmtree(f'{TEMP_PATH}/extracted-files/')

    return output_path


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

    print(texts.TITLE)
    latest_version = get_latest_version(version_type)
    assets = download_client_jar(latest_version)
    extracted = extract_textures(assets)
    filtered = filter_unwanted(extracted,
                               f'{output_dir}/java/{latest_version}',
                               edition=EditionType.JAVA)
    scale_textures(filtered, scale_factor, do_merge)

    output_dir = os.path.abspath(filtered).replace('\\', '/')
    print(texts.COMPLETED.format(output_dir=output_dir))
    return output_dir


def main():
    get_textures(VersionType.RELEASE, scale_factor=100)
    get_textures(VersionType.EXPERIMENTAL, scale_factor=100)


if __name__ == '__main__':
    main()
