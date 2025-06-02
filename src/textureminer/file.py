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
    p = Path(path)
    p.chmod(stat.S_IWRITE)
    p.unlink()


def rm_if_exists(path: Path) -> None:
    """Remove a file or directory if it exists.

    Args:
    ----
        path (Path): file or directory that will be removed

    """
    if path.exists():
        rmtree(path, onexc=rm_read_only)


def mk_dir(path: Path, *, del_prev: bool = False) -> bool:
    """Make a directory if one does not already exist.

    Args:
    ----
        path (Path): directory that will be created
        del_prev (bool, optional): whether to delete existing directory at the path

    Returns:
    -------
        bool: True if the directory was created, False if it could not be created

    """
    if del_prev and path.is_dir():
        rmtree(path)
    if not path.is_dir():
        path.mkdir(parents=True)
        return True
    return False
