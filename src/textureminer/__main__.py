import sys
from textureminer.common import EditionType, VersionType, tabbed_print
from textureminer import java, bedrock, texts

DEFAULT_VERSION = VersionType.RELEASE
DEFAULT_EDITION = EditionType.JAVA
DEFAULT_SCALE_FACTOR = 100


def get_textures(
    *args,
    edition: EditionType = EditionType.JAVA,
    version_or_type: VersionType | str = VersionType.RELEASE,
    scale_factor: int = 1,
    **kwargs,
) -> str:
    """Easily extract, filter, and scale item and block textures.

    Args:
        *args: arguments that will be passed to the get_textures function of the specified edition
        edition (EditionType): type of edition, defaults to `EditionType.JAVA`
        version_or_type (string): a Minecraft Java version, for example "1.11" or "22w11a"
        scale_factor (int): factor that will be used to scale the textures
        **kwargs: keyword arguments that will be passed to the get_textures function of the specified edition

    Returns:
        string: path of the final textures
    """

    if edition == EditionType.JAVA:
        return java.get_textures(*args,
                                 version_or_type=version_or_type,
                                 scale_factor=scale_factor,
                                 **kwargs)

    if edition == EditionType.BEDROCK:
        return bedrock.get_textures(*args,
                                    version_or_type=version_or_type,
                                    scale_factor=scale_factor,
                                    **kwargs)
    return None


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

    release = ['stable'
               'release']
    experimental = [
        'experimental', 'snapshot', 'pre-release', 'release candidate',
        'preview'
    ]

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
