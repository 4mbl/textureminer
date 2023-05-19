from shutil import copytree, rmtree
from zipfile import ZipFile
from enum import Enum
import urllib.request
import os
import re
import tempfile
import requests
from forfiles import image, file as f
from colorama import Fore, Back, Style

HOME_DIR = os.path.expanduser('~').replace('\\', '/')
TEMP_PATH = f'{tempfile.gettempdir()}/texture_miner'.replace('\\', '/')
DEFAULT_OUTPUT_DIR = f'{HOME_DIR}/Downloads/mc-textures'
version_manifest = None


class VersionType(Enum):
    SNAPSHOT = 'snapshot'
    RELEASE = 'release'


def make_dir(path: str, do_delete_prev: bool = False):
    """Makes a directory if one does not already exist.

    Args:
        path (str): path of the directory that will be created
    """
    if do_delete_prev and os.path.isdir(path):
        rmtree(path)

    if not os.path.isdir(path):
        os.makedirs(path)


def print_stylized(text):
    print(f"{Fore.CYAN}  * {Fore.RESET}{text}")


def validate_version(version_type: VersionType, version: str):
    REGEX_SNAPSHOT = r'^[0-9]{2}w[0-9]{2}[a-z]$'
    REGEX_PRE = r'^[0-9]\.[0-9]+\.?[0-9]+-pre[0-9]?$'
    REGEX_RC = r'^[0-9]\.[0-9]+\.?[0-9]+-rc[0-9]?$'
    REGEX_RELEASE = r'^[0-9]\.[0-9]+\.?[0-9]+?$'

    if version_type == VersionType.SNAPSHOT:
        return re.match(REGEX_SNAPSHOT, version) or re.match(
            REGEX_PRE, version) or re.match(REGEX_RC, version)
    if version_type == VersionType.RELEASE:
        return re.match(REGEX_RELEASE, version)


def get_version_manifest():
    return requests.get(
        'https://launchermeta.mojang.com/mc/game/version_manifest.json',
        timeout=10).json() if version_manifest is None else version_manifest


def get_latest_version(version_type: VersionType) -> str:
    print_stylized(f"Finding latest {version_type.value}...")
    latest_version = get_version_manifest()['latest'][version_type.value]
    if not validate_version(version_type, latest_version):
        raise Exception(f"Invalid version number ({latest_version}).")
    print_stylized(f"Latest {version_type.value} is {latest_version}.")
    return latest_version


def download_client_jar(
    version: str,
    download_path: str = f'{TEMP_PATH}/version-jars',
):

    for v in get_version_manifest()['versions']:
        if v['id'] == version:
            url = v['url']
            break
        else:
            url = None

    json = requests.get(url, timeout=10).json()
    client_jar_url = json['downloads']['client']['url']

    make_dir(download_path)
    print_stylized("Downloading assets...")
    urllib.request.urlretrieve(client_jar_url, f'{download_path}/{version}.jar')
    return f'{download_path}/{version}.jar'


def extract_textures(input_path: str,
                     output_path: str = f'{TEMP_PATH}/extracted-textures'):
    """Extracts textures from .jar file located in /.minecraft/ directory

    Args:
        version -- the version that the textures will be extracted from, for example: "1.18.2"
    Returns:
        string: path of the directory the files are extracted to
    """

    print_stylized(
        f"{len(ZipFile(input_path).namelist())} files are being extracted...")

    # extract the .jar file to a different directory
    with ZipFile(input_path, 'r') as zip_object:
        zip_object.extractall(f'{TEMP_PATH}/extracted-files/')
    rmtree(f'{TEMP_PATH}/version-jars/')

    if os.path.isdir(output_path):
        rmtree(output_path)

    copytree(f'{TEMP_PATH}/extracted-files/assets/minecraft/textures',
             output_path)
    rmtree(f'{TEMP_PATH}/extracted-files/')

    return output_path


def filter_non_icons(input_path: str, output_dir: str = DEFAULT_OUTPUT_DIR):
    """Iterates through item and block icons and deletes other files

    Args:
        input_path (string): directory where the input files are
        output_path (string): directory where accepted files will end up

    Returns:
        void
    """

    make_dir(output_dir, do_delete_prev=True)

    copytree(f'{input_path}/block', f'{output_dir}/block')
    copytree(f'{input_path}/item', f'{output_dir}/item')
    rmtree(TEMP_PATH)

    return output_dir


def scale_icons(path: str, scale_factor: int = 100, do_merge: bool = True):
    """Scales images within a directory by a factor

    Args:
        path (string): path of the icons that will be scaled
        scale_factor (int): factor that the icons will be scaled by

    Returns:
        string: path of the scaled icons
    """

    if do_merge:
        merge_dirs(path, path)

    for subdir, _, files in os.walk(path):
        if len(files) > 0:
            print_stylized(
                f"{len(files)} textures are being resized..." if do_merge else
                f"{len(files)} {os.path.basename(subdir)} are being resized...")

        for fil in files:
            f.filter(f'{os.path.abspath(subdir)}', ['.png'])
            image.scale(f"{os.path.abspath(subdir)}/{fil}", scale_factor,
                        scale_factor)

    return path


def merge_dirs(input_dir: str, output_dir: str):
    """Merges block and item textures to a single directory.
    Item textures are given priority when there are conflicts.

    Args:
        input_dir (string): directory in which there are subdirectories 'block' and 'item'
        output_dir (string): directory in which the files will be merged into
    """
    print_stylized("Merging block and item textures to a single directory...")
    copytree(f'{input_dir}/block', output_dir, dirs_exist_ok=True)
    rmtree(f'{input_dir}/block')
    copytree(f'{input_dir}/item', output_dir, dirs_exist_ok=True)
    rmtree(f'{input_dir}/item')


def get_icons(version_type: VersionType = VersionType.RELEASE,
              output_dir=DEFAULT_OUTPUT_DIR,
              scale_factor=1,
              do_merge=True):
    """Easily extract, filter, and scale item and block icons.

    Args:
        version (string): a Minecraft version number, for example "1.11" or "22w11a"
        output_dir (str, optional): directory that the final icons will go. Defaults to "".
        scale_factor (int, optional): factor that will be used to scale the icons. Defaults to 1.
    """

    print(f'\n{Fore.CYAN}TEXTURE MINER{Fore.RESET}')
    latest_version = get_latest_version(version_type)
    assets = download_client_jar(latest_version)
    extracted = extract_textures(assets)
    filtered = filter_non_icons(extracted, f'{output_dir}/{latest_version}')
    scale_icons(filtered, scale_factor, do_merge)

    output_dir = os.path.abspath(filtered).replace('\\', '/')
    print(
        f"{Fore.GREEN}Completed. You can find the textures on:\n{output_dir}{Fore.RESET}\n"
    )


def main():
    get_icons(VersionType.SNAPSHOT, scale_factor=100)
    get_icons(VersionType.RELEASE, scale_factor=100)


if __name__ == '__main__':
    main()
