"""Types and a base class for Minecraft editions."""  # noqa: N999

import logging
import re
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from shutil import copyfile, copytree, rmtree
from types import TracebackType
from typing import Self
from uuid import uuid4

from forfiles import file as f
from forfiles import image
from PIL import Image as Pil_Image

from textureminer import texts
from textureminer.file import mk_dir, rm_if_exists
from textureminer.options import DEFAULTS, EditionType, TextureOptions, VersionType

REGEX_BEDROCK_RELEASE = r'^v1\.[0-9]{2}\.[0-9]{1,2}\.[0-9]{1,2}$'
REGEX_BEDROCK_PREVIEW = r'^v1\.[0-9]{2}\.[0-9]{1,2}\.[0-9]{1,2}-preview$'

REGEX_JAVA_SNAPSHOT = r'^[0-9]{2}w[0-9]{2}[a-z]$'
REGEX_JAVA_PRE = r'^[0-9]\.[0-9]+\.?[0-9]+-pre[0-9]?$'
REGEX_JAVA_RC = r'^[0-9]\.[0-9]+\.?[0-9]+-rc[0-9]?$'
REGEX_JAVA_RELEASE = r'^[0-9]\.[0-9]+(\.[0-9]+)?$'


class BlockShape(Enum):
    """Enum class representing different block shapes."""

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
    SNOW = 'snow'
    """Only two bottom rows of pixels on the texture
    """
    GLASS_PANE = 'glass_pane'
    """Only the middle column of pixels on the texture
    """


