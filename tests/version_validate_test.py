import pytest

from textureminer import Edition, EditionType, VersionType


@pytest.mark.parametrize(
    'version, edition, version_type, expected',
    [
        ('v1.21.0.20-preview', EditionType.BEDROCK, None, True),
        ('v1.21.0.3', EditionType.BEDROCK, None, True),
        ('v1.21.0.20-preview', EditionType.BEDROCK, VersionType.EXPERIMENTAL, True),
        ('v1.21.0.3', EditionType.BEDROCK, VersionType.STABLE, True),
    ],
)
def test_validate_bedrock_valid(
    version: str, edition: EditionType, version_type: VersionType, expected: bool
) -> None:
    assert Edition.validate_version(version, edition=edition, version_type=version_type) == expected


@pytest.mark.parametrize(
    'version, edition, version_type, expected',
    [
        ('24w21a', EditionType.JAVA, None, True),
        ('24w21b', EditionType.JAVA, None, True),
        ('1.21.0-pre1', EditionType.JAVA, None, True),
        ('1.21.0-pre2', EditionType.JAVA, None, True),
        ('1.21.0-rc1', EditionType.JAVA, None, True),
        ('1.21.0-rc2', EditionType.JAVA, None, True),
        ('1.21.0', EditionType.JAVA, None, True),
        ('24w21a', EditionType.JAVA, VersionType.EXPERIMENTAL, True),
        ('24w21b', EditionType.JAVA, VersionType.EXPERIMENTAL, True),
        ('1.21.0-pre1', EditionType.JAVA, VersionType.EXPERIMENTAL, True),
        ('1.21.0-pre2', EditionType.JAVA, VersionType.EXPERIMENTAL, True),
        ('1.21.0-rc1', EditionType.JAVA, VersionType.EXPERIMENTAL, True),
        ('1.21.0-rc2', EditionType.JAVA, VersionType.EXPERIMENTAL, True),
        ('1.21.0', EditionType.JAVA, VersionType.STABLE, True),
    ],
)
def test_validate_java_valid(
    version: str, edition: EditionType, version_type: VersionType, expected: bool
) -> None:
    assert Edition.validate_version(version, edition=edition, version_type=version_type) == expected


@pytest.mark.parametrize(
    'version, edition, version_type, expected',
    [
        ('invalid.foo', EditionType.BEDROCK, None, False),
        ('invalid.foo', EditionType.BEDROCK, VersionType.EXPERIMENTAL, False),
        ('invalid.foo', EditionType.BEDROCK, VersionType.STABLE, False),
    ],
)
def test_validate_bedrock_invalid(
    version: str, edition: EditionType, version_type: VersionType, expected: bool
) -> None:
    assert Edition.validate_version(version, edition=edition, version_type=version_type) == expected


@pytest.mark.parametrize(
    'version, edition, version_type, expected',
    [
        ('invalid.foo', EditionType.JAVA, None, False),
        ('invalid.foo', EditionType.JAVA, VersionType.EXPERIMENTAL, False),
        ('invalid.foo', EditionType.JAVA, VersionType.STABLE, False),
    ],
)
def test_validate_java_invalid(
    version: str, edition: EditionType, version_type: VersionType, expected: bool
) -> None:
    assert Edition.validate_version(version, edition=edition, version_type=version_type) == expected
