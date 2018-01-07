""" Console and File Logging Functions """
########## STDLIB IMPORTS ##########
import os
import sys
import logging

########## CUSTOM IMPORTS ##########
import config

########## CONSTANTS ##########
LOGFMT = "%(asctime)s - %(funcName)s::%(lineno)d [%(threadName)s]: %(message)s"

########## CUSTOM IMPORTS ##########
def setupLogger():
    """ Configure and Initiate Logging """

    if os.path.exists(config.LOGFILE):
        os.remove(config.LOGFILE)

    logging.basicConfig(filename=config.LOGFILE, level=logging.INFO, format=LOGFMT)

    console = logging.getLogger(name="console")
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOGFMT))
    console.addHandler(console_handler)

def log(msg):
    """ Log to the Console and File"""
    logging.getLogger(name="console").info(msg)
