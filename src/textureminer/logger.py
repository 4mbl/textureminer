"""Logging utilities."""

import logging
import os
from typing import Any, override

from fortext import Fg, style

COLOR_MAP: dict[int, Fg] = {
    logging.DEBUG: Fg.GRAY,
    logging.INFO: Fg.CYAN,
    logging.WARNING: Fg.YELLOW,
    logging.ERROR: Fg.RED,
    logging.CRITICAL: Fg.MAGENTA,
}


class CustomLogger(logging.Logger):
    """Logger supporting NO_COLOR environment variable and tabbed output."""

    @override
    def __init__(self, name: str, level: int = 0) -> None:
        super().__init__(name, level)
        self.color_disabled = os.getenv('NO_COLOR') == '1'

    def _make_tab(self, color: Fg) -> str:
        asterisk = '*' if self.color_disabled else style('*', fg=color)
        return f'{" " * 4}{asterisk} '

    @override
    def log(
        self,
        level: int,
        msg: object,
        *args: object,
        exc_info: Any | None = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Any | None = None,
    ) -> None:
        msg_str = str(msg)
        tab = self._make_tab(COLOR_MAP[level])
        super().log(level, tab + msg_str if '\n' not in msg_str else msg_str, *args)

    @override
    def debug(self, msg: object, *args: object, **kwargs: Any) -> None:
        self.log(logging.DEBUG, msg, *args, **kwargs)

    @override
    def info(self, msg: object, *args: object, **kwargs: Any) -> None:
        self.log(logging.INFO, msg, *args, **kwargs)

    @override
    def warning(self, msg: object, *args: object, **kwargs: Any) -> None:
        self.log(logging.WARNING, msg, *args, **kwargs)

    @override
    def error(self, msg: object, *args: object, **kwargs: Any) -> None:
        self.log(logging.ERROR, msg, *args, **kwargs)

    @override
    def critical(self, msg: object, *args: object, **kwargs: Any) -> None:
        self.log(logging.CRITICAL, msg, *args, **kwargs)


class CustomFormatter(logging.Formatter):
    """Custom formatter for textureminer."""

    @override
    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Any = '%',
        validate: bool = True,
        *,
        level: int | None = None,
        defaults: Any | None = None,
    ) -> None:
        super().__init__(
            fmt=fmt, datefmt=datefmt, style=style, validate=validate, defaults=defaults
        )
        self.level = level

    @override
    def format(self, record: logging.LogRecord) -> str:
        if self.level == logging.DEBUG:
            return f'{record.relativeCreated:07.0f} {record.msg}'
        return record.msg


def get_logger(name: str | None = None, *, level: int = logging.INFO) -> logging.Logger:
    """Get a logger with ColorFormatter.

    Args:
    ----
        name (str | None, optional): Name of the logger. Defaults to None.
        level (int, optional): Logging level. Defaults to logging.INFO.

    Returns:
    -------
        logging.Logger: Logger with ColorFormatter.

    """
    logging.setLoggerClass(CustomLogger)
    logger: logging.Logger = logging.getLogger(name)
    handler: logging.StreamHandler = logging.StreamHandler()
    formatter = CustomFormatter(level=level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger
