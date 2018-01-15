""" Console and File Logging Functions """
########## STDLIB IMPORTS ##########
import os
import sys
import logging

from datetime import datetime

########## CUSTOM IMPORTS ##########
import config

########## FUNCTIONS ##########
class LogFormatter(logging.Formatter):
    """ Custom Log Formatting """
    def format(self, record):
        time = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        header = "{} [{:s}]::{:s}".format(time, record.module, record.funcName)
        return "{:60s} - {}".format(header, record.getMessage())

def setupLogger():
    """ Configure and Initiate Logging """

    if os.path.exists(config.LOGFILE):
        os.remove(config.LOGFILE)


    logging.basicConfig(filename=config.LOGFILE, level=logging.INFO)

    console = logging.getLogger(name="console")
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(LogFormatter())
    console.addHandler(console_handler)

def getConsole():
    """ Get a Console Object for Logging Messages"""
    return logging.getLogger(name="console")
