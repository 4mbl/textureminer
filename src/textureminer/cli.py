import sys
from typing import Tuple
from textureminer import texts
from textureminer.edition import Edition, Bedrock, Java
from textureminer.options import DEFAULTS, EditionType, VersionType
from textureminer.texts import tabbed_print


def get_target(
        args: list[str] = sys.argv[1:]
) -> Tuple[EditionType, VersionType | str]:
    """
    Retrieves the target edition and version from the command line arguments.

    Args:
        args (list[str], optional): Command line arguments. Defaults to `sys.argv[1:]`.

    Returns:
        Tuple[EditionType, VersionType | str]: A tuple containing the target edition and version.
    """

    if len(args) == 0:
        tabbed_print(texts.EDITION_USING_DEFAULT)
        return (DEFAULTS['EDITION'], DEFAULTS['VERSION'])

    version_or_type: VersionType | str = args[0].lower()

    release = ['stable'
               'release']
    experimental = [
        'experimental', 'snapshot', 'pre-release', 'release candidate',
        'preview'
    ]

    if version_or_type in release:
        version_or_type = VersionType.RELEASE
    elif version_or_type in experimental:
        version_or_type = VersionType.EXPERIMENTAL

    if len(args) == 1:
        tabbed_print(texts.EDITION_USING_DEFAULT)
        return (DEFAULTS['EDITION'], version_or_type)

    edition = args[1].lower()

    if edition == EditionType.JAVA.value.lower() and Edition.validate_version(
            str(version_or_type)):
        return (EditionType.JAVA, version_or_type)
    if edition == EditionType.BEDROCK.value.lower(
    ) and Edition.validate_version(str(version_or_type)):
        return (EditionType.BEDROCK, version_or_type)

    tabbed_print(texts.INVALID_COMBINATION)

    tabbed_print(texts.EDITION_USING_DEFAULT)
    return (DEFAULTS['EDITION'], DEFAULTS['VERSION'])


def cli(args: list[str] = sys.argv[1:]):
    """
    CLI entrypoint for textureminer.

    Args:
        args (list[str], optional): List of command-line arguments. Defaults to `sys.argv[1:]`.

    Returns:
        None
    """

    if len(args) > 0 and args[0].lower() in [
            '--help',
            '-h'
            'help',
    ]:
        print(texts.COMMAND_SYNTAX)
        return None

    print(texts.TITLE)

    (edition_type, version_or_type) = get_target()

    mc_edition: Edition = Bedrock(
    ) if edition_type == EditionType.BEDROCK else Java()

    mc_edition.get_textures(version_or_type=version_or_type,
                            scale_factor=DEFAULTS['SCALE_FACTOR'])
