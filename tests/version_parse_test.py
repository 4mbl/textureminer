import pytest

from textureminer import Java


@pytest.mark.parametrize(
    'snapshot, expected',
    [
        ('24w34a', (24, 34, 0)),
        ('24w34b', (24, 34, 1)),
        ('24w34c', (24, 34, 2)),
        ('22w14a', (22, 14, 0)),
        ('22w14b', (22, 14, 1)),
        ('22w14c', (22, 14, 2)),
    ],
)
def test_parse_snapshot(snapshot: str, expected: tuple) -> None:
    assert Java.parse_snapshot(snapshot) == expected


@pytest.mark.parametrize(
    'pre, expected',
    [
        ('1.21-pre1', (21, 0, 1)),
        ('1.21-pre2', (21, 0, 2)),
        ('1.21.1-pre1', (21, 1, 1)),
        ('1.21.1-pre2', (21, 1, 2)),
    ],
)
def test_parse_pre(pre: str, expected: tuple) -> None:
    assert Java.parse_pre(pre) == expected


@pytest.mark.parametrize(
    'rc, expected',
    [
        ('1.21-rc1', (21, 0, 1)),
        ('1.21-rc2', (21, 0, 2)),
        ('1.21.1-rc1', (21, 1, 1)),
        ('1.21.1-rc2', (21, 1, 2)),
    ],
)
def test_parse_rc(rc: str, expected: tuple) -> None:
    assert Java.parse_rc(rc) == expected


@pytest.mark.parametrize(
    'stable, expected',
    [
        ('1.21', (21, 0)),
        ('1.21.1', (21, 1)),
    ],
)
def test_parse_stable(stable: str, expected: tuple) -> None:
    assert Java.parse_stable(stable) == expected
