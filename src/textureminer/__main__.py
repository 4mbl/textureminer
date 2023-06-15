import sys
from textureminer.common import EditionType, VersionType
from textureminer import java, bedrock, texts


def mine(version: str = None,
         edition: EditionType = None,
         scale_factor: int = 100):

    if version is None:
        if edition == EditionType.JAVA or edition is None:
            print(texts.EDITION_USING_X.format(edition=EditionType.JAVA))
            java.get_textures(VersionType.RELEASE, scale_factor=scale_factor)
            return
        if edition == EditionType.BEDROCK:
            print(texts.EDITION_USING_X.format(edition=EditionType.BEDROCK))
            bedrock.get_textures(VersionType.RELEASE, scale_factor=scale_factor)
            return
        print(texts.EDITION_INVALID)

    if version:
        if edition == EditionType.JAVA or edition is None and java.validate_version(
                version):
            print(texts.EDITION_USING_X.format(edition=EditionType.JAVA))
            version_type = java.get_version_type(version)
            print(texts.VERSION_USING_X.format(edition=version_type.value))
            java.get_textures(version_or_type=version,
                              scale_factor=scale_factor)
            return
        if edition == EditionType.BEDROCK and bedrock.validate_version(version):
            print(texts.EDITION_USING_X.format(edition=EditionType.BEDROCK))
            version_type = bedrock.get_version_type(version)
            print(texts.VERSION_USING_X.format(edition=version_type.value))
            bedrock.get_textures(version_or_type=version,
                                 scale_factor=scale_factor)
            return
        print(texts.EDITION_INVALID)
        return


def main():
    version = None
    edition = None

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
    elif len(args) >= 2:
        if args[1].lower() == EditionType.JAVA.value.lower():
            edition = EditionType.JAVA
        elif args[1].lower() == EditionType.BEDROCK.value.lower():
            edition = EditionType.BEDROCK
        else:
            print(texts.EDITION_INVALID)

    mine(version, edition, scale_factor=1)


main()
