from enum import Enum
import os
import tempfile
from typing import TypedDict

HOME_DIR = os.path.expanduser('~').replace('\\', '/')


class VersionType(Enum):
    """Enum class representing different types of versions for Minecraft
    """

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
    """Enum class representing different editions of Minecraft
    """

    BEDROCK = 'bedrock'
    """Bedrock Edition
    """
    JAVA = 'java'
    """Java Edition
    """


class TextureOptions(TypedDict):
    """TypedDict class representing the options for textures.
    """

    DO_CROP: bool
    """Whether to crop non-square textures to be square
    """

    DO_MERGE: bool
    """Whether to merge block and item textures into a single directory
    """

    DO_PARTIALS: bool
    """Whether to create partial textures like stairs and slabs
    """

    SCALE_FACTOR: int
    """Factor that will be used to scale the textures
    """


class Options(TypedDict):
    """
    Represents the options for textureminer.

    Attributes:
        EDITION (EditionType): The type of edition to use.
        OUTPUT_DIR (str): The output directory for the textures.
        TEMP_PATH (str): The temporary path for processing.
        TEXTURE_OPTIONS (TextureOptions): Texture manipulation options.
        VERSION (VersionType): The version to use.
    """
    EDITION: EditionType
    OUTPUT_DIR: str
    TEMP_PATH: str
    TEXTURE_OPTIONS: TextureOptions
    VERSION: VersionType


DEFAULTS: Options = {
    'EDITION': EditionType.JAVA,
    'OUTPUT_DIR': os.path.normpath(f'{HOME_DIR}/Downloads/textureminer'),
    'TEMP_PATH': f'{tempfile.gettempdir()}/textureminer'.replace('\\', '/'),
    'VERSION': VersionType.ALL,
    'TEXTURE_OPTIONS': {
        'DO_CROP': True,
        'DO_MERGE': False,
        'DO_PARTIALS': True,
        'SCALE_FACTOR': 100,
    }
}
