"""Command line interface functionality."""

import argparse
import logging
import os
from enum import Enum
from importlib import metadata
from pathlib import Path

from fortext import Fg, style

from textureminer import texts
from textureminer.edition.Bedrock import Bedrock
from textureminer.edition.Edition import Edition
from textureminer.edition.Java import Java
from textureminer.logger import CustomLogger, get_logger
from textureminer.options import DEFAULTS, EditionType, TextureOptions, VersionType


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


def cli(argv: list[str] | None = None) -> None:  # noqa: C901, PLR0912, PLR0915
    """CLI entrypoint for textureminer.

    Args:
    ----
        argv (list[str] | None, optional): command line arguments, uses sys.argv if None

    """
    try:
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
            type=Path,
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
            help='copy and rename only texture variant, e.g. "glass_pane_top" to "glass_pane"',
        )
        parser.add_argument(
            '--scale',
            default=DEFAULTS['TEXTURE_OPTIONS']['SCALE_FACTOR'],
            type=int,
            help='scale factor for textures',
            metavar='N',
        )
        parser.add_argument(
            '--no-simple-structure',
            action='store_true',
            default=not DEFAULTS['TEXTURE_OPTIONS']['SIMPLIFY_STRUCTURE'],
            help='do not simplify file structure of textures',
        )
        parser.add_argument('--no-color', action='store_true', help='disable color output')
        parser.add_argument('--silent', action='store_true', help='silence output')
        parser.add_argument('--verbose', action='store_true', help='enable verbose output')
        parser.add_argument(
            '-v',
            '--version',
            action='version',
            version='%(prog)s ' + metadata.version('textureminer'),
            help='show textureminer version',
        )

        args = parser.parse_args(argv)

        if args.no_color:
            logging.getLogger('textureminer').debug('Disabling color output')
            os.environ['NO_COLOR'] = '1'

        color_disabled = args.no_color or os.getenv('NO_COLOR') == '1'

        logger: CustomLogger = get_logger(
            'textureminer',
            level=logging.DEBUG if args.verbose else logging.ERROR if args.silent else logging.INFO,
        )  # type: ignore[assignment]

        logger.debug('Arguments: {args}'.format(args=args))  # noqa: G001, UP032

        logger.info(style(texts.TITLE, fg=Fg.CYAN) if not color_disabled else texts.TITLE)

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

        logger.info(texts.EDITION_USING_X.format(edition=edition_type.value.capitalize()))

        texture_options: TextureOptions = {
            'DO_CROP': args.crop,
            'DO_MERGE': args.flatten,
            'DO_PARTIALS': args.partials,
            'DO_REPLICATE': args.replicate,
            'SCALE_FACTOR': args.scale,
            'SIMPLIFY_STRUCTURE': not args.no_simple_structure,
        }

        with Bedrock() if edition_type == EditionType.BEDROCK else Java() as edition:
            logger.debug(
                'Getting textures for {edition} with options: {options}'.format(  # noqa: G001, UP032
                    edition=edition_type.value.capitalize(), options=texture_options
                )
            )
            output_path = edition.get_textures(
                version_or_type=update if update else DEFAULTS['VERSION'],
                output_dir=args.output.resolve(),
                options=texture_options,
            )

    except Exception as e:
        logger.exception(
            f'Error: {e}',  # noqa: G004, TRY401
        )
        raise SystemExit(1, str(e)) from None

    if not color_disabled:
        logger.info(style(texts.COMPLETED, fg=Fg.GREEN))
        if output_path is not None:
            logger.info(style(output_path.as_posix(), fg=Fg.GREEN))
    else:
        logger.info(texts.COMPLETED.format(output_dir=output_path))
        if output_path is not None:
            logger.info(output_path)

    raise SystemExit(0)
