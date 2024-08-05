from abc import ABC, abstractmethod
from enum import Enum
import os
import re
from shutil import copytree, rmtree
from PIL import Image as pil_image  # type: ignore
from forfiles import image, file as f  # type: ignore

from .. import texts
from ..file import mk_dir
from ..options import DEFAULTS, EditionType, TextureOptions, VersionType
from ..texts import tabbed_print

REGEX_BEDROCK_RELEASE = r'^v1\.[0-9]{2}\.[0-9]{1,2}\.[0-9]{1,2}$'
REGEX_BEDROCK_PREVIEW = r'^v1\.[0-9]{2}\.[0-9]{1,2}\.[0-9]{1,2}-preview$'

REGEX_JAVA_SNAPSHOT = r'^[0-9]{2}w[0-9]{2}[a-z]$'
REGEX_JAVA_PRE = r'^[0-9]\.[0-9]+\.?[0-9]+-pre[0-9]?$'
REGEX_JAVA_RC = r'^[0-9]\.[0-9]+\.?[0-9]+-rc[0-9]?$'
REGEX_JAVA_RELEASE = r'^[0-9]\.[0-9]+\.?[0-9]+?$'


class BlockShape(Enum):
    """Enum class representing different block shapes
    """

    SQUARE = 'square'
    """Square texture
    """
    SLAB = 'slab'
    """Bottom half of the texture
    """
    STAIR = 'stair'
    """All corners of the texture except the top right corner
    """
    CARPET = 'carpet'
    """Only the bottom row of pixels on the texture
    """


