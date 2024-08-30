import logging
import os

import pytest
from fortext import Fg

from textureminer.logger import get_logger

styled_tab = '    * '
styled_tab_colored = '    \033[{color};49m*\033[0m {text}'


def test_no_color_env(caplog):
    os.environ['NO_COLOR'] = '1'
    lgr = get_logger('test_no_color_env')
    lgr.info('Should not be colored')
    os.environ['NO_COLOR'] = '0'

    assert len(caplog.records) == 1
    formatted_msg = caplog.records[0].message
    expected_msg = styled_tab + 'Should not be colored'
    assert formatted_msg == expected_msg


@pytest.mark.parametrize(
    'log_level, expected_color',
    [
        (logging.DEBUG, Fg.BLUE),
        (logging.INFO, Fg.GREEN),
        (logging.WARNING, Fg.YELLOW),
        (logging.ERROR, Fg.RED),
        (logging.CRITICAL, Fg.MAGENTA),
    ],
)
def test_color_formatter(caplog, log_level, expected_color):
    logger = get_logger('test_color_formatter__' + expected_color.name, level=log_level)

    log_message = 'Msg'
    with caplog.at_level(log_level):
        if log_level == logging.DEBUG:
            logger.debug(log_message)
        elif log_level == logging.INFO:
            logger.info(log_message)
        elif log_level == logging.WARNING:
            logger.warning(log_message)
        elif log_level == logging.ERROR:
            logger.error(log_message)
        elif log_level == logging.CRITICAL:
            logger.critical(log_message)

    assert len(caplog.records) == 1
    formatted_msg = caplog.records[0].message
    expected_msg = styled_tab_colored.format(color=expected_color.value, text='Msg')
    assert formatted_msg == expected_msg
