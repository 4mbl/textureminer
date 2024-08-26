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


def test_parse_pre() -> None:
    parsed = Java.parse_pre('1.21-pre1')
    assert parsed == (21, 0, 1)
    parsed = Java.parse_pre('1.21-pre2')
    assert parsed == (21, 0, 2)

    parsed = Java.parse_pre('1.21.1-pre1')
    assert parsed == (21, 1, 1)
    parsed = Java.parse_pre('1.21.1-pre2')
    assert parsed == (21, 1, 2)


def test_parse_rc() -> None:
    parsed = Java.parse_rc('1.21-rc1')
    assert parsed == (21, 0, 1)
    parsed = Java.parse_rc('1.21-rc2')
    assert parsed == (21, 0, 2)

    parsed = Java.parse_rc('1.21.1-rc1')
    assert parsed == (21, 1, 1)
    parsed = Java.parse_rc('1.21.1-rc2')
    assert parsed == (21, 1, 2)


def test_parse_stable() -> None:
    parsed = Java.parse_stable('1.21')
    assert parsed == (21, 0)
    parsed = Java.parse_stable('1.21.1')
    assert parsed == (21, 1)
