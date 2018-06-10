""" Console and File Logging Functions """
import os
import sys
import logging

import config

LOGGER_NAME = "SECOND30"
FMT= '{asctime} {module:>10s}.{funcName:15s} :: {message}'
DATE_FMT = '%m/%d/%Y %I:%M:%S %p'

def setup():
    """ Configure the Second30 Logging Module """
    if os.path.exists(config.LOGFILE):
        os.remove(config.LOGFILE)

    handlers = [
        logging.FileHandler(filename=config.LOGFILE),
        logging.StreamHandler(stream=sys.stdout)
    ]

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for handler in handlers:
        handler.setFormatter(logging.Formatter(fmt=FMT, datefmt=DATE_FMT, style='{'))
        logger.addHandler(handler)

def getLogger():
    return logging.getLogger(LOGGER_NAME)