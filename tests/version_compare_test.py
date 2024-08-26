import pytest

from textureminer import Java


@pytest.mark.parametrize(
    'version1, version2, expected',
    [
        ('1.21', '1.21', True),
        ('1.21.1', '1.21.1', True),
        ('1.21', '1.20', True),
        ('1.21.1', '1.21', True),
        ('1.20', '1.21', False),
        ('1.21', '1.21.1', False),
    ],
)
def test_version_comparison(version1: str, version2: str, expected: bool) -> None:
    assert Java.is_version_after(version1, version2) == expected
