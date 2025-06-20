"""Options for the program."""

import tempfile
from enum import Enum
from pathlib import Path
from typing import TypedDict


class VersionType(Enum):
    """Enum class representing different types of versions for Minecraft."""

    EXPERIMENTAL = 'experimental'
    """snapshot, pre-release, release candidate, or preview
    """
    STABLE = 'stable'
    """stable release
    """
    ALL = 'all'
    """all versions
    """


class EditionType(Enum):
    """Enum class representing different editions of Minecraft."""

    BEDROCK = 'bedrock'
    """Bedrock Edition
    """
    JAVA = 'java'
    """Java Edition
    """


class TextureOptions(TypedDict):
    """TypedDict class representing the options for textures."""

    DO_CROP: bool
    """Whether to crop non-square textures to be square
    """

    DO_MERGE: bool
    """Whether to merge block and item textures into a single directory
    """

    DO_PARTIALS: bool
    """Whether to create partial textures like stairs and slabs
    """

    DO_REPLICATE: bool
    """Whether to copy and rename only texture variant to match the block name.
    For example "glass_pane_top" to "glass_pane".
    """

    SIMPLIFY_STRUCTURE: bool
    """Whether to simplify file structure
    for example on Bedrock flattens candles to be directly in block and items directories.
    """

    SCALE_FACTOR: int
    """Factor that will be used to scale the textures
    """


class Options(TypedDict):
    """Represents the options for textureminer.

    Attributes
    ----------
        EDITION (EditionType): The type of edition to use.
        OUTPUT_DIR (Path): The output directory for the textures.
        TEMP_PATH (Path): The temporary path for processing.
        TEXTURE_OPTIONS (TextureOptions): Texture manipulation options.
        VERSION (VersionType): The version to use.

    """

    EDITION: EditionType
    OUTPUT_DIR: Path
    TEMP_PATH: Path
    TEXTURE_OPTIONS: TextureOptions
    VERSION: VersionType


HOME_DIR = Path().home()

DEFAULTS: Options = {
    'EDITION': EditionType.JAVA,
    'OUTPUT_DIR': (HOME_DIR / 'textureminer'),
    'TEMP_PATH': Path(tempfile.gettempdir()) / 'textureminer',
    'VERSION': VersionType.ALL,
    'TEXTURE_OPTIONS': {
        'DO_CROP': True,
        'DO_MERGE': False,
        'DO_PARTIALS': True,
        'DO_REPLICATE': True,
        'SIMPLIFY_STRUCTURE': True,
        'SCALE_FACTOR': 1,
    },
}

__all__ = ['DEFAULTS', 'EditionType', 'Options', 'TextureOptions', 'VersionType']
