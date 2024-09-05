import os
import re

import pytest

from textureminer import cli


@pytest.fixture
def disable_color():
    prev = os.getenv('NO_COLOR')
    os.environ['NO_COLOR'] = '1'
    yield
    if prev is not None:
        os.environ['NO_COLOR'] = prev
    else:
        del os.environ['NO_COLOR']


def test_version(capsys: pytest.CaptureFixture, disable_color) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli(['--version'])
    assert excinfo.value.code == 0
    out, err = capsys.readouterr()
    assert re.match(r'textureminer \d+\.\d+\.\d+', out.strip())
    assert err == ''

    with pytest.raises(SystemExit) as excinfo:
        cli(['-v'])
    assert excinfo.value.code == 0
    out, err = capsys.readouterr()
    assert re.match(r'textureminer \d+\.\d+\.\d+', out.strip())
    assert err == ''


def test_help(capsys: pytest.CaptureFixture, disable_color) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli(['--help'])
    assert excinfo.value.code == 0
    out, err = capsys.readouterr()
    assert err == ''
    assert out.startswith('usage: textureminer')

    with pytest.raises(SystemExit) as excinfo:
        cli(['-h'])
    assert excinfo.value.code == 0
    out, err = capsys.readouterr()
    assert out.startswith('usage: textureminer')
    assert err == ''


def test_bedrock_invalid_version(capsys: pytest.CaptureFixture, disable_color) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli(['--bedrock', '1.99'])
    assert excinfo.value.code != 0
    out, err = capsys.readouterr()
    assert 'Invalid version' in err


def test_java_invalid_version(capsys: pytest.CaptureFixture, disable_color) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli(['--java', '1.99'])
    assert excinfo.value.code != 0
    out, err = capsys.readouterr()
    assert 'Invalid version' in err


def test_java_valid_version(capsys: pytest.CaptureFixture, disable_color) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli(['--java', '1.21', '--scale', '1'])
    assert excinfo.value.code == 0
    out, err = capsys.readouterr()
    assert 'Invalid version' not in err


def test_bedrock_valid_version(capsys: pytest.CaptureFixture, disable_color) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli(['--bedrock', 'v1.20.0.1', '--scale', '1'])
    assert excinfo.value.code == 0
    out, err = capsys.readouterr()
    assert 'Invalid version' not in err
