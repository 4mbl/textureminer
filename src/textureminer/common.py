from enum import Enum
import os
from shutil import copytree, rmtree
import tempfile
from colorama import Fore
from forfiles import image, file as f

HOME_DIR = os.path.expanduser('~').replace('\\', '/')
TEMP_PATH = f'{tempfile.gettempdir()}/texture_miner'.replace('\\', '/')
DEFAULT_OUTPUT_DIR = f'{HOME_DIR}/Downloads/mc-textures'


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


def print_stylized(text):
    """Prints a message to the console with cyan text and a bullet point.
    """
    print(f"{Fore.CYAN}{' '*4}* {Fore.RESET}{text}")


def make_dir(path: str, do_delete_prev: bool = False):
    """Makes a directory if one does not already exist.

    Args:
        path (str): path of the directory that will be created
    """
    if do_delete_prev and os.path.isdir(path):
        rmtree(path)

    if not os.path.isdir(path):
        os.makedirs(path)


def filter_unwanted(input_dir: str,
                    output_dir: str,
                    edition: EditionType = EditionType.JAVA) -> str:
    """Removes files that are not item or block textures.

    Args:
        input_path (string): directory where the input files are
        output_path (string): directory where accepted files will end up

    Returns:
        void
    """

    make_dir(output_dir, do_delete_prev=True)

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

    print_stylized("Merging block and item textures to a single directory...")
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

    for subdir, _, files in os.walk(path):
        print_stylized(
            "Textures are being filtered..." if do_merge else
            f"{os.path.basename(subdir).capitalize()} textures are being filtered..."
        )
        f.filter(f'{os.path.abspath(subdir)}', ['.png'])

        if scale_factor == 1:
            continue

        if len(files) > 0:
            print_stylized(
                f"{len(files)} textures are being resized..." if do_merge else
                f"{len(files)} {os.path.basename(subdir)} textures are being resized..."
            )

        for fil in files:
            image.scale(f"{os.path.abspath(subdir)}/{fil}", scale_factor,
                        scale_factor)

    return path
