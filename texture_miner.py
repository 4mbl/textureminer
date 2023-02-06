from shutil import copytree, rmtree
from zipfile import ZipFile
import os
import re
import tempfile
from forfiles import image, file as f
from colorama import Fore, Back, Style

TEMP_PATH = f"{tempfile.gettempdir()}/texture_miner"
TEMP_PATH = TEMP_PATH.replace("\\", "/")

VERSIONS_PATH = f"{os.path.expanduser('~')}/AppData/Roaming/.minecraft/versions"


def make_temp_dir():
    """Makes a temporary directory for this project if one does not already exist.
    """
    if not os.path.isdir(TEMP_PATH):
        os.mkdir(TEMP_PATH)


def get_latest_stable():
    """Get latest installed Minecraft version

    Args:
        void

    Returns:
        string: latest stable version, for example: "1.18.1"
    """

    versions = [
        f for f in os.listdir(VERSIONS_PATH)
        if os.path.isdir(os.path.join(VERSIONS_PATH, f))
    ]

    stable_versions = []
    for version in versions:
        result = re.findall("[0-9]\.[0-9]+\.?[0-9]+?$", version)
        if result:
            stable_versions.append(result)

    latest_version = max(stable_versions)[0]

    print(f"* Latest installed stable version of Minecraft: {latest_version}")

    return latest_version


def get_latest_snapshot():
    """Get latest installed Minecraft snapshot version number

    Returns:
        string: latest snapshot version, for example "22w11a"
    """

    versions = [
        f for f in os.listdir(VERSIONS_PATH)
        if os.path.isdir(os.path.join(VERSIONS_PATH, f))
    ]

    snapshots = []
    for version in versions:
        result = re.findall("[0-9]{2}w[0-9]{2}[a-z]", version)
        if result:
            snapshots.append(result[0])

    latest_snapshot = sorted(snapshots)[-1]

    print(f"* Latest installed snapshot version of Minecraft: {latest_snapshot}")

    return latest_snapshot


def extract_textures(version: str, path: str = ""):
    """Extracts textures from .jar file located in /.minecraft/ directory

    Args:
        version -- the version that the textures will be extracted from, for example: "1.18.2"
    Returns:
        string: path of the directory the files are extracted to
    """

    if path == "":
        path = f"{TEMP_PATH}/extracted-textures"
        make_temp_dir()

    if os.path.isdir(path):
        rmtree(path)

    if os.path.isdir(f"{TEMP_PATH}/version-files"):
        rmtree(f"{TEMP_PATH}/version-files")

    # %APPDATA%\.minecraft
    copytree(
        f"{os.path.expanduser('~')}/AppData/Roaming/.minecraft/versions/{version}/",
        f"{TEMP_PATH}/version-files",
    )

    jar_path = f"{TEMP_PATH}/version-files/{version}.jar"

    print(f"* {len(ZipFile(jar_path).namelist())} files are being extracted...")

    # extract the .jar file to a different directory
    with ZipFile(f"{TEMP_PATH}/version-files/{version}.jar", "r") as zip_object:
        zip_object.extractall(f"{TEMP_PATH}/extracted-files/")
    rmtree(f"{TEMP_PATH}/version-files/")

    copytree(f"{TEMP_PATH}/extracted-files/assets/minecraft/textures", path)
    rmtree(f"{TEMP_PATH}/extracted-files/")

    return path


def filter_non_icons(input_path: str, output_path: str = ""):
    """Iterates through item and block icons and deletes other files

    Args:
        input_path (string): directory where the input files are
        output_path (string): directory where accepted files will end up

    Returns:
        void
    """

    if output_path == "":
        output_path = f"{os.path.expanduser('~')}/Downloads/mc-textures"
        if os.path.isdir(output_path):
            rmtree(output_path)
    elif not os.path.isdir(output_path):
        os.mkdir(output_path)

    copytree(f"{input_path}/block", f"{output_path}/block")
    copytree(f"{input_path}/item", f"{output_path}/item")
    rmtree(TEMP_PATH)

    return output_path


def scale_icons(path: str, scale_factor: int = 100):
    """Scales images within a directory by a factor

    Args:
        path (string): path of the icons that will be scaled
        scale_factor (int): factor that the icons will be scaled by

    Returns:
        string: path of the scaled icons
    """

    for subdir, _, files in os.walk(path):
        if len(files) != 0:
            print(
                f"* {len(files)} {os.path.basename(subdir)} textures are being resized..."
            )

        for file in files:
            f.filter(f"{os.path.abspath(subdir)}", [".png"])
            image.scale(f"{os.path.abspath(subdir)}/{file}", scale_factor,
                        scale_factor)

    print(f"""{Fore.GREEN}Completed. You can find the textures on:
{os.path.abspath(path)}{Fore.WHITE}.""")

    return path


def merge_dirs(input_dir: str, output_dir: str):
    """Merges block and item textures to a single directory.
    Item textures are given priority when there are conflicts.

    Args:
        input_dir (string): directory in which there are subdirectories 'block' and 'item'
        output_dir (string): directory in which the files will be merged into
    """
    copytree(f"{input_dir}/block", output_dir, dirs_exist_ok=True)
    rmtree(f"{input_dir}/block")
    copytree(f"{input_dir}/item", output_dir, dirs_exist_ok=True)
    rmtree(f"{input_dir}/item")


def get_icons(version, output_dir="", scale_factor=1):
    """Easily extract, filter, and scale item and block icons.

    Args:
        version (string): a Minecraft version number, for example "1.11" or "22w11a"
        output_dir (str, optional): directory that the final icons will go. Defaults to "".
        scale_factor (int, optional): factor that will be used to scale the icons. Defaults to 1.
    """

    if output_dir == "":
        output_dir = f"{os.path.expanduser('~')}/Downloads"

    extracted = extract_textures(version)
    filtered = filter_non_icons(extracted, f"{output_dir}/{version}_textures")
    scaled = scale_icons(filtered, scale_factor)
    merge_dirs(scaled, scaled)


def main():
    """
    Main function

    Args:
        void

    Returns:
        void
    """

    get_icons(get_latest_stable(), scale_factor=100)
    get_icons(get_latest_snapshot())


if __name__ == "__main__":
    main()
