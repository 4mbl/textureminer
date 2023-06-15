from enum import Enum
import os
import re
from shutil import copytree, rmtree
import stat
import tempfile
from forfiles import image, file as f
from textureminer import texts

HOME_DIR = os.path.expanduser('~').replace('\\', '/')
TEMP_PATH = f'{tempfile.gettempdir()}/texture_miner'.replace('\\', '/')
DEFAULT_OUTPUT_DIR = f'{HOME_DIR}/Downloads/textures'

REGEX_BEDROCK_RELEASE = r'^v1\.[0-9]{2}\.[0-9]{1,2}\.[0-9]{1,2}$'
REGEX_BEDROCK_PREVIEW = r'^v1\.[0-9]{2}\.[0-9]{1,2}\.[0-9]{1,2}-preview$'

REGEX_JAVA_SNAPSHOT = r'^[0-9]{2}w[0-9]{2}[a-z]$'
REGEX_JAVA_PRE = r'^[0-9]\.[0-9]+\.?[0-9]+-pre[0-9]?$'
REGEX_JAVA_RC = r'^[0-9]\.[0-9]+\.?[0-9]+-rc[0-9]?$'
REGEX_JAVA_RELEASE = r'^[0-9]\.[0-9]+\.?[0-9]+?$'


class VersionType(Enum):
    """Enum class representing different types of versions for Minecraft
    """

    EXPERIMENTAL = 'snapshot'
    """snapshot, pre-release, or release candidate
    """
    RELEASE = 'release'
    """stable release
    """


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
    """Removes read-only files on Windows.

    Args:
        func (function): Function that raised the exception
        path (str): Path of the file that couldn't be deleted
        exc_info (exception): Exception info
    """
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)


def rm_if_exists(path: str):
    """Removes a file or directory if it exists.

    Args:
        path (str): path of the file or directory that will be removed
    """
    if os.path.exists(path):
        rmtree(path, onerror=on_rm_error)


def tabbed_print(text):
    """Prints a message to the console with cyan text and a bullet point.
    """
    print(f"{texts.STYLED_TAB}{text}")


def mk_dir(path: str, do_delete_prev: bool = False):
    """Makes a directory if one does not already exist.

    Args:
        path (str): path of the directory that will be created
        do_delete_prev (bool): whether to delete the previous directory if it exists
    """
    if do_delete_prev and os.path.isdir(path):
        rmtree(path)

    if not os.path.isdir(path):
        os.makedirs(path)


def validate_version(version: str,
                     version_type: VersionType = None,
                     edition: EditionType = None) -> bool:
    """Validates a version string based on the version type using regex.

    Args:
        version (str): version string to validate
        version_type (VersionType): type of version, defaults to None, which will validate any version
        edition (EditionType): type of edition, defaults to None, which will validate any version

    Returns:
        bool: whether the version is valid
    """

    if edition == EditionType.BEDROCK:
        if version[0] != 'v':
            version = f'v{version}'
        if version_type is None:
            return re.match(REGEX_BEDROCK_RELEASE, version) or re.match(
                REGEX_BEDROCK_PREVIEW, version)
        if version_type == VersionType.RELEASE:
            return re.match(REGEX_BEDROCK_RELEASE, version)
        if version_type == VersionType.EXPERIMENTAL:
            return re.match(REGEX_BEDROCK_PREVIEW, version)

    elif edition == EditionType.JAVA:
        if version_type is None:
            return re.match(REGEX_JAVA_RELEASE, version) or re.match(
                REGEX_JAVA_SNAPSHOT, version) or re.match(
                    REGEX_JAVA_PRE, version) or re.match(
                        REGEX_JAVA_RC, version)
        if version_type == VersionType.RELEASE:
            return re.match(REGEX_JAVA_RELEASE, version)
        if version_type == VersionType.EXPERIMENTAL:
            return re.match(REGEX_JAVA_SNAPSHOT, version) or re.match(
                REGEX_JAVA_PRE, version) or re.match(REGEX_JAVA_RC, version)

    return re.match(REGEX_BEDROCK_PREVIEW, version) or re.match(
        REGEX_BEDROCK_RELEASE,
        version) or re.match(REGEX_JAVA_RELEASE, version) or re.match(
            REGEX_JAVA_SNAPSHOT, version) or re.match(
                REGEX_JAVA_PRE, version) or re.match(REGEX_JAVA_RC, version)


def filter_unwanted(input_dir: str,
                    output_dir: str,
                    edition: EditionType = EditionType.JAVA) -> str:
    """Removes files that are not item or block textures.

    Args:
        input_path (string): directory where the input files are
        output_path (string): directory where accepted files will end up
        edition (EditionType): type of edition, defaults to `EditionType.JAVA`
    """

    mk_dir(output_dir, do_delete_prev=True)

    blocks_input = f'{input_dir}/block' if edition.value == EditionType.JAVA.value else f'{input_dir}/resource_pack/textures/blocks'
    items_input = f'{input_dir}/item' if edition.value == EditionType.JAVA.value else f'{input_dir}/resource_pack/textures/items'

    blocks_output = f'{output_dir}/blocks'
    items_output = f'{output_dir}/items'

    copytree(blocks_input, blocks_output)
    copytree(items_input, items_output)

    f.filter(blocks_output, ['.png'])
    f.filter(items_output, ['.png'])

    return output_dir


def merge_dirs(input_dir: str, output_dir: str):
    """Merges block and item textures to a single directory.
    Item textures are given priority when there are conflicts.

    Args:
        input_dir (string): directory in which there are subdirectories 'block' and 'item'
        output_dir (string): directory in which the files will be merged into
    """

    block_folder = f'{input_dir}/blocks'
    item_folder = f'{input_dir}/items'

    tabbed_print(texts.TEXTURES_MERGING)
    copytree(block_folder, output_dir, dirs_exist_ok=True)
    rmtree(block_folder)
    copytree(item_folder, output_dir, dirs_exist_ok=True)
    rmtree(item_folder)


def scale_textures(path: str,
                   scale_factor: int = 100,
                   do_merge: bool = True) -> str:
    """Scales textures within a directory by a factor

    Args:
        path (string): path of the textures that will be scaled
        scale_factor (int): factor that the textures will be scaled by
        do_merge (bool): whether to merge block and item texture files into a single directory

    Returns:
        string: path of the scaled textures
    """

    if do_merge:
        merge_dirs(path, path)
    tabbed_print(texts.TEXTURES_FILTERING)
    for subdir, _, files in os.walk(path):
        f.filter(f'{os.path.abspath(subdir)}', ['.png'])

        if scale_factor == 1:
            continue

        if len(files) > 0:
            tabbed_print(
                texts.TEXTURES_RESIZING_AMOUNT.format(texture_amount=len(files))
                if do_merge else texts.TEXTURES_RESISING_AMOUNT_IN_DIR.
                format(len(files), os.path.basename(subdir)))

        for fil in files:
            image.scale(f"{os.path.abspath(subdir)}/{fil}", scale_factor,
                        scale_factor)

    return path
