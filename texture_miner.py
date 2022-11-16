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


def get_latest_stable():
    """Get latest installed Minecraft version

    Parameters:
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

    print(f"* Latest installed stable version of Minecraft: {latest_snapshot}")

    return latest_snapshot

def extract_textures(version):
    """Extract textures from .jar file located in /.minecraft/ directory

    Parameters:
        version -- the version that the textures will be extracted from, for example: "1.18.2"
    Returns:
        string: path of the directory the files were extracted
    """

    os.mkdir(TEMP_PATH)
    output_path = f"{TEMP_PATH}/extracted-textures"

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

    copytree(f"{TEMP_PATH}/extracted-files/assets/minecraft/textures",
             output_path)
    rmtree(f"{TEMP_PATH}/extracted-files/")

    return output_path


def get_item_icons(input_dir):
    """
    Iterate through item icons and delete other files

    Parameters:
        input_dir (string): directory where the files are

    Returns:
        void
    """

    output_dir = f"{os.path.expanduser('~')}/Downloads/mc-textures"

    # TODO merge to both to same dir and override blocks with items if conflicts
    # items are copied last as some assets are in both and they look better as items
    copytree(f"{input_dir}/block", f"{output_dir}/block")
    copytree(f"{input_dir}/item", f"{output_dir}/item")
    rmtree(TEMP_PATH)

    for subdir, dirs, files in os.walk(output_dir):

        if len(files) != 0:
            print(
                f"* {len(files)} {os.path.basename(subdir)} textures are being resized..."
            )

        for file in files:
            f.filter(f"{os.path.abspath(subdir)}", [".png"])
            image.scale(f"{os.path.abspath(subdir)}/{file}", 100, 100)

    print(f"""{Fore.GREEN}Completed. You can find the textures on:
{os.path.abspath(output_dir)}{Fore.WHITE}.""")


def main():
    """
    Main function

    Parameters:
        void

    Returns:
        void
    """
    # get_item_icons(extract_textures(get_latest_version()))
    get_item_icons(extract_textures(get_latest_snapshot()))


if __name__ == "__main__":
    main()
