"""Command line interface functionality."""

import argparse
from enum import Enum
from importlib import metadata

from . import texts
from .edition import Bedrock, Edition, Java
from .options import DEFAULTS, EditionType, VersionType
from .texts import tabbed_print


class UpdateOption(Enum):
    """Enum class representing different update options for textureminer."""

    STABLE = 'stable'
    """stable release
    """
    EXPERIMENTAL = 'experimental'
    """snapshot, pre-release, release candidate, or preview
    """
    EXPERIMENTAL_SHORT = 'exp'
    """snapshot, pre-release, release candidate, or preview
    """
    SNAPSHOT = 'snapshot'
    """snapshot
    """
    PREVIEW = 'preview'
    """preview
    """


def get_edition_from_version(version: str) -> EditionType | None:
    """Get the edition from a version.

    Args:
    ----
        version (str): version to get the edition from

    Returns:
    -------
        EditionType: edition of the version

    """
    if Edition.validate_version(version=version, edition=EditionType.JAVA):
        return EditionType.JAVA
    if Edition.validate_version(version=version, edition=EditionType.BEDROCK):
        return EditionType.BEDROCK
    return None


def cli() -> None:
    """CLI entrypoint for textureminer."""
    parser = argparse.ArgumentParser(
        prog='textureminer',
        description='extract and scale minecraft textures',
    )
    parser.add_argument(
        'update',
        default=DEFAULTS['VERSION'],
        nargs='?',
        help='version or type of version to use, e.g. "1.17.1", "stable", or "experimental"',
    )

    edition_group = parser.add_mutually_exclusive_group()
    edition_group.add_argument(
        '-j',
        '--java',
        action='store_true',
        help='use java edition',
    )
    edition_group.add_argument(
        '-b',
        '--bedrock',
        action='store_true',
        help='use bedrock edition',
    )

    parser.add_argument(
        '-o',
        '--output',
        metavar='DIR',
        default=DEFAULTS['OUTPUT_DIR'],
        help='path of output directory',
    )
    parser.add_argument(
        '--crop',
        action='store_true',
        default=DEFAULTS['TEXTURE_OPTIONS']['DO_CROP'],
        help='crop non-square textures to be square',
    )
    parser.add_argument(
        '--flatten',
        action='store_true',
        default=DEFAULTS['TEXTURE_OPTIONS']['DO_MERGE'],
        help='merge block and item textures into a single directory',
    )
    parser.add_argument(
        '--partials',
        action='store_true',
        default=DEFAULTS['TEXTURE_OPTIONS']['DO_PARTIALS'],
        help='create partial textures like stairs and slabs',
    )
    parser.add_argument(
        '--replicate',
        action='store_true',
        default=DEFAULTS['TEXTURE_OPTIONS']['DO_REPLICATE'],
        help='copy and rename only texture variant, for example "glass_pane_top" to "glass_pane"',
    )
    parser.add_argument(
        '--scale',
        default=DEFAULTS['TEXTURE_OPTIONS']['SCALE_FACTOR'],
        type=int,
        help='scale factor for textures',
        metavar='N',
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s ' + metadata.version('textureminer'),
        help='show textureminer version',
    )

    args = parser.parse_args()

    print(texts.TITLE)  # noqa: T201

    edition_type: EditionType | None = None
    update: str | VersionType | None = None

    if args.update == DEFAULTS['VERSION']:
        update = DEFAULTS['VERSION']
    elif args.update == UpdateOption.STABLE.value:
        update = VersionType.STABLE
    elif args.update in (
        UpdateOption.EXPERIMENTAL.value,
        UpdateOption.EXPERIMENTAL_SHORT.value,
    ) or args.update in (UpdateOption.SNAPSHOT.value, UpdateOption.PREVIEW.value):
        update = VersionType.EXPERIMENTAL
    else:
        update = args.update

    if args.bedrock or args.update == UpdateOption.PREVIEW.value:
        edition_type = EditionType.BEDROCK
    elif args.java or args.update == UpdateOption.SNAPSHOT.value:
        edition_type = EditionType.JAVA
    elif args.update and args.update not in VersionType:
        edition_type = get_edition_from_version(args.update)

    if edition_type is None:
        edition_type = DEFAULTS['EDITION']

    tabbed_print(texts.EDITION_USING_X.format(edition=edition_type.value.capitalize()))

    output_path = None
    with Bedrock() if edition_type == EditionType.BEDROCK else Java() as edition:
        try:
            output_path = edition.get_textures(
                version_or_type=update if update else DEFAULTS['VERSION'],
                output_dir=args.output,
                options={
                    'DO_CROP': args.crop,
                    'DO_MERGE': args.flatten,
                    'DO_PARTIALS': args.partials,
                    'DO_REPLICATE': args.replicate,
                    'SCALE_FACTOR': args.scale,
                },
            )

        except Exception:
            edition.cleanup()
            raise

    if output_path:
        print(texts.COMPLETED.format(output_dir=output_path))  # noqa: T201
