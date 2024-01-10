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


class Options(TypedDict):
    """
    Represents the options for textureminer.

    Attributes:
        DO_MERGE (bool): Whether to merge the block and item textures into a single directory.
        EDITION (EditionType): The type of edition to use.
        OUTPUT_DIR (str): The output directory for the textures.
        SCALE_FACTOR (int): The scale factor for the textures.
        TEMP_PATH (str): The temporary path for processing.
        VERSION (VersionType): The version to use.
    """
    DO_MERGE: bool
    EDITION: EditionType
    OUTPUT_DIR: str
    SCALE_FACTOR: int
    TEMP_PATH: str
    VERSION: VersionType


DEFAULTS: Options = {
    'DO_MERGE': False,
    'EDITION': EditionType.JAVA,
    'OUTPUT_DIR': os.path.normpath(f'{HOME_DIR}/Downloads/textureminer'),
    'SCALE_FACTOR': 100,
    'TEMP_PATH': f'{tempfile.gettempdir()}/textureminer'.replace('\\', '/'),
    'VERSION': VersionType.ALL,
}
