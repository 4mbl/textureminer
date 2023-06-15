import sys
from textureminer.common import EditionType, VersionType
from textureminer import java, bedrock


def mine(version: str = None,
         edition: EditionType = None,
         scale_factor: int = 100):
    if edition == EditionType.JAVA or edition is None:
        if version is None:
            version = java.get_latest_version(VersionType.RELEASE)
            return
        java.get_textures(VersionType.RELEASE, scale_factor=scale_factor)
    elif edition == EditionType.BEDROCK:
        bedrock.get_textures(version_or_type=version, scale_factor=scale_factor)
    else:
        print('Invalid edition')


def main():
    version = VersionType.RELEASE
    edition = EditionType.JAVA

    args = sys.argv[1:]

    if len(args) > 0 and args[0].lower() in [
            '--help',
            '-h'
            'help',
    ]:
        print(
            '\n\tpy -m textureminer <version> <edition>\n\te.g.\n\tpy -m textureminer 1.17 java\n\tpt -m textureminer 1.17 bedrock\n\tdefaults to java if no edition is specified, and defaults to latest version if no version is specified'
        )
        return

    if len(args) == 0:
        print('defaulting to latest java version')
    elif len(args) == 1:
        version = args[0].lower()
        print('defaulting to java edition')
    elif len(args) <= 2:
        if args[1].lower() == EditionType.JAVA.value:
            edition = EditionType.JAVA
        elif args[1].lower() == EditionType.BEDROCK.value:
            edition = EditionType.BEDROCK
        else:
            print('invalid edition')

    mine(version, edition, scale_factor=100)


main()
