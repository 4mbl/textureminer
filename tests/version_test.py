import pytest

from textureminer.edition.Java import Java  # type: ignore


def test_parse_snapshot() -> None:
    parsed = Java.parse_snapshot('24w34a')
    assert parsed == (24, 34, 0)
    parsed = Java.parse_snapshot('24w34b')
    assert parsed == (24, 34, 1)
    parsed = Java.parse_snapshot('24w34c')
    assert parsed == (24, 34, 2)

    parsed = Java.parse_snapshot('22w14a')
    assert parsed == (22, 14, 0)
    parsed = Java.parse_snapshot('22w14b')
    assert parsed == (22, 14, 1)
    parsed = Java.parse_snapshot('22w14c')
    assert parsed == (22, 14, 2)



def test_parse_stable() -> None:
    parsed = Java.parse_stable('1.21')
    assert parsed == (21, 0)
    parsed = Java.parse_stable('1.21.1')
    assert parsed == (21, 1)


def test_version_comparison_stable_equal() -> None:
    assert Java.is_version_after('1.21', '1.21')
    assert Java.is_version_after('1.21.1', '1.21.1')


def test_version_comparison_stable_different() -> None:
    assert Java.is_version_after('1.21', stable='1.20')
    assert Java.is_version_after('1.21.1', stable='1.21')

    assert not Java.is_version_after('1.20', stable='1.21')
    assert not Java.is_version_after('1.21', stable='1.21.1')