class Edition(ABC):

    @abstractmethod
    def get_textures(self,
                     version_or_type: VersionType | str,
                     output_dir: str = DEFAULTS['OUTPUT_DIR'],
                     options: TextureOptions | None = None):
        """Extract, filter, and scale item and block textures.

        Args:
            version_or_type (str): a Minecraft version type, or a version string.
            output_dir (str, optional): directory that the final textures will go.
            scale_factor (int, optional): factor that will be used to scale the textures.
            do_merge (bool, optional): whether to merge the block and item textures into a single directory.

        Returns:
            string | None: path of the final textures or None if invalid input
        """

    @abstractmethod
    def get_version_type(self, version: str) -> VersionType | None:
        """Gets the type of a version using regex.

        Args:
            version (str): version to get the type of

        Returns:
            VersionType | None: type of version or None if invalid input
        """

    @abstractmethod
    def get_latest_version(self, version_type: VersionType) -> str:
        """Gets the latest version of a certain type.

        Args:
            version_type (VersionType): type of version to get

        Raises:
            Exception: if the version number is invalid

        Returns:
            str: latest version as a string
        """

    @staticmethod
    def validate_version(version: str,
                         version_type: VersionType | None = None,
                         edition: EditionType | None = None) -> bool:
        """Validates a version string based on the version type using regex.

        Args:
            version (str): version to validate
            version_type (VersionType | None, optional): type of version, defaults to None, which will validate any version
            edition (EditionType | None, optional): type of edition, defaults to None, which will validate any version

        Returns:
            bool: whether the version is valid
        """

        if edition == EditionType.BEDROCK:
            if version[0] != 'v':
                version = f'v{version}'
            if version_type is None:
                return bool(
                    re.match(REGEX_BEDROCK_RELEASE, version) or
                    re.match(REGEX_BEDROCK_PREVIEW, version))
            if version_type == VersionType.STABLE:
                return bool(re.match(REGEX_BEDROCK_RELEASE, version))
            if version_type == VersionType.EXPERIMENTAL:
                return bool(re.match(REGEX_BEDROCK_PREVIEW, version))

        if edition == EditionType.JAVA:
            if version_type is None:
                return bool(
                    re.match(REGEX_JAVA_RELEASE, version) or
                    re.match(REGEX_JAVA_SNAPSHOT, version) or
                    re.match(REGEX_JAVA_PRE, version) or
                    re.match(REGEX_JAVA_RC, version))
            if version_type == VersionType.STABLE:
                return bool(re.match(REGEX_JAVA_RELEASE, version))
            if version_type == VersionType.EXPERIMENTAL:
                return bool(
                    re.match(REGEX_JAVA_SNAPSHOT, version) or
                    re.match(REGEX_JAVA_PRE, version) or
                    re.match(REGEX_JAVA_RC, version))

        is_valid = re.match(REGEX_BEDROCK_PREVIEW, version) or re.match(
            REGEX_BEDROCK_RELEASE, version) or re.match(
                REGEX_JAVA_RELEASE, version) or re.match(
                    REGEX_JAVA_SNAPSHOT, version) or re.match(
                        REGEX_JAVA_PRE, version) or re.match(
                            REGEX_JAVA_RC, version)

        if is_valid:
            return True

        if version[0] != 'v':
            version = f'v{version}'

        return bool(
            re.match(REGEX_BEDROCK_PREVIEW, version) or
            re.match(REGEX_BEDROCK_RELEASE, version) or
            re.match(REGEX_JAVA_RELEASE, version) or
            re.match(REGEX_JAVA_SNAPSHOT, version) or
            re.match(REGEX_JAVA_PRE, version) or
            re.match(REGEX_JAVA_RC, version))

    @staticmethod
    def merge_dirs(input_dir: str, output_dir: str):
        """Merges block and item textures to a single directory.
        Item textures are given priority when there are conflicts.

        Args:
            input_dir (str): directory in which there are subdirectories 'block' and 'item'
            output_dir (str): directory in which the files will be merged into
        """

        block_folder = f'{input_dir}/blocks'
        item_folder = f'{input_dir}/items'

        tabbed_print(texts.TEXTURES_MERGING)
        copytree(block_folder, output_dir, dirs_exist_ok=True)
        rmtree(block_folder)
        copytree(item_folder, output_dir, dirs_exist_ok=True)
        rmtree(item_folder)

    @staticmethod
    def filter_unwanted(input_dir: str,
                        output_dir: str,
                        edition: EditionType = EditionType.JAVA) -> str:
        """Removes files that are not item or block textures.

        Args:
            input_path (str): directory where the input files are
            output_path (str): directory where accepted files will end up
            edition (EditionType, optional): type of edition, defaults to `EditionType.JAVA`
        """

        mk_dir(output_dir, del_prev=True)

        blocks_input = f'{input_dir}/block' if edition.value == EditionType.JAVA.value else f'{input_dir}/resource_pack/textures/blocks'
        items_input = f'{input_dir}/item' if edition.value == EditionType.JAVA.value else f'{input_dir}/resource_pack/textures/items'

        blocks_output = f'{output_dir}/blocks'
        items_output = f'{output_dir}/items'

        copytree(blocks_input, blocks_output)
        copytree(items_input, items_output)

        f.filter(blocks_output, ['.png'])
        f.filter(items_output, ['.png'])

        return output_dir

    @staticmethod
    def crop_texture(image_path: str,
                     crop_shape: BlockShape,
                     output_path: str | None = None):
        """Crops a texture to a specific shape.

        Args:
            image_path (str): path of the texture to crop
            crop_shape (BlockShape): shape to crop the texture to
            output_path (str, optional): path to save the cropped texture to. Defaults to `image_path`.
        """

        if output_path is None:
            output_path = image_path

        transparent_color = (255, 255, 255, 0)

        match crop_shape:
            case BlockShape.SQUARE:
                if pil_image.open(image_path).size != (16, 16):
                    pil_image.open(image_path).crop(
                        (0, 0, 16, 16)).save(output_path)

            case BlockShape.SLAB:
                pil_image.open(image_path).crop(
                    (0, 8, 16, 16)).save(output_path)

            case BlockShape.STAIR:
                img = pil_image.open(image_path).convert("RGBA")
                img.paste(transparent_color, (8, 0, 16, 8))
                img.save(output_path)

            case BlockShape.CARPET:
                img = pil_image.open(image_path).convert("RGBA")
                img.paste(transparent_color, (0, 0, 16, 15))
                img.save(output_path)

            case _:
                raise ValueError(f'Unknown block shape {crop_shape}')

    @staticmethod
    def scale_textures(
            path: str,
            scale_factor: int = DEFAULTS['TEXTURE_OPTIONS']['SCALE_FACTOR'],
            do_merge: bool = DEFAULTS['TEXTURE_OPTIONS']['DO_MERGE'],
            do_crop: bool = DEFAULTS['TEXTURE_OPTIONS']['DO_CROP']) -> str:
        """Scales textures within a directory by a factor

        Args:
            path (str): path of the textures that will be scaled
            scale_factor (int, optional): factor that the textures will be scaled by
            do_merge (bool, optional): whether to merge block and item texture files into a single directory
            do_crop (bool, optional): whether to crop non-square textures to be square

        Returns:
            string: path of the scaled textures
        """

        if do_merge:
            Edition.merge_dirs(path, path)
        tabbed_print(texts.TEXTURES_FILTERING)
        for subdir, _, files in os.walk(path):
            f.filter(f'{os.path.abspath(subdir)}', ['.png'])

            if scale_factor != 1 and len(files) > 0:
                if do_merge:
                    tabbed_print(
                        texts.TEXTURES_RESIZING_AMOUNT.format(
                            texture_amount=len(files)))
                else:
                    tabbed_print(
                        texts.TEXTURES_RESISING_AMOUNT_IN_DIR.format(
                            texture_amount=len(files),
                            dir_name=os.path.basename(subdir)))

            for fil in files:
                image_path = os.path.normpath(
                    f"{os.path.abspath(subdir)}/{fil}")
                if do_crop:
                    Edition.crop_texture(image_path, BlockShape.SQUARE,
                                         image_path)

                if scale_factor != 1:
                    image.scale(image_path, scale_factor, scale_factor)

        return path
