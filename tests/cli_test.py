import re

import pytest

from textureminer import cli


def test_version(capsys: pytest.CaptureFixture) -> None:
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


def test_help(capsys: pytest.CaptureFixture) -> None:
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
    assert err == ''
    assert out.startswith('usage: textureminer')


def test_bedrock_invalid_version(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli(['--bedrock', '1.99'])
    assert excinfo.value.code != 0
    out, err = capsys.readouterr()
    assert out != ''
    assert err.startswith('Error: Invalid version')


def test_java_invalid_version(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli(['--java', '1.99'])
    assert excinfo.value.code != 0
    out, err = capsys.readouterr()
    assert out != ''
    assert err.startswith('Error: Invalid version')


def test_java_valid_version(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli(['--java', '1.21'])
    assert excinfo.value.code == 0
    out, err = capsys.readouterr()
    assert err.startswith('Error: Invalid version') == False


def test_bedrock_valid_version(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli(['--bedrock', 'v1.20.0.1'])
    assert excinfo.value.code == 0
    out, err = capsys.readouterr()
    assert err.startswith('Error: Invalid version') == False
