import argparse
import toml
from . import texts
from .edition import Edition, Bedrock, Java
from .options import DEFAULTS, EditionType
from .texts import tabbed_print


def get_edition_from_version(version: str) -> EditionType | None:
    """Gets the edition from a version.

    Args:
        version (str): version to get the edition from

    Returns:
        EditionType: edition of the version
    """

    if Edition.validate_version(version=version, edition=EditionType.JAVA):
        return EditionType.JAVA
    if Edition.validate_version(version=version, edition=EditionType.BEDROCK):
        return EditionType.BEDROCK
    return None


def cli():
    """CLI entrypoint for textureminer.

    Returns:
        None
    """
    parser = argparse.ArgumentParser(
        prog='textureminer', description='extract and scale minecraft textures')
    parser.add_argument(
        'update',
        default=DEFAULTS['VERSION'],
        nargs='?',
        help=
        'version or type of version to use, e.g. "1.17.1", or "experimental"')

    edition_group = parser.add_mutually_exclusive_group()
    edition_group.add_argument('-j',
                               '--java',
                               action='store_true',
                               help='use java edition')
    edition_group.add_argument('-b',
                               '--bedrock',
                               action='store_true',
                               help='use bedrock edition')

    parser.add_argument('-o',
                        '--output',
                        metavar='DIR',
                        default=DEFAULTS['OUTPUT_DIR'],
                        help='path of output directory')
    parser.add_argument(
        '--flatten',
        action='store_true',
        default=DEFAULTS['DO_MERGE'],
        help='merge block and item textures into a single directory')
    parser.add_argument('--scale',
                        default=DEFAULTS['SCALE_FACTOR'],
                        type=int,
                        help='scale factor for textures',
                        metavar='N')
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='%(prog)s ' + read_version_from_pyproject(),
                        help='show textureminer version')

    args = parser.parse_args()

    print(texts.TITLE)

    edition_type: EditionType | None = None

    if args.bedrock:
        edition_type = EditionType.BEDROCK
    elif args.java:
        edition_type = EditionType.JAVA
    elif args.update:
        edition_type = get_edition_from_version(args.update)

    if edition_type is None:
        tabbed_print(texts.EDITION_USING_DEFAULT)
        edition_type = DEFAULTS['EDITION']

    tabbed_print(
        texts.EDITION_USING_X.format(edition=edition_type.value.capitalize()))

    mc_edition: Edition = Bedrock(
    ) if edition_type == EditionType.BEDROCK else Java()

    mc_edition.get_textures(version_or_type=args.update,
                            scale_factor=args.scale)


def read_version_from_pyproject(path: str = 'pyproject.toml'):
    """Reads the version from pyproject.toml.
    """

    with open(path, 'r', encoding='utf-8') as pyproject:
        pyproject_toml = toml.load(pyproject)
        return pyproject_toml['project']['version']
