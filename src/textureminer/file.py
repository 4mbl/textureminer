import os
from shutil import rmtree
import stat


def rm_read_only(_func, path, _exc_info):
    """Removes read-only files on Windows.

    Args:
        _func (function): not used, but required for callback function to work
        path (str): path of the file that will be removed
        _exc_info (object): not used, but required for callback function to work
    """
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)


def rm_if_exists(path: str):
    """Removes a file or directory if it exists.

    Args:
        path (str): path of the file or directory that will be removed
    """
    if os.path.exists(path):
        rmtree(path, onerror=rm_read_only)


def mk_dir(path: str, del_prev: bool = False):
    """Makes a directory if one does not already exist.

    Args:
        path (str): path of the directory that will be created
        del_prev (bool, optional): whether to delete existing directory at the path, defaults to False
    """
    if del_prev and os.path.isdir(path):
        rmtree(path)

    if not os.path.isdir(path):
        os.makedirs(path)
