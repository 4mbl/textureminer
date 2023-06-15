import sys
from textureminer.common import EditionType, VersionType, tabbed_print, get_textures
from textureminer import java, bedrock, texts

DEFAULT_VERSION = VersionType.RELEASE
DEFAULT_EDITION = EditionType.JAVA
DEFAULT_SCALE_FACTOR = 100

release = ['stable'
           'release']
experimental = [
    'experimental', 'snapshot', 'pre-release', 'release candidate', 'preview'
]


def cli():
    """CLI entrypoint.

    Returns:
        str: path to the output directory
    """
    args = sys.argv[1:]

    if len(args) > 0 and args[0].lower() in [
            '--help',
            '-h'
            'help',
    ]:
        print(texts.COMMAND_SYNTAX)
        return None

    print(texts.TITLE)

    if len(args) == 0:
        tabbed_print(texts.EDITION_USING_DEFAULT)
        return get_textures(DEFAULT_EDITION,
                            DEFAULT_VERSION,
                            scale_factor=DEFAULT_SCALE_FACTOR)

    version = args[0].lower()

    if version in release:
        version = VersionType.RELEASE
    if version in experimental:
        version = VersionType.EXPERIMENTAL

    if len(args) == 1:
        tabbed_print(texts.EDITION_USING_DEFAULT)
        return get_textures(version,
                            DEFAULT_EDITION,
                            scale_factor=DEFAULT_SCALE_FACTOR)

    edition = args[1].lower()

    if edition == EditionType.JAVA.value.lower() and java.validate_version(
            version):
        return get_textures(version,
                            EditionType.JAVA,
                            scale_factor=DEFAULT_SCALE_FACTOR)
    if edition == EditionType.BEDROCK.value.lower(
    ) and bedrock.validate_version(version):
        return get_textures(version,
                            EditionType.BEDROCK,
                            scale_factor=DEFAULT_SCALE_FACTOR)

    tabbed_print(texts.INVALID_COMBINATION)
    tabbed_print(texts.EDITION_USING_DEFAULT)
    return get_textures(DEFAULT_VERSION, DEFAULT_EDITION)


cli()