class Edition(ABC):
    """Base class for Minecraft editions."""

    def __init__(self) -> None:
        """Initialize the Edition."""
        self.id = uuid4()
        self.temp_dir = DEFAULTS['TEMP_PATH'] / self.id.__str__()
        self.type = None
        logging.getLogger('textureminer').debug(texts.EDITION_ID.format(id=self.id))
        logging.getLogger('textureminer').debug(texts.TEMP_DIR.format(temp=self.temp_dir))

        if self.temp_dir.is_dir():
            rmtree(self.temp_dir)
        mk_dir(self.temp_dir)

    def __enter__(self) -> Self:
        """Enter the context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the context manager."""
        self.cleanup()

    def cleanup(self) -> None:
        """Clean up temporary files."""
        logging.getLogger('textureminer').debug(texts.CLEARING_TEMP)
        rm_if_exists(self.temp_dir)

    @abstractmethod
    def get_textures(
        self,
        version_or_type: VersionType | str,
        output_dir: Path = DEFAULTS['OUTPUT_DIR'],
        options: TextureOptions | None = None,
    ) -> Path | None:
        """Extract, filter, and scale item and block textures.

        Args:
        ----
            version_or_type (str): a Minecraft version type, or a version string.
            output_dir (Path, optional): directory that the final textures will go
            options (TextureOptions | None, optional): options for the textures

        Returns:
        -------
            Path | None: directory of the final textures or None if invalid input

        """

    @abstractmethod
    def get_version_type(self, version: str) -> VersionType | None:
        """Get the type of a version using regex.

        Args:
        ----
            version (str): version to get the type of

        Returns:
        -------
            VersionType | None: type of version or None if invalid input

        """

    @abstractmethod
    def get_latest_version(self, version_type: VersionType) -> str | None:
        """Get the latest version of a certain type.

        Args:
        ----
            version_type (VersionType): type of version to get

        Returns:
        -------
            str: latest version as a string

        """

    @staticmethod
    def validate_version(  # noqa: C901, PLR0911
        version: str,
        version_type: VersionType | None = None,
        edition: EditionType | None = None,
    ) -> bool:
        """Validate a version string based on the version type using regex.

        Args:
        ----
            version (str): version to validate
            version_type (VersionType | None, optional): type of version to validate
            edition (EditionType | None, optional): type of edition to validate

        Returns:
        -------
            bool: whether the version is valid

        """
        if edition == EditionType.BEDROCK:
            if version[0] != 'v':
                version = f'v{version}'
            if version_type is None:
                return bool(
                    re.match(REGEX_BEDROCK_RELEASE, version)
                    or re.match(REGEX_BEDROCK_PREVIEW, version),
                )
            if version_type == VersionType.STABLE:
                return bool(re.match(REGEX_BEDROCK_RELEASE, version))
            if version_type == VersionType.EXPERIMENTAL:
                return bool(re.match(REGEX_BEDROCK_PREVIEW, version))

        if edition == EditionType.JAVA:
            if version_type is None:
                return bool(
                    re.match(REGEX_JAVA_RELEASE, version)
                    or re.match(REGEX_JAVA_SNAPSHOT, version)
                    or re.match(REGEX_JAVA_PRE, version)
                    or re.match(REGEX_JAVA_RC, version),
                )
            if version_type == VersionType.STABLE:
                return bool(re.match(REGEX_JAVA_RELEASE, version))
            if version_type == VersionType.EXPERIMENTAL:
                return bool(
                    re.match(REGEX_JAVA_SNAPSHOT, version)
                    or re.match(REGEX_JAVA_PRE, version)
                    or re.match(REGEX_JAVA_RC, version),
                )

        is_valid = (
            re.match(REGEX_BEDROCK_PREVIEW, version)
            or re.match(REGEX_BEDROCK_RELEASE, version)
            or re.match(REGEX_JAVA_RELEASE, version)
            or re.match(REGEX_JAVA_SNAPSHOT, version)
            or re.match(REGEX_JAVA_PRE, version)
            or re.match(REGEX_JAVA_RC, version)
        )

        if is_valid:
            return True

        if version[0] != 'v':
            version = f'v{version}'

        return bool(
            re.match(REGEX_BEDROCK_PREVIEW, version)
            or re.match(REGEX_BEDROCK_RELEASE, version)
            or re.match(REGEX_JAVA_RELEASE, version)
            or re.match(REGEX_JAVA_SNAPSHOT, version)
            or re.match(REGEX_JAVA_PRE, version)
            or re.match(REGEX_JAVA_RC, version),
        )

    @staticmethod
    def filter_unwanted(
        input_dir: Path,
        output_dir: Path,
        edition: EditionType = EditionType.JAVA,
    ) -> Path:
        """Remove files that are not item or block textures.

        Args:
        ----
            input_dir (Path): directory where the input files are
            output_dir (Path): directory where accepted files will end up
            edition (EditionType, optional): type of edition

        """
        mk_dir(output_dir, del_prev=True)

        blocks_input = (
            input_dir / 'block'
            if edition.value == EditionType.JAVA.value
            else input_dir / 'resource_pack' / 'textures' / 'blocks'
        )
        items_input = (
            input_dir / 'item'
            if edition.value == EditionType.JAVA.value
            else input_dir / 'resource_pack' / 'textures' / 'items'
        )

        blocks_output = output_dir / 'blocks'
        items_output = output_dir / 'items'

        logging.getLogger('textureminer').debug(
            texts.COPYING_TEXTURES.format(
                input=blocks_input,
                output=blocks_output,
            )
        )
        copytree(blocks_input, blocks_output)

        logging.getLogger('textureminer').debug(
            texts.COPYING_TEXTURES.format(
                input=items_input,
                output=items_output,
            )
        )
        copytree(items_input, items_output)

        logging.getLogger('textureminer').debug(texts.FILTERING_TEXTURES)
        f.filter_type(blocks_output.as_posix(), ['.png'])
        f.filter_type(items_output.as_posix(), ['.png'])

        return output_dir

    @staticmethod
    def crop_texture(
        image_path: Path,
        crop_shape: BlockShape,
        output_path: Path | None = None,
    ) -> None:
        """Crop a texture to a specific shape.

        Args:
        ----
            image_path (Path): path of the texture to crop
            crop_shape (BlockShape): shape to crop the texture to
            output_path (Path, optional): path to save the cropped texture to

        """
        if output_path is None:
            output_path = image_path

        transparent_color = (255, 255, 255, 0)

        match crop_shape:
            case BlockShape.SQUARE:
                Pil_Image.open(image_path).crop((0, 0, 16, 16)).save(output_path)

            case BlockShape.SLAB:
                img = Pil_Image.open(image_path).convert('RGBA')
                img.paste(transparent_color, (0, 0, 16, 8))
                img.save(output_path)

            case BlockShape.STAIR:
                img = Pil_Image.open(image_path).convert('RGBA')
                img.paste(transparent_color, (8, 0, 16, 8))
                img.save(output_path)

            case BlockShape.CARPET:
                img = Pil_Image.open(image_path).convert('RGBA')
                img.paste(transparent_color, (0, 0, 16, 15))
                img.save(output_path)

            case BlockShape.SNOW:
                img = Pil_Image.open(image_path).convert('RGBA')
                img.paste(transparent_color, (0, 0, 16, 14))
                img.save(output_path)

            case BlockShape.GLASS_PANE:
                img = Pil_Image.open(image_path).convert('RGBA')
                img.paste(transparent_color, (0, 0, 7, 16))
                img.paste(transparent_color, (9, 0, 16, 16))
                img.save(output_path)

            case _:
                unknown_block_shape_msg = f'Unknown block shape {crop_shape}'
                raise ValueError(unknown_block_shape_msg)

    @staticmethod
    def replicate_textures(asset_dir: Path, replication_rules: dict[str, str]) -> int:
        """Replicate textures in a directory.

        Args:
        ----
            asset_dir (Path): path to the directory containing the textures
            replication_rules (dict): dictionary containing the replication rules

        Returns:
        -------
            int: number of textures replicated

        """
        logging.getLogger('textureminer').info(texts.TEXTURES_REPLICATING)

        count = 0
        originals = list(replication_rules.keys())
        for subpath in asset_dir.rglob('*'):
            if not subpath.is_file() or subpath.suffix != '.png':
                continue
            file_name = subpath.stem
            if file_name in originals:
                replicated_path = subpath.parent / f'{replication_rules[file_name]}.png'
                copyfile(subpath, replicated_path)
                count += 1

        return count

    @staticmethod
    def scale_textures(
        path: Path,
        scale_factor: int = DEFAULTS['TEXTURE_OPTIONS']['SCALE_FACTOR'],
        *,
        do_merge: bool = DEFAULTS['TEXTURE_OPTIONS']['DO_MERGE'],
        do_crop: bool = DEFAULTS['TEXTURE_OPTIONS']['DO_CROP'],
    ) -> Path:
        """Scales textures within a directory by a factor.

        Args:
        ----
            path (Path): path of the textures that will be scaled
            scale_factor (int, optional): factor that the textures will be scaled by
            do_merge (bool, optional): merge block and item texture files into a single directory
            do_crop (bool, optional): crop non-square textures to be square

        Returns:
        -------
            string: path of the scaled textures

        """
        if do_merge:
            Edition.merge_dirs(path, path)

        logging.getLogger('textureminer').info(texts.TEXTURES_FILTERING)
        for file in path.rglob('*'):
            if not file.is_file():
                continue
            if file.suffix != '.png':
                file.unlink()

            if do_crop:
                Edition.crop_texture(file, BlockShape.SQUARE, file)

            if scale_factor != 1:
                image.scale(file.as_posix(), scale_factor, scale_factor)

        return path

    @staticmethod
    def simplify_structure(_edition_type: EditionType, input_root: Path) -> None:
        """Simplify file structure of textures.

        For example on Bedrock flattens candles to be directly in block and items directories.

        Args:
        ----
            edition_type (EditionType): type of edition
            input_root (Path): directory in which there are subdirectories 'block' and 'item'

        """
        logging.getLogger('textureminer').info(texts.TEXTURES_SIMPLIFYING)
        for texture_subdir in ('blocks', 'items'):
            texture_dir = input_root / texture_subdir
            for subdir in texture_dir.iterdir():
                if not subdir.is_dir():
                    continue
                for file in subdir.iterdir():
                    file.rename(subdir.parent / file.name)
                rmtree(subdir)

    @staticmethod
    def merge_dirs(input_dir: Path, output_dir: Path) -> None:
        """Merge block and item textures to a single directory. Item textures are given priority.

        Args:
        ----
            input_dir (Path): directory in which there are subdirectories for blocks and items
            output_dir (Path): directory in which the files will be merged into

        """
        logging.getLogger('textureminer').info(texts.TEXTURES_MERGING)

        block_folder = input_dir / 'blocks'
        item_folder = input_dir / 'items'

        copytree(block_folder, output_dir, dirs_exist_ok=True)
        rmtree(block_folder)
        copytree(item_folder, output_dir, dirs_exist_ok=True)
        rmtree(item_folder)
