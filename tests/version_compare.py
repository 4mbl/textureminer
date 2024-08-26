import pytest

from textureminer.edition.Java import Java  # type: ignore


def test_version_comparison_stable_equal() -> None:
    assert Java.is_version_after('1.21', '1.21')
    assert Java.is_version_after('1.21.1', '1.21.1')


def test_version_comparison_stable_different() -> None:
    assert Java.is_version_after('1.21', stable='1.20')
    assert Java.is_version_after('1.21.1', stable='1.21')

    assert not Java.is_version_after('1.20', stable='1.21')
    assert not Java.is_version_after('1.21', stable='1.21.1')

