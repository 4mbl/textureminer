"""File utilities."""

import stat
from collections.abc import Callable
from pathlib import Path
from shutil import rmtree


def rm_read_only(_func: Callable, path: str, _exc_info: object) -> None:
    """Remove read-only files on Windows.

    Args:
    ----
        _func (function): not used, but required for callback function to work
        path (str): path of the file that will be removed
        _exc_info (object): not used, but required for callback function to work

    """
    Path(path).chmod(stat.S_IWRITE)
    Path(path).unlink()


def rm_if_exists(path: str) -> None:
    """Remove a file or directory if it exists.

    Args:
    ----
        path (str): path of the file or directory that will be removed

    """
    if Path(path).exists():
        rmtree(path, onexc=rm_read_only)


def mk_dir(path: str, *, del_prev: bool = False) -> bool:
    """Make a directory if one does not already exist.

    Args:
    ----
        path (str): path of the directory that will be created
        del_prev (bool, optional): whether to delete existing directory at the path

    Returns:
    -------
        bool: True if the directory was created, False if it could not be created

    """
    if del_prev and Path(path).is_dir():
        rmtree(path)
    if not Path(path).is_dir():
        Path(path).mkdir(parents=True)
        return True
    return False
