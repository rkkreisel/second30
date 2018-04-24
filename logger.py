""" Console and File Logging Functions """
import os
import sys
import logging

import config

def setup():
    """ Configure the Second30 Logging Module """
    if os.path.exists(config.LOGFILE):
        os.remove(config.LOGFILE)

    handlers = [
        logging.FileHandler(filename=config.LOGFILE),
        logging.StreamHandler(stream=sys.stdout)
    ]

    logging.basicConfig(
        level=logging.INFO,
        format='{asctime} {module:>10s}.{funcName:15s} :: {message}',
        style='{',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        handlers=handlers
    )
