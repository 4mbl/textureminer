from textureminer import Edition, EditionType, VersionType  # type: ignore


def test_validate_bedrock_valid() -> None:
    assert Edition.validate_version('v1.21.0.20-preview', edition=EditionType.BEDROCK)
    assert Edition.validate_version('v1.21.0.3', edition=EditionType.BEDROCK)

    assert Edition.validate_version(
        'v1.21.0.20-preview',
        edition=EditionType.BEDROCK,
        version_type=VersionType.EXPERIMENTAL,
    )
    assert Edition.validate_version(
        'v1.21.0.3', edition=EditionType.BEDROCK, version_type=VersionType.STABLE
    )


def test_validate_java_valid() -> None:
    assert Edition.validate_version('24w21a', edition=EditionType.JAVA)
    assert Edition.validate_version('24w21b', edition=EditionType.JAVA)
    assert Edition.validate_version('1.21.0-pre1', edition=EditionType.JAVA)
    assert Edition.validate_version('1.21.0-rc1', edition=EditionType.JAVA)
    assert Edition.validate_version('1.21.0', edition=EditionType.JAVA)

    assert Edition.validate_version(
        '24w21a', edition=EditionType.JAVA, version_type=VersionType.EXPERIMENTAL
    )
    assert Edition.validate_version(
        '24w21b', edition=EditionType.JAVA, version_type=VersionType.EXPERIMENTAL
    )
    assert Edition.validate_version(
        '1.21.0-pre1', edition=EditionType.JAVA, version_type=VersionType.EXPERIMENTAL
    )
    assert Edition.validate_version(
        '1.21.0-rc1', edition=EditionType.JAVA, version_type=VersionType.EXPERIMENTAL
    )
    assert Edition.validate_version(
        '1.21.0', edition=EditionType.JAVA, version_type=VersionType.STABLE
    )


def test_validate_bedrock_invalid() -> None:
    assert Edition.validate_version('invalid.foo', edition=EditionType.BEDROCK) is False


def test_validate_java_invalid() -> None:
    assert Edition.validate_version('invalid.foo', edition=EditionType.JAVA) is False
