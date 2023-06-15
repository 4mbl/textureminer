import sys
from textureminer.common import EditionType, VersionType
from textureminer import java, bedrock, texts


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
        print(texts.EDITION_INVALID)


def main():
    version = VersionType.RELEASE
    edition = EditionType.JAVA

    args = sys.argv[1:]

    if len(args) > 0 and args[0].lower() in [
            '--help',
            '-h'
            'help',
    ]:
        print(texts.COMMAND_SYNTAX)
        return

    if len(args) == 0:
        print(texts.EDITION_USING_DEFAULT)
    elif len(args) == 1:
        version = args[0].lower()
        print(texts.EDITION_USING_DEFAULT)
    elif len(args) <= 2:
        if args[1].lower() == EditionType.JAVA.value:
            edition = EditionType.JAVA
        elif args[1].lower() == EditionType.BEDROCK.value:
            edition = EditionType.BEDROCK
        else:
            print(texts.EDITION_INVALID)

    mine(version, edition, scale_factor=1)


main()
